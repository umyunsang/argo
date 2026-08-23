import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import type { AgentMessage } from "@earendil-works/pi-agent-core";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { DaemonWorkerFrameHeader } from "../src/modes/daemon/daemon-worker-protocol.js";
import { DaemonSupervisor } from "../src/modes/daemon/daemon-supervisor.js";
import { SnapshotTranscriptCache } from "../src/modes/daemon/snapshot-transcript-cache.js";
import type { PrivateFrame } from "../src/modes/session-worker/private-framing.js";

const tempDirs: string[] = [];

afterEach(() => {
	for (const directory of tempDirs.splice(0)) {
		rmSync(directory, { recursive: true, force: true });
	}
});

function tempDir(): string {
	const directory = mkdtempSync(join(tmpdir(), "snapshot-containment-test-"));
	tempDirs.push(directory);
	return directory;
}

const ACTIVE = "active-a";
const SNAPSHOT_ID = "snap-1";
const CURSOR = { generation: "gen-1", sequence: 42 };

function messages(count: number): AgentMessage[] {
	return Array.from({ length: count }, (_, index) => ({
		role: "user" as const,
		content: `${index}:${"x".repeat(60)}`,
		timestamp: index,
	}));
}

function beginPayload(messageCount: number): Buffer {
	return Buffer.from(
		JSON.stringify({
			type: "session_snapshot_begin",
			activeSessionId: ACTIVE,
			snapshotId: SNAPSHOT_ID,
			messageCount,
			targetChunkBytes: 200,
			snapshot: {
				activeSessionId: ACTIVE,
				summary: { id: ACTIVE, sessionId: "session-a", activeSessionId: ACTIVE, cwd: "/tmp/project" },
				state: {},
				messages: [],
				lastEventSequence: CURSOR.sequence,
				lastEventCursor: CURSOR,
			},
		}),
	);
}

function chunkPayload(content: string): Buffer {
	return Buffer.from(
		JSON.stringify({
			type: "session_snapshot_chunk",
			activeSessionId: ACTIVE,
			snapshotId: SNAPSHOT_ID,
			index: 0,
			messages: [{ role: "user", content, timestamp: 0 }],
		}),
	);
}

function endPayload(chunkCount: number): Buffer {
	return Buffer.from(
		JSON.stringify({
			type: "session_snapshot_end",
			activeSessionId: ACTIVE,
			snapshotId: SNAPSHOT_ID,
			chunkCount,
		}),
	);
}

interface Harness {
	supervisor: DaemonSupervisor;
	worker: {
		descriptor: Record<string, unknown>;
		client: { close: ReturnType<typeof vi.fn> };
		transcriptCaches: Map<string, SnapshotTranscriptCache>;
		snapshotCache: Map<string, unknown>;
		snapshotGenerations: Map<string, Map<string, unknown>>;
	};
	closeWorker: ReturnType<typeof vi.fn>;
	handleWorkerClose: ReturnType<typeof vi.fn>;
	generations: Map<string, unknown>;
}

// Constructor-bypass harness coupled to the fields handleWorkerFrame touches on
// the snapshot transfer paths.
function createHarness(): Harness {
	const closeWorker = vi.fn();
	const worker = {
		descriptor: { workerId: "worker-1", pid: 1234, lifecycle: "ready", rootActiveSessionId: ACTIVE },
		client: { close: closeWorker },
		snapshotCache: new Map<string, unknown>(),
		transcriptCaches: new Map<string, SnapshotTranscriptCache>(),
		snapshotGenerations: new Map<string, Map<string, unknown>>(),
	};
	const generations = new Map<string, unknown>();
	worker.snapshotGenerations.set(ACTIVE, generations);
	const supervisor = Object.assign(Object.create(DaemonSupervisor.prototype), {
		log: vi.fn(),
		publicSummary: vi.fn((_worker: unknown, summary: unknown) => summary),
		handleWorkerClose: vi.fn(),
	}) as DaemonSupervisor;
	return { supervisor, worker, closeWorker, handleWorkerClose: supervisor.handleWorkerClose as ReturnType<typeof vi.fn>, generations };
}

function seedCompleteGeneration(harness: Harness, messageCount: number) {
	const transcript = new SnapshotTranscriptCache({
		activeSessionId: ACTIVE,
		snapshotId: SNAPSHOT_ID,
		messages: messages(messageCount),
		cacheRoot: tempDir(),
		targetChunkBytes: 200,
	});
	transcript.markComplete();
	const result = {
		activeSessionId: ACTIVE,
		lastEventSequence: CURSOR.sequence,
		lastEventCursor: CURSOR,
		snapshot: { lastEventSequence: CURSOR.sequence, lastEventCursor: CURSOR },
		snapshotStream: { id: SNAPSHOT_ID, messageCount, targetChunkBytes: 200 },
	};
	harness.generations.set(SNAPSHOT_ID, {
		transcript,
		result,
		incoming: false,
		retired: false,
		end: Buffer.from(JSON.stringify({ chunkCount: transcript.chunkCount })),
	});
	harness.worker.transcriptCaches.set(ACTIVE, transcript);
	harness.worker.snapshotCache.set(ACTIVE, result);
	return { transcript };
}

function frame(header: Record<string, unknown>, payload?: Buffer): PrivateFrame<DaemonWorkerFrameHeader> {
	return { header: header as DaemonWorkerFrameHeader, payload: payload ?? Buffer.alloc(0) };
}

describe("duplicate snapshot mismatch containment", () => {
	it("invalidates a mismatching duplicate chunk without closing the worker channel", () => {
		const harness = createHarness();
		const { transcript } = seedCompleteGeneration(harness, 5);

		// Re-stream the cached snapshot; this enters duplicate-validation mode.
		harness.supervisor.handleWorkerFrame(
			harness.worker,
			frame(
				{ kind: "outbound", outboundType: "session_snapshot_begin", activeSessionId: ACTIVE, snapshotId: SNAPSHOT_ID },
				beginPayload(5),
			),
		);

		// Chunk 0 arrives with bytes that differ from the cached transfer.
		expect(() =>
			harness.supervisor.handleWorkerFrame(
				harness.worker,
				frame(
					{
						kind: "outbound",
						outboundType: "session_snapshot_chunk",
						activeSessionId: ACTIVE,
						snapshotId: SNAPSHOT_ID,
					},
					chunkPayload("tampered"),
				),
			),
		).not.toThrow();

		// The mismatched transfer is invalidated...
		expect(harness.generations.has(SNAPSHOT_ID)).toBe(false);
		expect(harness.worker.transcriptCaches.has(ACTIVE)).toBe(false);
		expect(harness.worker.snapshotCache.has(ACTIVE)).toBe(false);
		expect((transcript as unknown as { disposed?: boolean }).disposed).toBe(true);

		// ...but the healthy worker's control channel stays open.
		expect(harness.closeWorker).not.toHaveBeenCalled();
		expect(harness.handleWorkerClose).not.toHaveBeenCalled();
	});

	it("invalidates an end-frame metadata mismatch without closing the worker channel", () => {
		const harness = createHarness();
		seedCompleteGeneration(harness, 5);

		harness.supervisor.handleWorkerFrame(
			harness.worker,
			frame(
				{ kind: "outbound", outboundType: "session_snapshot_begin", activeSessionId: ACTIVE, snapshotId: SNAPSHOT_ID },
				beginPayload(5),
			),
		);

		// End frame declares a chunk count that cannot match the cached transfer.
		expect(() =>
			harness.supervisor.handleWorkerFrame(
				harness.worker,
				frame(
					{
						kind: "outbound",
						outboundType: "session_snapshot_end",
						activeSessionId: ACTIVE,
						snapshotId: SNAPSHOT_ID,
					},
					endPayload(Number.MAX_SAFE_INTEGER),
				),
			),
		).not.toThrow();

		expect(harness.generations.has(SNAPSHOT_ID)).toBe(false);
		expect(harness.closeWorker).not.toHaveBeenCalled();
		expect(harness.handleWorkerClose).not.toHaveBeenCalled();
	});
});
