import type { Plugin } from "@opencode-ai/plugin"
import { tool } from "@opencode-ai/plugin"
import { existsSync, readFileSync } from "node:fs"
import { join, dirname, resolve } from "node:path"
import { execFileSync } from "node:child_process"

function getStatePath(directory: string): string {
  return join(directory, ".opencode", "workflow-state.json")
}

function getEnforceScript(directory: string): string {
  return join(directory, "scripts", "enforcement", "workflow-enforce.sh")
}

function runEnforce(directory: string, args: string[]): string {
  const script = getEnforceScript(directory)
  if (!existsSync(script)) return ""
  try {
    const result = execFileSync("bash", [script, ...args], {
      cwd: directory,
      encoding: "utf-8",
      timeout: 10000,
    })
    return result.trim()
  } catch (err: any) {
    const out = (err.stdout || err.stderr || err.message || "").toString().trim()
    return out
  }
}

function ensureState(directory: string): void {
  if (!existsSync(getStatePath(directory))) {
    runEnforce(directory, ["init"])
  }
}

/**
 * Walk up from startDir to find the nearest directory containing an
 * opencode.json with a "default_agent" field. This distinguishes a
 * nested generated workflow package from the parent workflow-architect repo.
 * Returns the package root directory, or null if none found.
 */
function findPackageRoot(startDir: string): string | null {
  let dir = resolve(startDir)
  while (true) {
    const opencodeJsonPath = join(dir, "opencode.json")
    if (existsSync(opencodeJsonPath)) {
      try {
        const config = JSON.parse(readFileSync(opencodeJsonPath, "utf-8"))
        if (config.default_agent) {
          return dir
        }
      } catch {
        // Malformed opencode.json — skip this directory
      }
    }
    const parent = dirname(dir)
    if (parent === dir) break
    dir = parent
  }
  return null
}

function readLegacyState(directory: string): any | null {
  const statePath = getStatePath(directory)
  if (!existsSync(statePath)) return null
  try {
    return JSON.parse(readFileSync(statePath, "utf-8"))
  } catch {
    return null
  }
}

function isLegacyStateBoundToSession(directory: string, sessionID: string): boolean {
  const state = readLegacyState(directory)
  if (!state) return false
  const boundSession = state.session_id ?? state.sessionID ?? state.binding?.session_id
  return typeof boundSession === "string" && boundSession === sessionID
}

function legacyStateSummary(directory: string): string {
  const state = readLegacyState(directory)
  return JSON.stringify({
    workflow_package: state?.workflow_package ?? "unknown",
    current_phase: state?.current_phase ?? null,
    current_gate: state?.phases?.[String(state?.current_phase)]?.gate ?? null,
    updated_at: state?.updated_at ?? null,
    binding: "legacy_unbound",
    applied: false,
    warning:
      "Preserved package-wide legacy state is not applied to this session. Use explicit run-scoped enrollment before enforcing or mutating workflow state.",
  })
}

/**
 * Resolve the session's project directory from a sessionID using the SDK client.
 * Returns the session directory string, or null if resolution fails.
 */
async function resolveSessionDir(client: any, sessionID: string): Promise<string | null> {
  if (!sessionID) return null
  try {
    const response = await client.session.get({ path: { id: sessionID } })
    const session = (response as any)?.data ?? response
    return (session as any)?.directory ?? null
  } catch {
    return null
  }
}

/**
 * Resolve the effective enforcement directory for a given session.
 * Uses a cache to avoid repeated SDK calls for explicitly bound sessions.
 * Unbound legacy state is never cached, so later run-scoped enrollment can take
 * effect without restarting the service. Display-only status remains available.
 */
function makeDirResolver(client: any, pluginDir: string) {
  const enfCache = new Map<string, string>()
  const disCache = new Map<string, string>()

  async function resolveEnforcementDir(sessionID: string | undefined): Promise<string> {
    if (!sessionID) return pluginDir

    if (enfCache.has(sessionID)) {
      return enfCache.get(sessionID)!
    }

    const sessionDir = await resolveSessionDir(client, sessionID)
    const pkgRoot = sessionDir ? findPackageRoot(sessionDir) : null

    let resolved: string
    if (pkgRoot && isLegacyStateBoundToSession(pkgRoot, sessionID)) {
      resolved = pkgRoot
    } else if (sessionDir && isLegacyStateBoundToSession(sessionDir, sessionID)) {
      // Session directory has its own enforcement script but no opencode.json marker.
      // Use it directly — this handles edge cases like the canonical workflow-designer-agent package.
      resolved = sessionDir
    } else {
      // No package root found — fail closed for enforcement.
      // Return empty string to signal "no enforcement" rather than using the wrong package.
      resolved = ""
    }

    if (resolved) enfCache.set(sessionID, resolved)
    return resolved
  }

  async function resolveDisplayDir(sessionID: string | undefined, toolContextDir?: string): Promise<string> {
    if (toolContextDir) {
      const pkgRoot = findPackageRoot(toolContextDir)
      if (pkgRoot) return pkgRoot
      return toolContextDir
    }

    if (!sessionID) return pluginDir

    if (disCache.has(sessionID)) {
      return disCache.get(sessionID)!
    }

    const sessionDir = await resolveSessionDir(client, sessionID)
    const pkgRoot = sessionDir ? findPackageRoot(sessionDir) : null

    const resolved = pkgRoot ?? sessionDir ?? pluginDir
    disCache.set(sessionID, resolved)
    return resolved
  }

  function invalidate(sessionID: string): void {
    enfCache.delete(sessionID)
    disCache.delete(sessionID)
  }

  return { resolveEnforcementDir, resolveDisplayDir, invalidate }
}

function extractToolArg(toolName: string, args: any): string {
  if (!args || typeof args !== "object") return ""
  if (toolName === "bash") return String(args.command ?? args.cmd ?? "")
  if (toolName === "write" || toolName === "edit" || toolName === "apply_patch") {
    return String(args.filePath ?? args.path ?? args.file ?? "")
  }
  return ""
}

export const WorkflowEnforcer: Plugin = async ({ directory, client }) => {
  const resolver = makeDirResolver(client, directory)

  ensureState(directory)

  await client.app.log({
    body: {
      service: "workflow-enforcer",
      level: "info",
      message: "Workflow enforcer plugin initialized (session-aware)",
    },
  })

  return {
    "tool.execute.before": async (input, output) => {
      const enforceDir = await resolver.resolveEnforcementDir(input.sessionID)

      if (!enforceDir) {
        if (input.tool === "call_omo_agent" || input.tool === "call-omo-agent") {
          throw new Error(
            "[workflow-enforcer] call_omo_agent is forbidden as an OpenCode dispatch path. Use task(subagent_type=...); if a real task call fails, stop with TASK_DISPATCH_UNAVAILABLE. See dispatch-protocol.md."
          )
        }
        return
      }

      const toolArg = extractToolArg(input.tool, output.args)
      const result = runEnforce(enforceDir, ["check", input.tool, toolArg])
      if (result.startsWith("block:")) {
        throw new Error(`[workflow-enforcer] ${result.slice(6)}`)
      }
    },

    "experimental.session.compacting": async (input, output) => {
      const enforceDir = await resolver.resolveEnforcementDir(input.sessionID)
      if (!enforceDir) return

      const context = runEnforce(enforceDir, ["compaction"])
      if (context) {
        output.context.push(context)
      }
    },

    event: async ({ event }) => {
      const part = event.type === "message.part.updated" ? (event as any).properties?.part : null
      if (part?.type === "tool" && part.tool === "task" && part.state?.status === "error") {
        const enforceDir = await resolver.resolveEnforcementDir(part.sessionID)
        if (enforceDir) runEnforce(enforceDir, ["dispatch-failed"])
      }
      if (event.type === "session.created") {
        // Invalidate cache for new sessions
        const sid = (event as any).properties?.sessionID ?? (event as any).sessionID
        if (sid) {
          resolver.invalidate(sid)
        }
        // Initialize state for the plugin-init directory (backward compatibility)
        ensureState(directory)
      }
    },

    tool: {
      workflow_status: tool({
        description:
          "Check or update workflow enforcement state. pass_gate and advance REQUIRE evidence describing completed work. Mutating tools are blocked until the current phase gate is passed. Binds to the calling session's package root, not the parent repo.",
        args: {
          action: tool.schema.enum(["status", "advance", "pass_gate", "fail_gate"]),
          phase: tool.schema.number().optional(),
          reason: tool.schema.string().optional(),
          evidence: tool.schema.string().optional(),
        },
        async execute(args, context) {
          // Use ToolContext.directory (the session's project directory) for status operations.
          const enforceDir = await resolver.resolveDisplayDir(context.sessionID, context.directory)
          const sessionBound = isLegacyStateBoundToSession(enforceDir, context.sessionID)

          if (!sessionBound) {
            if (args.action === "status") return legacyStateSummary(enforceDir)
            throw new Error(
              "[workflow-enforcer] Legacy package state is not bound to this session and is read-only. Use explicit run-scoped enrollment."
            )
          }

          switch (args.action) {
            case "status":
              return runEnforce(enforceDir, ["status"]) || "No workflow enforcement active in this directory."
            case "advance": {
              const phase = args.phase != null ? String(args.phase) : ""
              const evidence = args.evidence ?? args.reason ?? ""
              const result = runEnforce(enforceDir, ["advance", phase, evidence])
              if (result.startsWith("error:")) {
                throw new Error(`[workflow-enforcer] ${result.slice(6)}`)
              }
              return result
            }
            case "pass_gate": {
              const phase = args.phase != null ? String(args.phase) : ""
              const evidence = args.evidence ?? args.reason ?? ""
              const result = runEnforce(enforceDir, ["pass", phase, evidence])
              if (result.startsWith("error:")) {
                throw new Error(`[workflow-enforcer] ${result.slice(6)}`)
              }
              return result
            }
            case "fail_gate": {
              const phase = args.phase != null ? String(args.phase) : ""
              const reason = args.reason ?? ""
              if (!reason) {
                throw new Error("[workflow-enforcer] fail_gate requires a reason describing the failure.")
              }
              return runEnforce(enforceDir, ["fail", phase, reason])
            }
            default:
              return `Unknown action: ${args.action}`
          }
        },
      }),
    },
  }
}
