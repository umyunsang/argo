import { appendFileSync, readFileSync } from "node:fs";

const recordPath = process.argv[2];
const request = JSON.parse(readFileSync(0, "utf8"));
appendFileSync(recordPath, `${JSON.stringify(request)}
`);
if (request.action !== "read_public_result") {
  process.stdout.write(JSON.stringify({ ok: false, error: "INVALID_ARGUMENT" }));
} else {
  process.stdout.write(JSON.stringify({
    ok: true,
    result: {
      phase: "development",
      dev_attempts: 0,
      final_attempts: 0,
      remaining_dev_opportunities: 3,
      runs: [],
    },
  }));
}
