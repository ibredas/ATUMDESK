
# ⚡ PROTOCOL CONFIRMATION ⚡

**User Question**: "WHAT WILL YOU DO WHEN I ASK FOR SOMETHING?"

**My Response**:

1.  **TRIGGER**: You prompt me.
2.  **IMMEDIATE**: I execute `### 1) STUDY (Deep System Understanding) ⚠️ CRITICAL
**THIS STEP IS NON-NEGOTIABLE — SKIP IT AND YOU WILL BREAK PRODUCTION.**

**Objective**: Establish ground truth (what exists, what’s running, what’s working) before touching anything.

#### A) What Is Currently Installed & Running (Ground Truth Snapshot)
Run and record:
- All active services related to the system
- All running processes related to the system
- All listening ports for the system + owning PIDs
- All service manager definitions (unit files) and their paths
- Runtime environments (venv/paths) and versions
- Key directories: config, logs, data, binaries, integrations

**Output requirement**: Create `STATE_SNAPSHOT_BEFORE.md` including:
- timestamp, host, current user, cwd
- services list (running + enabled)
- port map
- key paths used
- runtime versions

#### B) What Is Working (Current Operations)
Prove health with evidence:
- service health status
- last 1h logs scan for ERROR/WARN spikes
- endpoint smoke tests (if applicable)
- dataflow proof (input → processing → output)

**Output requirement**: Include proof snippets and “green/red” status in `STATE_SNAPSHOT_BEFORE.md`.

#### C) Impact Analysis (Before ANY Modification)
Write `IMPACT_NOTE.md` answering:
- What will change (files/services/configs/schemas)
- Who depends on it (dependency list)
- What can break (top failure modes)
- What must NOT change (constraints)
- What restarts are required (order)
- Rollback trigger conditions

#### D) Conflict Prevention Checklist (Expanded & Enforced)
Before modifying anything:
- [ ] Port conflicts checked
- [ ] Path conflicts checked
- [ ] Import/module conflicts checked
- [ ] Service name conflicts checked
- [ ] Config key conflicts checked
- [ ] Permissions/ownership checked
- [ ] Disk/RAM headroom checked
- [ ] Duplicate writers to same DB/file checked

#### E) Modification Safety Matrix (Upgrade)
Classify your change and apply required checks:

| Type | Risk | Must Do |
|------|------|---------|
| New service | HIGH | port plan, unit name uniqueness, restart order, disable plan |
| Edit code | MED | signature/caller audit, logging, unit smoke tests |
| Config change | HIGH | backup, schema validate, identify all readers |
| New dependency | MED | pin version, isolate env, import test |
| Schema/data migration | CRITICAL | backup, migration script, rollback script, data validation |

**✅ Exit Criteria (Step 1 passes only if):**
- `STATE_SNAPSHOT_BEFORE.md` exists and is complete
- `IMPACT_NOTE.md` exists
- No unresolved red flags

---

### 2) ANALYZE (Current State)
**Objective**: Understand the system’s architecture + dependency graph so you don’t create “works on my machine” fractures.

**Agent must produce:**
`ARCH_MAP` (written inside `CHANGE_DESIGN.md` or separate section):
- service map (service → ports → paths → logs)
- dataflow map (inputs → transforms → stores → outputs)
- dependency map (what relies on what)

**Identify integration points:**
- API boundaries, queues, DBs, file handoffs

**Identify common failure points:**
- split-brain DB paths, race conditions, restart ordering

**✅ Exit Criteria:**
- Dependency map written
- Integration points listed
- Risks documented

` 
3.  **THE KIT**: I generate a **Strategic Plan**:
    *   **Roadmap**: High-level milestones.
    *   **Implementation Plan**: Technical details.
    *   **Task Breakdown**: Checklist.
4.  **THE STOP**: I **STOP** and `notify_user` with:
    *   The Proposed KIT.
    *   **Clarifying Questions** (to align with Architect).
5.  **REFINE**: I update the plan based on your answers.


**Result**: No more "lazy agent". Only **Expert Execution**.


