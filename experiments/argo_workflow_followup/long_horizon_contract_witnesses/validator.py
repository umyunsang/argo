"""Local engineered specification. No external truth or efficacy claims."""
import hashlib
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fields(value, names):
    require(type(value) is dict and set(value) == set(names.split()),
            "missing, unknown, or malformed evidence fields")
    return value


def text(value):
    require(type(value) is str and bool(value.strip()), "expected nonempty text")
    return value


def sequence(value, nonempty=False):
    require(type(value) is list and (value or not nonempty), "expected list")
    return value


def strings(value, nonempty=False):
    values = [text(item) for item in sequence(value, nonempty)]
    require(len(values) == len(set(values)), "duplicate identifiers")
    return values


def digest(value):
    text(value)
    require(len(value) == 64 and all(c in "0123456789abcdef" for c in value),
            "expected lowercase SHA-256")
    return value


def payload(value):
    text(value)
    try:
        result = bytes.fromhex(value)
    except ValueError as error:
        raise ValueError("malformed byte evidence") from error
    require(bool(result), "empty byte evidence")
    return result


def sha(data):
    return hashlib.sha256(data).hexdigest()


def exposure(e):
    fields(e, "original_sha256 archive_hex required_span exposed_spans")
    data = payload(e["archive_hex"])
    recoverable = sha(data) == digest(e["original_sha256"])
    spans = [e["required_span"]] + sequence(e["exposed_spans"])
    for span in spans:
        sequence(span)
        require(len(span) == 2 and all(type(x) is int for x in span),
                "span must contain two integer byte offsets")
        require(0 <= span[0] < span[1] <= len(data), "invalid byte span")
    cursor, end = e["required_span"]
    for start, stop in sorted(e["exposed_spans"]):
        if start <= cursor:
            cursor = max(cursor, stop)
    exposed = cursor >= end
    return {"recoverable": recoverable, "evidence_exposed": exposed,
            "eligible": recoverable and exposed}


def graph(e):
    fields(e, "nodes edges claim verifier required_scope")
    nodes = e["nodes"]
    require(type(nodes) is dict and bool(nodes), "missing graph nodes")
    for name, scopes in nodes.items():
        text(name)
        strings(scopes)
    claim, verifier, scope = (text(e[k]) for k in ("claim", "verifier", "required_scope"))
    edges = sequence(e["edges"])
    for edge in edges:
        sequence(edge)
        require(len(edge) == 2, "edge must contain two node IDs")
        for node in edge:
            text(node)
    closed = claim in nodes and verifier in nodes
    closed = closed and all(a in nodes and b in nodes for a, b in edges)
    seen, pending = set(), [claim] if claim in nodes else []
    while pending:
        node = pending.pop()
        if node not in seen:
            seen.add(node)
            pending.extend(b for a, b in edges if a == node and b in nodes)
    reachable = verifier in seen
    matches = scope in nodes.get(verifier, [])
    return {"graph_closed": closed, "verifier_reachable": reachable,
            "scope_matches": matches, "eligible": closed and reachable and matches}


def cache(e):
    fields(e, "current cached")
    current = fields(e["current"], "artifact version bytes_hex")
    cached = fields(e["cached"], "artifact version sha256 result")
    for entry in (current, cached):
        text(entry["artifact"])
        text(entry["version"])
    require(cached["result"] in ("pass", "fail"), "missing cached result")
    byte_match = sha(payload(current["bytes_hex"])) == digest(cached["sha256"])
    bound = all(current[key] == cached[key] for key in ("artifact", "version"))
    return {"reusable": bound and byte_match}


def negative(e):
    fields(e, "prior_context current_context relevant_keys observation")
    prior, current = e["prior_context"], e["current_context"]
    for context in (prior, current):
        require(type(context) is dict and bool(context), "missing context")
        for key, value in context.items():
            text(key)
            text(value)
    require(set(prior) == set(current), "context schema change needs new relevance review")
    relevant = strings(e["relevant_keys"], nonempty=True)
    require(set(relevant) <= set(prior), "missing relevant context")
    observation = fields(e["observation"], "id outcome context_sha256")
    text(observation["id"])
    require(observation["outcome"] == "negative", "missing negative observation")
    encoded = json.dumps(prior, sort_keys=True, separators=(",", ":")).encode()
    bound = sha(encoded) == digest(observation["context_sha256"])
    changed = sorted(key for key in relevant if prior[key] != current[key])
    return {"action": "recheck" if changed or not bound else "exclude",
            "changed_relevant_keys": changed}


def archive(e):
    fields(e, "entries corrections")
    entries = sequence(e["entries"], nonempty=True)
    accepted = {}
    for entry in entries:
        fields(entry, "id priority accepted")
        name = text(entry["id"])
        require(name not in accepted, "duplicate archive entry")
        require(type(entry["priority"]) is int, "priority must be an integer")
        require(type(entry["accepted"]) is bool, "accepted must be boolean")
        accepted[name] = entry["accepted"]
    before = sorted(name for name, valid in accepted.items() if valid)
    best = max(entries, key=lambda item: (item["priority"], item["id"]))["id"]
    for correction in sequence(e["corrections"]):
        fields(correction, "id accepted reason")
        name = text(correction["id"])
        require(name in accepted, "correction refers to missing archive evidence")
        require(type(correction["accepted"]) is bool, "accepted must be boolean")
        text(correction["reason"])
        accepted[name] = correction["accepted"]
    return {"historical_best": best, "accepted_before": before,
            "eligible_after": sorted(name for name, valid in accepted.items() if valid)}


def replay(e):
    fields(e, "files")
    byte_matches, originals, names = [], [], set()
    for file in sequence(e["files"], nonempty=True):
        fields(file, "name origin bytes_hex original_sha256")
        name = text(file["name"])
        require(name not in names, "duplicate replay file")
        names.add(name)
        require(file["origin"] in ("original", "inferred"), "unknown provenance")
        byte_matches.append(sha(payload(file["bytes_hex"])) == digest(file["original_sha256"]))
        originals.append(file["origin"] == "original")
    matches, original = all(byte_matches), all(originals)
    return {"bytes_match": matches, "original_provenance": original,
            "original_replay": matches and original}


VALIDATORS = {"exposure": exposure, "graph": graph, "cache": cache,
              "negative": negative, "archive": archive, "replay": replay}


def validate(record):
    """Return contract decisions; malformed/missing evidence raises ValueError."""
    fields(record, "kind evidence")
    kind = text(record["kind"])
    require(kind in VALIDATORS, "unknown witness kind")
    return VALIDATORS[kind](record["evidence"])
