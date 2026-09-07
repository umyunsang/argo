import { appendFileSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";

const [, , recordPath, mode = "normal"] = process.argv;
const input = readFileSync(0);
if (recordPath) {
  appendFileSync(recordPath, `${input.toString("utf8")}\n`, { encoding: "utf8" });
}

if (mode === "timeout") {
  setTimeout(() => undefined, 60_000);
} else if (mode === "oversize") {
  process.stdout.write("x".repeat(300_000));
} else if (mode === "unknown-error") {
  process.stdout.write(JSON.stringify({ ok: false, error: "RAW_HOST_ERROR_SENTINEL" }));
} else if (mode === "unknown-property") {
  process.stdout.write(JSON.stringify({ ok: true, result: {}, extra: "RAW_HOST_SENTINEL" }));
} else if (mode === "metric-scientific") {
  process.stdout.write(`{"ok":true,"result":{"results":[{"run_id":"11111111-1111-4111-8111-111111111111","solution_sha256":"${"3".repeat(64)}","valid":true,"mae":1e3,"rows":292}]}}`);
} else {
  const request = JSON.parse(input.toString("utf8"));
  const sha256 = (value) => createHash("sha256").update(value).digest("hex");
  const solutionContent = {
    "solution.py": "def fit_predict(train, features):\n    return [1.0] * len(features)\n",
    "research.md": "# Synthetic research\n",
    "intent.json": "{\"phase\":\"dev\"}\n",
  };
  const run = {
    intent_sha256: "1".repeat(64),
    run_id: "11111111-1111-4111-8111-111111111111",
    experiment_id: "22222222-2222-4222-8222-222222222222",
    solution_sha256: "3".repeat(64),
    phase: "dev",
  };
  let result;
  switch (request.action) {
    case "read_solution": {
      const content = solutionContent[request.arguments.path];
      result = { path: request.arguments.path, content, sha256: sha256(content) };
      break;
    }
    case "write_solution":
      result = {
        path: request.arguments.path,
        sha256: sha256(request.arguments.content),
        bytes: Buffer.byteLength(request.arguments.content, "utf8"),
      };
      break;
    case "request_R1_run":
      result = run;
      break;
    case "read_public_result":
      result = {
        phase: "development",
        dev_attempts: 1,
        final_attempts: 0,
        remaining_dev_opportunities: 2,
        runs: [{ ...run, status: "DONE" }],
      };
      break;
    case "read_dev_result":
      result = {
        results: [{
          run_id: run.run_id,
          solution_sha256: run.solution_sha256,
          valid: true,
          mae: 12345.125,
          rows: 100,
        }],
      };
      break;
    case "lock_final_artifact":
      result = {
        run_id: request.arguments.run_id,
        artifact_sha256: request.arguments.artifact_sha256,
        lock_sha256: "4".repeat(64),
        solution_sha256: run.solution_sha256,
      };
      break;
    default:
      process.stdout.write(JSON.stringify({ ok: false, error: "INVALID_ARGUMENT" }));
      process.exit(0);
  }
  const response = { ok: true, result };
  if (mode === "unknown-property") response.extra = true;
  if (mode === "metric-exponent" && request.action === "read_dev_result") {
    process.stdout.write(`{"ok":true,"result":{"results":[{"run_id":"${run.run_id}","solution_sha256":"${run.solution_sha256}","valid":true,"mae":1e3,"rows":100}]}}`);
  } else {
    process.stdout.write(JSON.stringify(response));
  }
}
