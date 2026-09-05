import fs from "node:fs";
import path from "node:path";

export default function register(pi) {
  const cwd = process.cwd();
  const budget = JSON.parse(fs.readFileSync(path.join(cwd, "budget.json"), "utf8"));
  const readIds = new Set();
  const accessPath = path.join(cwd, "record_access_log.json");

  function log(event) {
    let rows = [];
    try { rows = JSON.parse(fs.readFileSync(accessPath, "utf8")); } catch {}
    rows.push({ seq: rows.length + 1, ...event });
    fs.writeFileSync(accessPath, JSON.stringify(rows, null, 2), "utf8");
  }

  function text(value, isError = false) {
    return { content: [{ type: "text", text: value }], isError };
  }

  pi.registerTool({
    name: "read_index",
    label: "Read index",
    description: "Read the free record index and provenance map. Does not use a verification slot.",
    parameters: { type: "object", properties: {} },
    async execute() {
      log({ tool: "read_index", charged: false });
      return text(fs.readFileSync(path.join(cwd, "index.json"), "utf8"));
    },
  });

  pi.registerTool({
    name: "read_allocation",
    label: "Read allocation",
    description: "Read the the allocated verification record. Does not use an additional verification slot.",
    parameters: { type: "object", properties: {} },
    async execute() {
      const p = path.join(cwd, "allocation.json");
      log({ tool: "read_allocation", charged: false, available: fs.existsSync(p) });
      if (!fs.existsSync(p)) return text("No allocation is available for this task.", true);
      return text(fs.readFileSync(p, "utf8"));
    },
  });

  pi.registerTool({
    name: "read_record",
    label: "Read one record",
    description: "Read one record body by id. Each new record id uses one remaining verification slot.",
    parameters: {
      type: "object",
      properties: { record_id: { type: "string", enum: ["R1", "R2", "R3", "R4", "R5", "M"] } },
      required: ["record_id"],
    },
    async execute(_id, params) {
      const rid = String(params.record_id).toUpperCase();
      if (!readIds.has(rid) && readIds.size >= budget.remaining_record_reads) {
        log({ tool: "read_record", record_id: rid, charged: false, blocked: true,
              reason: "verification_budget_exhausted" });
        return text(`Budget exhausted: ${budget.remaining_record_reads} additional record reads allowed.`, true);
      }
      const p = path.join(cwd, "records", `${rid}.txt`);
      if (!fs.existsSync(p)) {
        log({ tool: "read_record", record_id: rid, charged: false, blocked: true,
              reason: "record_not_found" });
        return text(`Unknown record ${rid}.`, true);
      }
      const fresh = !readIds.has(rid);
      readIds.add(rid);
      log({ tool: "read_record", record_id: rid, charged: fresh, blocked: false });
      return text(fs.readFileSync(p, "utf8"));
    },
  });

  pi.registerTool({
    name: "write_decision",
    label: "Write final decision",
    description: "Write decision.json and finish the task.",
    parameters: {
      type: "object",
      properties: {
        constraint_status: { type: "string", enum: ["valid", "withdrawn", "unverified"] },
        action: { type: "string", enum: ["proceed", "recheck"] },
        records_inspected: { type: "array", items: { type: "string" } },
        reason: { type: "string" },
      },
      required: ["constraint_status", "action", "records_inspected", "reason"],
    },
    async execute(_id, params) {
      const payload = {
        constraint_status: params.constraint_status,
        action: params.action,
        records_inspected: params.records_inspected,
        reason: params.reason,
      };
      fs.writeFileSync(path.join(cwd, "decision.json"), JSON.stringify(payload, null, 2), "utf8");
      log({ tool: "write_decision", charged: false });
      return text("decision.json written. Stop now.");
    },
  });
}
