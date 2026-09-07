import { spawn } from "node:child_process";
import { readFileSync } from "node:fs";

readFileSync(0);
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
const descendant = spawn(process.execPath, ["-e", "setTimeout(() => process.exit(0), 1500)"], {
  stdio: ["ignore", process.stdout, "ignore"],
});
descendant.unref();
