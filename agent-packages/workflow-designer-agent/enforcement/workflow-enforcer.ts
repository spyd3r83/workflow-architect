import type { Plugin } from "@opencode-ai/plugin"
import { tool } from "@opencode-ai/plugin"
import { existsSync } from "node:fs"
import { join } from "node:path"
import { execSync } from "node:child_process"

function getStatePath(directory: string): string {
  return join(directory, ".opencode", "workflow-state.json")
}

function getEnforceScript(directory: string): string {
  return join(directory, "scripts", "enforcement", "workflow-enforce.sh")
}

function runEnforce(directory: string, ...args: string[]): string {
  const script = getEnforceScript(directory)
  if (!existsSync(script)) return ""
  try {
    const result = execSync(`bash "${script}" ${args.map(a => a ? `"${a}"` : "").join(" ")}`, {
      cwd: directory,
      encoding: "utf-8",
      timeout: 10000,
    })
    return result.trim()
  } catch (err: any) {
    return err.stdout?.trim() || ""
  }
}

function ensureState(directory: string): void {
  if (!existsSync(getStatePath(directory))) {
    runEnforce(directory, "init")
  }
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
      const result = runEnforce(directory, "check", input.tool)
      if (result.startsWith("block:")) {
        throw new Error(`[workflow-enforcer] ${result.slice(6)}`)
      }
    },

    "experimental.session.compacting": async (input, output) => {
      const context = runEnforce(directory, "compaction")
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
          "Check or update the workflow enforcement state. Use this to see which phase is current, whether gates have passed, and to advance phases or mark gates as passed/failed.",
        args: {
          action: tool.schema.enum(["status", "advance", "pass_gate", "fail_gate"], {
            description: "Action: 'status' to check state, 'advance' to move to next phase, 'pass_gate' to mark current gate passed, 'fail_gate' to mark current gate failed",
          }),
          phase: tool.schema.number().optional().describe("Phase number for pass_gate/fail_gate/advance (defaults to current phase)"),
          reason: tool.schema.string().optional().describe("Reason for fail_gate"),
        },
        async execute(args) {
          switch (args.action) {
            case "status":
              return runEnforce(directory, "status")
            case "advance":
              return runEnforce(directory, "advance", String(args.phase ?? ""))
            case "pass_gate":
              return runEnforce(directory, "pass", String(args.phase ?? ""))
            case "fail_gate":
              return runEnforce(directory, "fail", String(args.phase ?? ""), args.reason ?? "unspecified")
            default:
              return `Unknown action: ${args.action}`
          }
        },
      }),
    },
  }
}
