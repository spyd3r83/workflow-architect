import { test, expect, mock } from "bun:test"
import { mkdtempSync, mkdirSync, writeFileSync, rmSync, copyFileSync, readFileSync, realpathSync } from "node:fs"
import { join, resolve } from "node:path"
import { createHash } from "node:crypto"

mock.module("@opencode-ai/plugin", () => {
  const field: any = { optional: () => field }
  const tool: any = (value: any) => value
  tool.schema = { enum: () => field, number: () => field, string: () => field }
  return { tool }
})
const { WorkflowEnforcer } = await import("../../../.opencode/plugins/workflow-enforcer")
const hash = (value: any) => createHash("sha256").update(value).digest("hex")
const token = (state: any) => [state.owner, state.owner_epoch, state.state_version]
const stable = (v: any): any => Array.isArray(v) ? v.map(stable) : v && typeof v === "object" ? Object.fromEntries(Object.keys(v).sort().map(k => [k, stable(v[k])])) : v

function fixture(role = "coordinator", taskAvailable = true) {
  const root = mkdtempSync(join(import.meta.dir, "plugin-fixture-"))
  const store = join(root, ".opencode/workflow-runs")
  mkdirSync(store, { recursive: true })
  mkdirSync(join(root, "scripts/enforcement"), { recursive: true })
  writeFileSync(join(root, "opencode.json"), '{"default_agent":"fixture"}')
  for (const name of ["run_store.py", "run_cli.py", "run_policy.py", "run_effects.py", "run_operator.py", "operator_cli.py", "workflow-enforce.sh"]) {
    copyFileSync(resolve(import.meta.dir, "../enforcement", name), join(root, "scripts/enforcement", name))
  }
  writeFileSync(join(root, ".opencode/workflow-operator.key"), Buffer.alloc(32, 102), { mode: 0o600 })
  const config = { schema_version: 1, command_adapter: "exact-action-v1", total_phases: 2, min_evidence_chars: 20, max_revisions: 3, implementation_phases: [1], revision_phases: [1] }
  writeFileSync(join(root, ".opencode/workflow-config.json"), JSON.stringify(config))
  writeFileSync(join(store, "config.json"), JSON.stringify({ schema_version: 1, capacity: 5, filesystem: "local" }))
  const scope = { targets: ["fixture.txt", "second.txt"], read_targets: ["fixture.txt", "diagnostic.py"], deliverable_digest: "a".repeat(64) }
  const child = { role: "leaf", task_available: false, can_reconcile: false, tools: ["write", "apply_patch"], phases: [1], agents: [], scope, completion_producers: ["opencode-host"] }
  const actor = { ...child, role, task_available: taskAvailable, can_reconcile: role === "coordinator", host_reconcile: role === "coordinator", agents: ["worker"], child_profiles: { worker: child }, actions: ["diagnostic"], tools: ["write", "apply_patch", "workflow_action"] }
  const data = { policy_config: config, authorization: { run_id: "one", revoked: false, approval_digests: [] }, revision_count: 0, current_phase: 1,
    phases: { "1": { gate: "pending", status: "in_progress", attempt: 1, deliverable_digest: null }, "2": { gate: "pending", status: "pending", attempt: 1 } }, actors: { s1: actor } }
  const state: any = { schema_version: 1, workspace: root, run_id: "one", owner: "owner", owner_epoch: 1, state_version: 2, published: true, lifecycle: "active", effects: [], data }
  writeFileSync(join(store, "one.run.json"), JSON.stringify(state))
  writeFileSync(join(store, "active.json"), JSON.stringify({ schema_version: 1, workspace: root, run_id: "one" }))
  writeFileSync(join(store, "s1.binding.json"), JSON.stringify({ schema_version: 1, workspace: root, run_id: "one", session_id: "s1", owner: "owner", owner_epoch: 1 }))
  const sessions: any = { s1: { id: "s1", directory: root } }
  const lookups: any[] = []

  const client: any = { session: { get: async ({ path }: any) => { lookups.push(path); return { data: sessions[path.id] } }, create: async ({ body }: any) => {
    const child = { id: "child1", directory: root, parentID: body.parentID }; sessions.child1 = child; return { data: child }
  } } }
  return { root, store, state, client, lookups, read: () => JSON.parse(readFileSync(join(store, "one.run.json"), "utf8")),
    plugin: () => WorkflowEnforcer({ directory: root, client } as any) as Promise<any>, clean: () => rmSync(root, { recursive: true }) }
}

test("session lookup uses SDK path id and rejects unknown sessions before enforcement", async () => {
  const f = fixture()
  try {
    const plugin = await f.plugin()
    await plugin.tool.workflow_status.execute({ action: "status" }, { sessionID: "s1", directory: f.root })
    expect(f.lookups).toEqual([{ id: "s1" }])
    const before = readFileSync(join(f.store, "one.run.json"), "utf8")
    await expect(plugin.tool.workflow_status.execute({ action: "status" }, { sessionID: "unknown", directory: f.root })).rejects.toThrow("Ambiguous session workspace")
    expect(f.lookups.at(-1)).toEqual({ id: "unknown" })
    expect(readFileSync(join(f.store, "one.run.json"), "utf8")).toBe(before)
  } finally { f.clean() }
})



test("actual task:false worker writes within handoff and completes", async () => {
  const loaded = readFileSync(resolve(import.meta.dir, "../../../.opencode/agents/implementation-planner.md"), "utf8")
  expect(loaded).toContain("mode: subagent")
  expect(loaded).toContain("task:false leaf")
  const capability = /^  task: (true|false)$/m.exec(loaded)?.[1]
  expect(capability).toBe("false")
  const f = fixture("leaf", capability === "true")
  try {
    const plugin = await f.plugin()
    const args = { filePath: join(f.root, "fixture.txt"), content: "fixture" }
    const input = { sessionID: "s1", callID: "w1", tool: "write", args }
    await plugin["tool.execute.before"](input, { args })
    writeFileSync(args.filePath, args.content)
    await plugin["tool.execute.after"](input, { output: "written" })
    expect(f.read().effects).toEqual([])
    expect(f.read().data.effect_records.w1.status).toBe("completed")
  } finally { f.clean() }
})

test("actual task parent, child mutation, explicit reconciliation, gate", async () => {
  const f = fixture()
  try {
    const plugin = await f.plugin()
    const args: any = { subagent_type: "worker", description: "fixture", prompt: "fixture work" }
    const parent = { sessionID: "s1", callID: "d1", tool: "task", args }
    await plugin["tool.execute.before"](parent, { args })
    expect(args.task_id).toBe("child1")
    const childArgs = { filePath: join(f.root, "fixture.txt"), content: "child" }
    const child = { sessionID: "child1", callID: "w1", tool: "write", args: childArgs }
    await plugin["tool.execute.before"](child, { args: childArgs })
    writeFileSync(childArgs.filePath, childArgs.content)
    await plugin["tool.execute.after"](child, { output: "written" })
    await plugin["tool.execute.after"](parent, { output: "task completed", metadata: { sessionId: "child1" } })
    expect(f.read().effects).toEqual([])
    expect(f.read().data.effect_records.d1.completion_audit.action).toBe("reconcile-effect")
    await plugin.tool.workflow_status.execute({ action: "pass_gate", expected: JSON.stringify(token(f.read())), evidence: "fixture work independently witnessed", deliverable_digest: "a".repeat(64) }, { sessionID: "s1", directory: f.root })
    expect(f.read().data.phases["1"].gate).toBe("passed")
  } finally { f.clean() }
})

test("durable lookup survives plugin recreation; duplicate callback is no-op", async () => {
  const f = fixture()
  try {
    let plugin = await f.plugin()
    const args = { filePath: join(f.root, "fixture.txt"), content: "fixture" }
    const input = { sessionID: "s1", callID: "w1", tool: "write", args }
    await plugin["tool.execute.before"](input, { args })
    plugin = await f.plugin()
    await plugin["tool.execute.after"](input, { output: "done" })
    const before = readFileSync(join(f.store, "one.run.json"), "utf8")
    await plugin["tool.execute.after"](input, { output: "done" })
    expect(readFileSync(join(f.store, "one.run.json"), "utf8")).toBe(before)
  } finally { f.clean() }
})

test("registered host error event terminalizes failure without claiming success", async () => {
  const f = fixture()
  try {
    const plugin = await f.plugin()
    const args = { filePath: join(f.root, "fixture.txt"), content: "fixture" }
    await plugin["tool.execute.before"]({ sessionID: "s1", callID: "w1", tool: "write" }, { args })
    await plugin.event({ event: { type: "message.part.updated", properties: { part: { type: "tool", sessionID: "s1", callID: "w1", tool: "write", state: { status: "error", input: args, error: "fixture failure" } } } } })
    expect(f.read().effects).toEqual([])
    expect(f.read().data.effect_records.w1.status).toBe("failed")
    expect(f.read().data.dispatch_failed).toBe(true)
  } finally { f.clean() }
})

test("missing coordinator dispatch is denied in coordinator role", async () => {
  const f = fixture("coordinator", false)
  try { const p = await f.plugin(); await expect(p["tool.execute.before"]({ sessionID: "s1", callID: "d1", tool: "task" }, { args: { subagent_type: "worker" } })).rejects.toThrow() }
  finally { f.clean() }
})

for (const target of [".opencode/workflow-operator.key", "scripts/enforcement/run_store.py", "../escape"]) {
  test(`actual plugin protects target ${target}`, async () => {
    const f = fixture()
    try { const p = await f.plugin(); await expect(p["tool.execute.before"]({ sessionID: "s1", callID: "w1", tool: "write" }, { args: { filePath: `${f.root}/${target}`, content: "denied" } })).rejects.toThrow() }
    finally { f.clean() }
  })
}

for (const body of ["exit 3", "printf '{broken'", "sleep 3"]) {
  test(`actual plugin denies subprocess failure: ${body}`, async () => {
    const f = fixture()
    try { writeFileSync(join(f.root, "scripts/enforcement/workflow-enforce.sh"), body); const p = await f.plugin(); await expect(p["tool.execute.before"]({ sessionID: "s1", callID: "w1", tool: "write" }, { args: { filePath: join(f.root, "fixture.txt") } })).rejects.toThrow() }
    finally { f.clean() }
  })
}

for (const [file, body] of [["active.json", "{"], ["active.json", '{"schema_version":1,"run_id":"absent"}'], ["one.run.json", '{"schema_version":999}']]) {
  test(`actual plugin rejects invalid binding ${body}`, async () => {
    const f = fixture()
    try { writeFileSync(join(f.store, file), body); const p = await f.plugin(); await expect(p["tool.execute.before"]({ sessionID: "s1", callID: "w1", tool: "write" }, { args: { filePath: join(f.root, "fixture.txt") } })).rejects.toThrow() }
    finally { f.clean() }
  })
}

test("actual exact-action custom tool executes a pinned diagnostic", async () => {
  const f = fixture()
  try {
    const script = join(f.root, "diagnostic.py")
    writeFileSync(script, 'print("diagnostic-ok")\n')
    const executable = realpathSync("/usr/bin/python3")
    const definition = { argv: [executable, "-I", "-B", script], cwd: ".", classification: "diagnostic", scope: "fixture", inputs: { "diagnostic.py": hash(readFileSync(script)) }, outputs: [], timeout_ms: 1000, executable_sha256: hash(readFileSync(executable)) }
    f.state.data.action_catalog = { diagnostic: { definition, subject_hash: hash(JSON.stringify(stable(definition))) } }
    writeFileSync(join(f.store, "one.run.json"), JSON.stringify(f.state))
    const plugin = await f.plugin()
    const args: any = { action_id: "diagnostic", expected: JSON.stringify(token(f.read())) }
    await plugin["tool.execute.before"]({ sessionID: "s1", callID: "a1", tool: "workflow_action" }, { args })
    const value = await plugin.tool.workflow_action.execute(args, { sessionID: "s1", directory: f.root })
    expect(JSON.parse(value).output.trim()).toBe("diagnostic-ok")
    expect(f.read().effects).toEqual([])
  } finally { f.clean() }
})

test("parent cancellation protects active child and unknown effects", async () => {
  const f = fixture()
  try {
    const plugin = await f.plugin()
    const args: any = { subagent_type: "worker", description: "fixture", prompt: "fixture" }
    await plugin["tool.execute.before"]({ sessionID: "s1", callID: "d1", tool: "task" }, { args })
    const childArgs = { filePath: join(f.root, "fixture.txt"), content: "pending" }
    await plugin["tool.execute.before"]({ sessionID: "child1", callID: "w1", tool: "write" }, { args: childArgs })
    const error = (sessionID: string, callID: string, tool: string, input: any) => ({ event: { type: "message.part.updated", properties: { part: { type: "tool", sessionID, callID, tool, state: { status: "error", input, error: "cancelled fixture" } } } } })
    const before = readFileSync(join(f.store, "one.run.json"), "utf8")
    await plugin.event(error("s1", "unknown", "task", args))
    await plugin.event(error("s1", "d1", "task", args))
    expect(readFileSync(join(f.store, "one.run.json"), "utf8")).toBe(before)
    await plugin.event(error("child1", "w1", "write", childArgs))
    await plugin.event(error("s1", "d1", "task", args))
    expect(f.read().effects).toEqual([])
    expect(f.read().data.effect_records.d1.status).toBe("failed")
  } finally { f.clean() }
})

test("unverified task provider child metadata never completes the effect", async () => {
  const f = fixture()
  try {
    const plugin = await f.plugin()
    const args: any = { subagent_type: "worker", description: "fixture", prompt: "fixture" }
    const input = { sessionID: "s1", callID: "d1", tool: "task", args }
    await plugin["tool.execute.before"](input, { args })
    const before = readFileSync(join(f.store, "one.run.json"), "utf8")
    await expect(plugin["tool.execute.after"](input, { output: "done", metadata: { sessionId: "foreign" } })).rejects.toThrow()
    expect(readFileSync(join(f.store, "one.run.json"), "utf8")).toBe(before)
  } finally { f.clean() }
})
