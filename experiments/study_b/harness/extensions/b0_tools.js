
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

export default function(pi) {
  const logPath = path.join(process.cwd(), 'manipulation_log.json');
  function logEvent(toolName, extra = {}) {
    let logs = [];
    try {
      if (fs.existsSync(logPath)) {
        logs = JSON.parse(fs.readFileSync(logPath, 'utf8'));
      }
    } catch (e) {}
    logs.push({ timestamp: new Date().toISOString(), tool: toolName, ...extra });
    try {
      fs.writeFileSync(logPath, JSON.stringify(logs, null, 2), 'utf8');
    } catch (e) {}
  }

  // Intercept every tool call to track exact tool usage
  pi.on("tool_call", async (event) => {
    logEvent(event.toolName, { input: event.input });
  });

  // Tool 1: read
  pi.registerTool({
    name: "read",
    label: "Read File",
    description: "Read the entire contents of a file as UTF-8 text.",
    parameters: {
      type: "object",
      properties: {
        path: { type: "string", description: "Path of the file to read" }
      },
      required: ["path"]
    },
    async execute(id, params) {
      const target = path.resolve(process.cwd(), params.path);
      if (!fs.existsSync(target)) {
        return { content: [{ type: "text", text: `Error: File not found: ${params.path}` }], isError: true };
      }
      try {
        const text = fs.readFileSync(target, "utf8");
        return { content: [{ type: "text", text }] };
      } catch (err) {
        return { content: [{ type: "text", text: `Error reading ${params.path}: ${err.message}` }], isError: true };
      }
    }
  });

  // Tool 2: write
  pi.registerTool({
    name: "write",
    label: "Write File",
    description: "Write text content to a file, overwriting existing contents or creating parent directories if needed.",
    parameters: {
      type: "object",
      properties: {
        path: { type: "string", description: "Path of the file to write" },
        content: { type: "string", description: "Full text content to write" }
      },
      required: ["path", "content"]
    },
    async execute(id, params) {
      const target = path.resolve(process.cwd(), params.path);
      try {
        fs.mkdirSync(path.dirname(target), { recursive: true });
        fs.writeFileSync(target, params.content, "utf8");
        return { content: [{ type: "text", text: `Successfully wrote ${params.content.length} characters to ${params.path}` }] };
      } catch (err) {
        return { content: [{ type: "text", text: `Error writing ${params.path}: ${err.message}` }], isError: true };
      }
    }
  });

  // Tool 3: edit
  pi.registerTool({
    name: "edit",
    label: "Edit File",
    description: "Replace exactly one occurrence of old_str with new_str in a file.",
    parameters: {
      type: "object",
      properties: {
        path: { type: "string", description: "Path of the file to edit" },
        old_str: { type: "string", description: "Exact string to find and replace" },
        new_str: { type: "string", description: "Replacement string" }
      },
      required: ["path", "old_str", "new_str"]
    },
    async execute(id, params) {
      const target = path.resolve(process.cwd(), params.path);
      if (!fs.existsSync(target)) {
        return { content: [{ type: "text", text: `Error: File not found: ${params.path}` }], isError: true };
      }
      try {
        const text = fs.readFileSync(target, "utf8");
        if (!text.includes(params.old_str)) {
          return { content: [{ type: "text", text: `Error: old_str not found in ${params.path}` }], isError: true };
        }
        const count = text.split(params.old_str).length - 1;
        if (count > 1) {
          return { content: [{ type: "text", text: `Error: old_str appears ${count} times in ${params.path}; must be unique` }], isError: true };
        }
        const updated = text.replace(params.old_str, params.new_str);
        fs.writeFileSync(target, updated, "utf8");
        return { content: [{ type: "text", text: `Successfully replaced old_str in ${params.path}` }] };
      } catch (err) {
        return { content: [{ type: "text", text: `Error editing ${params.path}: ${err.message}` }], isError: true };
      }
    }
  });

  // Tool 4: bash
  pi.registerTool({
    name: "bash",
    label: "Bash Shell",
    description: "Execute a shell command synchronously and return stdout and stderr.",
    parameters: {
      type: "object",
      properties: {
        command: { type: "string", description: "Bash command to execute" }
      },
      required: ["command"]
    },
    async execute(id, params) {
      try {
        const res = spawnSync("bash", ["-c", params.command], {
          cwd: process.cwd(),
          encoding: "utf8",
          timeout: 60000,
          maxBuffer: 10 * 1024 * 1024
        });
        const out = (res.stdout || "") + (res.stderr || "");
        return {
          content: [{ type: "text", text: out || `[Process exited with code ${res.status}]` }],
          details: { exitCode: res.status }
        };
      } catch (err) {
        return { content: [{ type: "text", text: `Command execution error: ${err.message}` }], isError: true };
      }
    }
  });
}
