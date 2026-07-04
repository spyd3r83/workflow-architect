# Skill File Template

This template defines the structure for creating a skill file. Fill in all `{{PLACEHOLDERS}}`.

---

# Skill: {{SKILL_NAME}}

## Purpose

{{PURPOSE — one sentence: what this skill does. e.g., "Inventories and assesses existing website content for quality, accuracy, and SEO performance."}}

## When To Use

{{WHEN_TO_USE — specific triggers and phases. e.g., "Phase 3 of the website revamp workflow, after intake and before IA mapping."}}

## Required Inputs

{{REQUIRED_INPUTS — what the skill needs to execute.}}

- {{input 1}}
- {{input 2}}

## Process

{{PROCESS — step-by-step procedure. Numbered list, not narrative.}}

1. {{step 1}}
2. {{step 2}}
3. {{step 3}}
4. ...

## Output Format

{{OUTPUT_FORMAT — the structure of the skill's output. Use a code block or template.}}

```
{{output structure}}
```

## Validation Criteria

{{VALIDATION_CRITERIA — checklist for when the skill's output is valid.}}

- [ ] {{criterion 1}}
- [ ] {{criterion 2}}
- [ ] ...

## Common Mistakes

{{COMMON_MISTAKES — what to avoid when using this skill.}}

- {{mistake 1}}
- {{mistake 2}}
- ...

## Example Usage

{{EXAMPLE_USAGE — concrete example with inputs and expected outputs.}}

**Input:**
```
{{example input}}
```

**Output:**
```
{{example output}}
```

---

## Fill Instructions

1. **Skill name**: kebab-case, capability-oriented (e.g., `content-audit`, `threat-modeling`).
2. **Purpose**: one sentence, specific. Not "helps with research".
3. **When To Use**: specific triggers, not "when appropriate".
4. **Required Inputs**: list everything needed. Mark optional inputs.
5. **Process**: numbered steps, not a paragraph. Each step is one action.
6. **Output Format**: show the actual structure. Use code blocks.
7. **Validation Criteria**: verifiable checklist items.
8. **Common Mistakes**: specific to this skill, not generic.
9. **Example Usage**: real inputs and real expected outputs. Not "example goes here".

## Validation Criteria (when this template is properly filled)

- [ ] All 8 sections present and populated.
- [ ] No `{{PLACEHOLDER}}` remains.
- [ ] Purpose is specific (not generic).
- [ ] Process is step-by-step (not narrative).
- [ ] Example usage has real inputs and outputs.
- [ ] Skill is reusable (not hardcoded to one project).
- [ ] Common mistakes are specific to this skill.