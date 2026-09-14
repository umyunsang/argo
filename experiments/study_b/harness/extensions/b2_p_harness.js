
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

export default function(pi) {
  const cwd = process.cwd();
  const logPath = path.join(cwd, 'manipulation_log.json');
  const graphPath = path.join(cwd, 'context_graph.json');
  const decisionsPath = path.join(cwd, 'decisions.json');
  const thresholdsPath = path.join(cwd, 'thresholds.json');

  let state = {
    decisions: [],
    thresholds: [],
    graph: { nodes: {}, edges: [] },
    gateBlocks: 0,
    pivots: 0
  };

  // Helper: log manipulation events
  function logEvent(event, data = {}) {
    let logs = [];
    try {
      if (fs.existsSync(logPath)) {
        logs = JSON.parse(fs.readFileSync(logPath, 'utf8'));
      }
    } catch (e) {}
    logs.push({ timestamp: new Date().toISOString(), event, ...data });
    try {
      fs.writeFileSync(logPath, JSON.stringify(logs, null, 2), 'utf8');
    } catch (e) {}
  }

  // --- Fail-Closed Gate REMOVED in B2-P ---

  // --- P: Decision & Threshold Tools REMOVED in B2-P ---

  // --- G: Typed Context Graph Tools (Retained in B2-P) ---
  pi.registerTool({
    name: "graph_add",
    label: "Add Context Graph Node",
    description: "Add a typed research node (gap, hypothesis, decision, experiment, claim, receipt) to the persistent context graph.",
    parameters: {
      type: "object",
      properties: {
        kind: {
          type: "string",
          enum: ["gap", "hypothesis", "decision", "experiment", "claim", "receipt"],
          description: "Kind of research node"
        },
        id: { type: "string", description: "Unique identifier, e.g. hyp:l2_regularization" },
        statement: { type: "string", description: "Clear factual or theoretical statement" },
        data: { type: "object", description: "Optional metadata object" }
      },
      required: ["kind", "id", "statement"]
    },
    async execute(id, params) {
      const allowedKinds = ["gap", "hypothesis", "decision", "experiment", "claim", "receipt"];
      if (!allowedKinds.includes(params.kind)) {
        return { content: [{ type: "text", text: `Error: Invalid kind ${params.kind}. Allowed: ${allowedKinds.join(", ")}` }], isError: true };
      }
      state.graph.nodes[params.id] = {
        kind: params.kind,
        id: params.id,
        statement: params.statement,
        data: params.data || {},
        created_at: new Date().toISOString()
      };
      fs.writeFileSync(graphPath, JSON.stringify(state.graph, null, 2), 'utf8');
      logEvent("graph_add", { id: params.id, kind: params.kind });
      return { content: [{ type: "text", text: `Successfully registered node [${params.kind}:${params.id}] in context_graph.json` }] };
    }
  });

  pi.registerTool({
    name: "graph_query",
    label: "Query Context Graph",
    description: "Query existing nodes and edges in the persistent context graph.",
    parameters: {
      type: "object",
      properties: {
        kind: { type: "string", description: "Filter by kind (optional)" }
      }
    },
    async execute(id, params) {
      logEvent("graph_query", { filter: params.kind });
      let nodes = Object.values(state.graph.nodes);
      if (params.kind) {
        nodes = nodes.filter(n => n.kind === params.kind);
      }
      return { content: [{ type: "text", text: JSON.stringify({ count: nodes.length, nodes }, null, 2) }] };
    }
  });

  // --- L: Falsification Loop & Pivot Tool ---
  pi.registerTool({
    name: "loop_evaluate",
    label: "Evaluate Falsification Threshold",
    description: "Compare observed experimental outcomes against pre-registered thresholds; pivot if falsified.",
    parameters: {
      type: "object",
      properties: {
        metric: { type: "string", description: "Metric name" },
        observed_value: { type: "number", description: "Observed experimental value" }
      },
      required: ["metric", "observed_value"]
    },
    async execute(id, params) {
      const match = state.thresholds.find(t => t.metric === params.metric);
      if (!match) {
        return { content: [{ type: "text", text: `No pre-registered threshold found for metric: ${params.metric}` }], isError: true };
      }
      let passed = false;
      const obs = params.observed_value;
      const target = match.threshold_value;
      if (match.operator === ">") passed = obs > target;
      else if (match.operator === ">=") passed = obs >= target;
      else if (match.operator === "<") passed = obs < target;
      else if (match.operator === "<=") passed = obs <= target;
      else if (match.operator === "==") passed = Math.abs(obs - target) < 1e-9;

      if (passed) {
        logEvent("threshold_evaluated", { metric: params.metric, passed: true, observed: obs, threshold: target });
        return { content: [{ type: "text", text: `PASS: Observed ${obs} satisfies ${match.metric} ${match.operator} ${target}. You may proceed to final answers.` }] };
      } else {
        state.pivots++;
        logEvent("threshold_evaluated", { metric: params.metric, passed: false, observed: obs, threshold: target, pivot: state.pivots });
        return { content: [{ type: "text", text: `FALSIFIED: Observed ${obs} fails ${match.metric} ${match.operator} ${target}. Pivot required (pivot count: ${state.pivots}). Adjust feature space or hyperparameter grid before completing answers.` }] };
      }
    }
  });

  // Tool: read (file tool)
  pi.registerTool({
    name: "read",
    label: "Read File",
    description: "Read file contents.",
    parameters: {
      type: "object",
      properties: { path: { type: "string" } },
      required: ["path"]
    },
    async execute(id, params) {
      const target = path.resolve(cwd, params.path);
      if (!fs.existsSync(target)) return { content: [{ type: "text", text: `File not found: ${params.path}` }], isError: true };
      return { content: [{ type: "text", text: fs.readFileSync(target, "utf8") }] };
    }
  });

  // Tool: write (file tool)
  pi.registerTool({
    name: "write",
    label: "Write File",
    description: "Write content to file.",
    parameters: {
      type: "object",
      properties: { path: { type: "string" }, content: { type: "string" } },
      required: ["path", "content"]
    },
    async execute(id, params) {
      const target = path.resolve(cwd, params.path);
      fs.mkdirSync(path.dirname(target), { recursive: true });
      fs.writeFileSync(target, params.content, "utf8");
      return { content: [{ type: "text", text: `Wrote ${params.content.length} chars to ${params.path}` }] };
    }
  });

  // Tool: bash (shell tool)
  pi.registerTool({
    name: "bash",
    label: "Bash Shell",
    description: "Run bash command.",
    parameters: {
      type: "object",
      properties: { command: { type: "string" } },
      required: ["command"]
    },
    async execute(id, params) {
      try {
        const res = spawnSync("bash", ["-c", params.command], { cwd, encoding: "utf8", timeout: 60000 });
        return { content: [{ type: "text", text: (res.stdout || "") + (res.stderr || "") }] };
      } catch (e) {
        return { content: [{ type: "text", text: e.message }], isError: true };
      }
    }
  });
}
