# Source Log Template

This template defines the structure for the source chain-of-custody log. Fill in all `{{PLACEHOLDERS}}`.

---

# Source Log: {{PACKAGE_NAME}}

## Retrieval Entry Format

```
### RET-XXX: <source title>
- URL: <url>
- Author/Org: <author or organization>
- Date Published: <date>
- Date Retrieved: <YYYY-MM-DD>
- Retrieval Status: success / failed / redirected
- Content Hash: <sha256 of retrieved content, first 16 chars>
- Re-verification Due: <YYYY-MM-DD>
- Used By: <which claims cite this source>
- Notes: <any notes>
```

## Retrieval Entries

### RET-001: {{source title}}
- URL: {{url}}
- Author/Org: {{author/org}}
- Date Published: {{date}}
- Date Retrieved: {{YYYY-MM-DD}}
- Retrieval Status: {{success/failed/redirected}}
- Content Hash: {{hash}}
- Re-verification Due: {{YYYY-MM-DD}}
- Used By: {{claims that cite this}}
- Notes: {{notes}}

### RET-002: {{source title}}

{{...copy per source...}}

## Dual-Source Verification

For compliance and regulatory claims, a second independent source is required.

| Claim | Primary Source | Secondary Source | Verification |
|-------|---------------|-----------------|-------------|
| {{claim}} | RET-XXX | RET-XXX | {{verified/discrepancy}} |

## Re-Verification Schedule

| Domain | Period | Sources Due |
|--------|-------|-------------|
| Security | 30 days | {{RET-XXX list}} |
| Technical | 60 days | {{RET-XXX list}} |
| Legal / compliance | 90 days | {{RET-XXX list}} |
| Marketing | 60 days | {{RET-XXX list}} |
| Design | 180 days | {{RET-XXX list}} |
| Business operations | 180 days | {{RET-XXX list}} |

## Failed Retrievals

| URL | Date Attempted | Status | Fallback Action |
|-----|---------------|--------|----------------|
| {{url}} | {{date}} | {{status}} | {{fallback}} |

---

## Fill Instructions

1. Every source cited in the package must have an entry in this log.
2. Every entry has a unique retrieval ID (RET-XXX).
3. Citations in research summaries and agent/skill files must reference RET-XXX.
4. Record the fetch timestamp and content hash for verification.
5. Set re-verification due date per the domain schedule.
6. For compliance/regulatory claims, record a secondary source.
7. Log failed retrievals and fallback actions.

## Validation Criteria

- [ ] Every citation in the package has a RET-XXX reference.
- [ ] Every RET-XXX entry has URL, author, date, retrieval status.
- [ ] Content hash recorded for verification.
- [ ] Re-verification dates set per domain schedule.
- [ ] Compliance claims have dual-source verification.
- [ ] validate-package.py confirms source-log structure.