import type { Plugin } from "../node_modules/@opencode-ai/plugin/dist/index.js"
import { tool } from "../node_modules/@opencode-ai/plugin/dist/index.js"
import { existsSync, realpathSync, openSync, closeSync, constants } from "node:fs"
import { join, isAbsolute } from "node:path"
import { execFileSync, execFile } from "node:child_process"

const READ = new Set(["read", "glob", "grep", "lsp_diagnostics", "lsp_symbols", "workflow_status"])
const token = (state: any) => [state.owner, state.owner_epoch, state.state_version]
const same = (a: any, b: any) => JSON.stringify(a) === JSON.stringify(b)

function script(root: string, name: string): string {
  if (!isAbsolute(root) || realpathSync(root) !== root) throw new Error("Invalid workspace")
  const path = join(root, "scripts/enforcement", name)
  if (!existsSync(path) || realpathSync(path) !== path) throw new Error("Missing/redirected enforcement")
  return path
}

function response(raw: string): any {
  const value = JSON.parse(raw)
  if (value.ok !== true || value.result == null) throw new Error(value.error ?? "Explicit success required")
  return value.result
}

function invoke(root: string, request: any): any {
  const raw = execFileSync("bash", [script(root, "workflow-enforce.sh")], {
    cwd: root, input: JSON.stringify({ ...request, workspace: root }), encoding: "utf8", timeout: 2000,
  })
  return response(raw)
}

function admin(root: string, request: any): any {
  const fd = openSync(join(root, ".opencode/workflow-operator.key"), constants.O_RDONLY | constants.O_NOFOLLOW)
  try {
    return response(execFileSync("python3", ["-B", script(root, "operator_cli.py")], {
      cwd: root, input: JSON.stringify({ ...request, workspace: root }), encoding: "utf8", timeout: 2000,
      env: { ...process.env, WORKFLOW_OPERATOR_FD: "3" }, stdio: ["pipe", "pipe", "pipe", fd],
    }))
  } finally { closeSync(fd) }
}

function envelope(state: any, session: string, action: string, extra = {}): any {
  return { workspace: state.workspace, session_id: session, run_id: state.run_id,
    expected: token(state), action, ...extra }
}

async function bound(client: any, session: string): Promise<any> {
  if (!session) throw new Error("Session binding required")
  const res = await client.session.get({ path: { sessionID: session } })
  const directory = res?.data?.directory ?? res?.directory
  if (typeof directory !== "string") throw new Error("Ambiguous session workspace")
  return invoke(directory, { action: "bound", session_id: session })
}

function requestFor(state: any, input: any, args: any, action: string): any {
  const actor = state.data.actors[input.sessionID]
  return envelope(state, input.sessionID, action, { tool: input.tool, arguments: args,
    dispatch_id: input.callID, deliverable_digest: actor.scope.deliverable_digest })
}

async function startTask(client: any, state: any, input: any, args: any): Promise<void> {
  const actor = state.data.actors[input.sessionID]
  const profile = actor.child_profiles?.[args.subagent_type]
  if (!profile || args.task_id) throw new Error("Explicit new-child grant required; resume needs recovery")
  const created = await client.session.create({ body: { parentID: input.sessionID, title: "Bound workflow child",
    permission: [{ permission: "task", pattern: "*", action: "deny" }] }, query: { directory: state.workspace } })
  const child = created.data ?? created
  if (!child.id || child.directory !== state.workspace || child.parentID !== input.sessionID) throw new Error("Child binding mismatch")
  args.task_id = child.id
  const started = invoke(state.workspace, { ...requestFor(state, input, args, "dispatch-begin"),
    agent: args.subagent_type, child_sessions: [child.id] })
  admin(state.workspace, { action: "enroll", run_id: state.run_id, expected: token(started),
    session_id: child.id, profile: { ...profile, parent_effect: input.callID } })
}

async function before(client: any, input: any, output: any): Promise<void> {
  const state = await bound(client, input.sessionID)
  const args = input.tool === "workflow_action" ? { action_id: output.args.action_id } : output.args
  const check = requestFor(state, input, args, "check")
  if (invoke(state.workspace, check).decision !== "allow") throw new Error("Tool denied")
  if (READ.has(input.tool)) return
  admin(state.workspace, { action: "inspect-run", run_id: state.run_id })
  if (!input.callID) throw new Error("Call identity required")
  if (input.tool === "workflow_action") { output.args.call_id = input.callID; return }
  if (input.tool === "task") return startTask(client, state, input, output.args)
  invoke(state.workspace, requestFor(state, input, output.args, "tool-begin"))
}

function reconciliation(state: any, record: any, session: string): string | undefined {
  if (same(token(state), record.start_token)) return undefined
  const parent = record.parent_effect && state.data.effect_records[record.parent_effect]?.origin_session
  const candidate = parent ?? session
  const actor = state.data.actors[candidate]
  if (!actor?.can_reconcile || !actor?.host_reconcile) throw new Error("Explicit reconcile-effect authorization required")
  return candidate
}

function closeChildren(state: any, record: any, metadata: any, status: string): any {
  if (record.kind !== "dispatch" || record.status !== "running") return state
  if (status === "completed" && !record.child_sessions.includes(metadata?.sessionId)) throw new Error("Unverified task adapter child receipt")
  for (const session of record.child_sessions) {
    state = admin(state.workspace, { action: "close-child", run_id: state.run_id,
      expected: token(state), session_id: session, reason: "Pinned host task settled; registered effects checked terminal" })
  }
  return state
}

async function finish(client: any, input: any, output: any, status: string): Promise<void> {
  let state = await bound(client, input.sessionID)
  const record = invoke(state.workspace, envelope(state, input.sessionID, "effect-status", { call_id: input.callID }))
  const reconciler = record.status === "running" ? reconciliation(state, record, input.sessionID) : undefined
  state = closeChildren(state, record, output.metadata, status)
  const proof = admin(state.workspace, { action: "observe", run_id: state.run_id, expected: token(state),
    session_id: input.sessionID, dispatch_id: input.callID, tool: input.tool, arguments: input.args,
    status, evidence: JSON.stringify({ event: status, output: output.output, call: input.callID }) })
  const action = proof.replay_audit?.action ?? (reconciler ? "reconcile-effect" : record.kind === "dispatch" ? "dispatch-end" : "tool-end")
  const session = proof.replay_audit?.session_id ?? reconciler ?? input.sessionID
  invoke(state.workspace, envelope(state, session, action, { expected: proof.expected,
    dispatch_id: input.callID, effect_token: record.token, identity_digest: record.identity_digest,
    completion_digest: proof.completion_digest, reason: "Authorized host completion reconciled after explicit CAS inspection",
    reason_provenance: { source: "OpenCode 22c1c40 lifecycle", reference: proof.completion_digest } }))
}

async function failure(client: any, event: any): Promise<void> {
  const part = event.type === "message.part.updated" ? event.properties?.part : null
  if (part?.type !== "tool" || part.state?.status !== "error" || READ.has(part.tool)) return
  const input = { sessionID: part.sessionID, callID: part.callID, tool: part.tool, args: part.state.input }
  try { await finish(client, input, { output: part.state.error }, "failed") }
  catch { /* Unknown, stale or active-child effects stay protected for explicit recovery. */ }
}

function runAction(root: string, request: any): Promise<any> {
  return new Promise((resolve, reject) => {
    const child = execFile("bash", [script(root, "workflow-enforce.sh")], { cwd: root, timeout: 35000, maxBuffer: 4194304 },
      (error, stdout) => { try { if (error) throw error; resolve(response(stdout)) } catch (cause) { reject(cause) } })
    child.stdin!.end(JSON.stringify({ ...request, workspace: root }))
  })
}

async function actionTool(client: any, args: any, context: any): Promise<string> {
  const state = await bound(client, context.sessionID)
  if (!args.call_id || context.directory !== state.workspace) throw new Error("Action context missing")
  const input = { sessionID: context.sessionID, callID: args.call_id, tool: "workflow_action", args: { action_id: args.action_id } }
  const request = requestFor(state, input, input.args, "run-action")
  request.expected = JSON.parse(args.expected)
  const result = await runAction(state.workspace, request)
  await finish(client, input, { output: result.output }, result.status)
  return JSON.stringify({ output: result.output, status: result.status, returncode: result.returncode })
}

async function statusTool(client: any, args: any, context: any): Promise<string> {
  const state = await bound(client, context.sessionID)
  if (context.directory !== state.workspace) throw new Error("Context workspace mismatch")
  const action = args.action === "pass_gate" ? "pass" : args.action === "fail_gate" ? "fail" : args.action
  const request = envelope(state, context.sessionID, action, { evidence: args.evidence ?? "", deliverable_digest: args.deliverable_digest })
  if (action !== "status") request.expected = JSON.parse(args.expected)
  return JSON.stringify(invoke(state.workspace, request))
}

export const WorkflowEnforcer: Plugin = async ({ client }: any) => ({
  "tool.execute.before": (input: any, output: any) => before(client, input, output),
  "tool.execute.after": async (input: any, output: any) => {
    if (!READ.has(input.tool) && input.tool !== "workflow_action") await finish(client, input, output, "completed")
  },
  event: ({ event }: any) => failure(client, event),
  "experimental.session.compacting": async (input: any, output: any) => {
    const state = await bound(client, input.sessionID)
    output.context.push(JSON.stringify(envelope(state, input.sessionID, "status")))
  },
  tool: {
    workflow_status: tool({ description: "Bound workflow status; mutations require an explicit expected CAS tuple.",
      args: { action: tool.schema.enum(["status", "advance", "pass_gate", "fail_gate"]), expected: tool.schema.string().optional(),
        evidence: tool.schema.string().optional(), deliverable_digest: tool.schema.string().optional() },
      execute: (args: any, context: any) => statusTool(client, args, context) }),
  },
})
