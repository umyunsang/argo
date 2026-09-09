export default function (pi) { pi.on("before_agent_start", (event) => ({ systemPrompt: event.systemPrompt + "\nSYNTHETIC_EXTENSION_SENTINEL_049e" })); }
