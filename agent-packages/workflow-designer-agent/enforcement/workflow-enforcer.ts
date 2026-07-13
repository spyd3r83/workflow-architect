import type { Plugin } from "@opencode-ai/plugin"
import { tool } from "@opencode-ai/plugin"
import { existsSync } from "node:fs"
import { join } from "node:path"
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

function extractToolArg(toolName: string, args: any): string {
  if (!args || typeof args !== "object") return ""
  if (toolName === "bash") return String(args.command ?? args.cmd ?? "")
  if (toolName === "write" || toolName === "edit" || toolName === "apply_patch") {
    return String(args.filePath ?? args.path ?? args.file ?? "")
  }
  return ""
}

export const WorkflowEnforcer: Plugin = async ({ directory, client }) => {
  ensureState(directory)

  await client.app.log({
    body: {
      service: "workflow-enforcer",
      level: "info",
      message: "Workflow enforcer plugin initialized",
    },
  })

  return {
    "tool.execute.before": async (input, output) => {
      const toolArg = extractToolArg(input.tool, output.args)
      const result = runEnforce(directory, ["check", input.tool, toolArg])
      if (result.startsWith("block:")) {
        throw new Error(`[workflow-enforcer] ${result.slice(6)}`)
      }
    },

    "experimental.session.compacting": async (_input, output) => {
      const context = runEnforce(directory, ["compaction"])
      if (context) {
        output.context.push(context)
      }
    },

    event: async ({ event }) => {
      if (event.type === "session.created") {
        ensureState(directory)
      }
    },

    tool: {
      workflow_status: tool({
        description:
          "Check or update workflow enforcement state. pass_gate and advance REQUIRE evidence describing completed work. Mutating tools are blocked until the current phase gate is passed.",
        args: {
          action: tool.schema.enum(["status", "advance", "pass_gate", "fail_gate"]),
          phase: tool.schema.number().optional(),
          reason: tool.schema.string().optional(),
          evidence: tool.schema.string().optional(),
        },
        async execute(args) {
          switch (args.action) {
            case "status":
              return runEnforce(directory, ["status"])
            case "advance": {
              const phase = args.phase != null ? String(args.phase) : ""
              const evidence = args.evidence ?? args.reason ?? ""
              const result = runEnforce(directory, ["advance", phase, evidence])
              if (result.startsWith("error:")) {
                throw new Error(`[workflow-enforcer] ${result.slice(6)}`)
              }
              return result
            }
            case "pass_gate": {
              const phase = args.phase != null ? String(args.phase) : ""
              const evidence = args.evidence ?? args.reason ?? ""
              const result = runEnforce(directory, ["pass", phase, evidence])
              if (result.startsWith("error:")) {
                throw new Error(`[workflow-enforcer] ${result.slice(6)}`)
              }
              return result
            }
            case "fail_gate": {
              const phase = args.phase != null ? String(args.phase) : ""
              return runEnforce(directory, ["fail", phase, args.reason ?? "unspecified"])
            }
            default:
              return `Unknown action: ${args.action}`
          }
        },
      }),
    },
  }
}
