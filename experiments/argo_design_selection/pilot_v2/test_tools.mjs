import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import register from "./tools.js";

const dir = fs.mkdtempSync(path.join(os.tmpdir(), "argo-pilot-tools-"));
process.chdir(dir);
fs.mkdirSync("records");
fs.writeFileSync("budget.json", JSON.stringify({ remaining_record_reads: 2 }));
fs.writeFileSync("index.json", "INDEX");
for (const r of ["R1", "R2", "R3", "R4", "R5", "M"]) fs.writeFileSync(`records/${r}.txt`, r);
const tools = new Map();
register({ registerTool(t) { tools.set(t.name, t); } });
function ok(name, value) { if (!value) throw new Error(name); console.log(`PASS ${name}`); }
ok("four-tool thin surface", [...tools.keys()].sort().join(",") === "read_allocation,read_index,read_record,write_decision");
ok("free index", (await tools.get("read_index").execute()).content[0].text === "INDEX");
ok("first read", (await tools.get("read_record").execute("1", { record_id: "R1" })).content[0].text === "R1");
ok("duplicate read is free", !(await tools.get("read_record").execute("2", { record_id: "R1" })).isError);
ok("second read", (await tools.get("read_record").execute("3", { record_id: "R2" })).content[0].text === "R2");
ok("third distinct read blocked", (await tools.get("read_record").execute("4", { record_id: "R3" })).isError);
await tools.get("write_decision").execute("5", { constraint_status: "unverified", action: "recheck", records_inspected: ["R1", "R2"], reason: "x" });
ok("decision written", fs.existsSync("decision.json"));
const log = JSON.parse(fs.readFileSync("record_access_log.json", "utf8"));
ok("two charged reads", log.filter(x => x.tool === "read_record" && x.charged).length === 2);
ok("blocked access logged", log.some(x => x.blocked && x.reason === "verification_budget_exhausted"));
console.log("All checks passed.");
