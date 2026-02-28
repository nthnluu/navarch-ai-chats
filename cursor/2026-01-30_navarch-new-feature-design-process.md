# Navarch new feature design process

- **Date**: 2026-01-30 06:13 UTC
- **Mode**: agent
- **Model**: default
- **Composer ID**: `44ceaabc-838c-4c90-ac4b-4c9526dfbcd7`
- **Changes**: 1 files, +129/-0 lines

---

## User

lets define this process:

I'm building a new feature for Navarch, an open-source multi-cloud GPU fleet management system written in Go. It's a hardware-aware orchestrator for AI labs managing distributed GPU workloads—think similar problem space to Kubernetes, Nomad, Ray, Slurm, but specialized for GPU/AI infrastructure.

Before writing any code, I need you to help me design this properly.

## Phase 1: Understand & Clarify
- Restate the feature in your own words to confirm understanding
- Ask clarifying questions about requirements, constraints, and scope
- Identify ambiguities or unstated assumptions that need answers
- What are the success criteria? How will we know this feature works correctly?

## Phase 2: Research Prior Art
Search for and analyze how similar features are implemented in comparable systems:
- **Kubernetes** (k8s.io, kubernetes/kubernetes repo)
- **Nomad** (HashiCorp)
- **Ray** (distributed AI/ML framework)
- **Slurm** (HPC scheduler)
- **Borg/Omega** (Google papers)
- **Other relevant systems** based on the specific feature

For each relevant system:
- How did they solve this problem?
- What abstractions/APIs did they expose?
- What were the tradeoffs they made and why?
- What lessons learned or pitfalls are documented?

Synthesize: What's the canonical/idiomatic approach? Where do systems diverge and why?

## Phase 3: Design Space Exploration
- What are the different ways we could implement this?
- For each approach, analyze:
  - Complexity (implementation + operational)
  - Consistency/correctness guarantees
  - Performance characteristics
  - Failure modes
  - Extensibility and future-proofing
- What's the simplest thing that could work vs. the "right" long-term solution?
- Recommendation: which approach and why?

## Phase 4: API & Interface Design
- What's the user-facing API? (CLI, config, gRPC, etc.)
- Design for the 80% use case—is it simple and obvious?
- Does it compose well with existing Navarch concepts?
- Is it consistent with conventions in the codebase and similar tools?
- What are the error cases and how are they surfaced to users?

## Phase 5: System Design
- Data model: what state needs to be stored? Where? Consistency requirements?
- Component interactions: what touches what? Draw the flow.
- Distributed systems concerns:
  - What happens during node failures, network partitions, leader elections?
  - Concurrency model—what runs in parallel, what needs coordination?
  - Idempotency, retries, and recovery
- Dependencies: what does this feature rely on? What relies on it?

## Phase 6: Incremental Delivery Plan
- Break into mergeable chunks that each provide value or are safely behind a flag
- What's the MVP that proves the core concept?
- What can be deferred to fast-follow iterations?
- Testing strategy for each phase

## Phase 7: Test Plan
- What unit tests are needed?
- Integration test scenarios
- Failure injection tests (node crash, timeout, partial failure)
- Edge cases and boundary conditions to cover
- How would we load test this at scale?

## Phase 8: Observability & Operations
- What metrics should this emit?
- What logs are needed for debugging?
- How will operators know if this feature is healthy or broken?
- Runbook sketch: what are the expected failure modes and how to remediate?

---

**After this design phase, provide:**
1. A design doc summary I could share for review
2. Recommended file/package structure 
3. Key interfaces and types (Go code)
4. Implementation order with clear milestones

---

## Feature Description:
[I'll describe the feature below]

---

## Assistant

Creating a new design-phase workflow for Navarch.

---

## Assistant

Creating the feature design process.

---

## Assistant

Summary of what was added:

**New workflow: `feature-design`**

**When it runs**  
When you want to design a new Navarch feature before coding, or when you say you want a “design phase” or to explore prior art and design space.

**What it does**  
1. **Finds the feature** – Looks for “Feature Description:” (or similar) in your message; if it’s missing, it asks for a short description.
2. **Runs the 8 phases in order**  
   - Phase 1: Understand & clarify (restate, questions, success criteria)  
   - Phase 2: Research prior art (Kubernetes, Nomad, Ray, Slurm, Borg/Omega + synthesis)  
   - Phase 3: Design space (options, tradeoffs, recommendation)  
   - Phase 4: API & interface design  
   - Phase 5: System design (data model, components, distributed concerns, dependencies)  
   - Phase 6: Incremental delivery plan  
   - Phase 7: Test plan  
   - Phase 8: Observability & operations  
3. **Produces**  
   - Design doc summary (for review)  
   - Recommended file/package structure  
   - Key Go interfaces and types  
   - Implementation order with milestones  

**How to use it**  
In a prompt, either:

- Paste your full template (including “Feature Description:” and the text below it), or  
- Say you want to design a feature and paste the feature description, e.g.  
  **”Use the feature design process. Feature description: [your description].”**

---
