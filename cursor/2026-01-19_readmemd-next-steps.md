# README.md next steps

- **Date**: 2026-01-19 22:26 UTC
- **Mode**: agent
- **Model**: claude-4.5-opus-high-thinking
- **Composer ID**: `11d6fd38-761b-46ad-98bf-ae3fee2d8d86`
- **Changes**: 11 files, +1970/-5 lines

---

## User

looking at the README roadmap, the simulation framework feels like the right next step — lets us validate end-to-end without cloud spend

---

## Assistant

Looking at the README.md, I can see the roadmap section shows what's completed and what's next. Let me check the current state of the codebase to give you a better recommendation on what would be the most impactful next step.

---

## Assistant

Based on my analysis of the codebase and the roadmap, here's my assessment:

## Current State

The foundation is solid:
- Control plane server with full gRPC API ✅
- Node daemon with heartbeat, health check reporting, and command polling ✅
- Database layer for tracking nodes and health ✅
- Basic health check interfaces ✅

## What's Actually Implemented vs. Placeholder

| Component | Status |
|-----------|--------|
| `XidCheck` | **Placeholder** - returns "ok" with "not implemented yet" |
| `CordonAndReplace` | **Placeholder** - just returns `ActionCordon` without integration |
| `runHealthChecks` in node | **Placeholder** - always reports "boot check passed" |

## Recommended Next Step: XID Error Detection

I'd recommend implementing **XID error detection and classification** next. Here's why:

1. **It's already scaffolded** - The `XidCheck` struct exists but does nothing
2. **Clear scope** - Parse `/dev/kmsg` or `dmesg` for NVIDIA XID errors
3. **High value** - XID errors are how you detect real GPU failures (memory errors, driver issues, hardware faults)
4. **Prerequisite for replacement** - You need to detect failures before you can automatically replace nodes

### What XID detection would involve:

```go
// Parse dmesg for entries like:
// "NVRM: Xid (PCI:0000:3b:00): 79, pid=1234, GPU has fallen off the bus"
// "NVRM: Xid (PCI:0000:3b:00): 48, Double Bit ECC Error"
```

Different XID codes mean different things:
- **XID 31, 32, 45** - Often recoverable, GPU reset might fix
- **XID 48, 63, 64, 79** - Usually fatal, need node replacement
- **XID 74** - NVLink error, might affect multi-GPU workloads

Would you like to start implementing XID error detection? We'd need to:
1. Add dmesg/kmsg parsing logic
2. Define XID classification (fatal vs. recoverable)
3. Wire it into the node daemon's health check loop
4. Update the placeholder in `pkg/health/xid.go`

---

## User

actually i want to easily verify this works in the real world. can we create a script or something that sets up a simulated fleet and control plane and lets us submit commands? it could be cool if theres an easy way to specify sequences of commands to run too and also model failures etc. this should be the framework we test everything and will be extended into future.

---

## Assistant

This is a great idea! A simulation framework will be invaluable for testing, demos, and development. Let me build this out.

---

## Assistant

Now I have a good understanding of the data structures. Let me create the simulation framework.

---

## Assistant

Now let me add the yaml dependency and verify everything compiles:

---

## Assistant

Let me check the Makefile and add a simulator target:

---

## Assistant

Now let's test the GPU failure scenario:

---

## Assistant

Excellent! Both scenarios work perfectly. Let me run the tests to make sure everything is still working:

---

## Assistant

All tests pass and the code is clean. Here's a summary of what I've built:

## Fleet Simulator Framework

### New Files

**Core Simulator Package** (`pkg/simulator/`):
- `scenario.go` - YAML scenario format with validation and XID code definitions
- `node.go` - Simulated node that registers, sends heartbeats, reports health, and can have failures injected
- `runner.go` - Scenario runner with event scheduling, embedded control plane, and assertions

**CLI** (`cmd/simulator/main.go`):
- `run <scenario.yaml>` - Run a scenario file
- `interactive` - Start an interactive session with a default fleet
- `validate <scenario.yaml>` - Validate a scenario without running it

**Example Scenarios** (`scenarios/`):
- `basic-fleet.yaml` - Start 3 nodes and verify they all register
- `gpu-failure.yaml` - Inject XID 79 (GPU fallen off bus) and verify node becomes unhealthy
- `xid-classification.yaml` - Test fatal vs. recoverable XID codes
- `cordon-drain.yaml` - Test command flow

### Scenario Format

```yaml
name: gpu-failure
description: Simulate a fatal GPU failure

fleet:
  - id: node-1
    provider: gcp
    region: us-central1
    instance_type: a3-highgpu-8g
    gpu_count: 8
    gpu_type: "NVIDIA H100 80GB HBM3"

events:
  - at: 0s
    action: start_fleet

  - at: 5s
    action: inject_failure
    target: node-1
    params:
      failure_type: xid_error
      xid_code: 79
      gpu_index: 3

  - at: 12s
    action: wait_for_status
    target: node-1
    params:
      expected_status: unhealthy

assertions:
  - type: health_status
    target: node-1
    expected: unhealthy
```

### Usage

```bash
# Build the simulator
make build

# Validate a scenario
./bin/simulator validate scenarios/gpu-failure.yaml

# Run a scenario
./bin/simulator run scenarios/gpu-failure.yaml -v

# Interactive mode (starts control plane + 2 nodes)
./bin/simulator interactive -v

# Or use make targets
make sim                                    # Interactive mode
make sim-run SCENARIO=scenarios/gpu-failure.yaml
```

### Supported Actions

| Action | Description |
|--------|-------------|
| `start_fleet` | Start all simulated nodes |
| `stop_fleet` | Stop all nodes |
| `inject_failure` | Inject a failure (xid_error, nvml_failure, boot_failure) |
| `recover_failure` | Clear failures from a node |
| `issue_command` | Issue cordon/drain/terminate commands |
| `wait_for_status` | Wait for a node to reach a status |
| `log` | Print a message |
| `assert` | Check a condition |

This gives you a foundation to test the entire control plane flow, and it's extensible for future features like automatic node replacement.

---

## User

Can we create user docs for the simulation framework?

---

## Assistant

Let me also add a reference to the simulator in the main README:

---

## Assistant

I've created the simulator documentation at `docs/simulator.md`. Here's what it covers:

**Documentation structure:**

1. **Overview** - What the simulator does and why to use it.

2. **Building and running** - How to build and run scenarios or interactive mode.

3. **Scenario file format** - Complete YAML format reference with:
   - Fleet definition fields
   - Event timing

4. **Available actions** - Detailed reference for all 9 actions:
   - `start_fleet`, `stop_fleet`
   - `inject_failure`, `recover_failure`
   - `issue_command`
   - `wait_for_status`, `wait`
   - `log`, `assert`

5. **Assertions** - How to verify final state.

6. **XID error codes** - Reference table of fatal vs. recoverable codes.

7. **Example scenarios** - Description of included scenarios.

8. **Writing custom scenarios** - Tips for creating new scenarios.

9. **Makefile targets** - Quick reference for make commands.

I also updated the main README.md to:
- Add a "Development" section explaining how to use the simulator
- Update the repository structure to include the simulator and scenarios directories

---

## User

commit the simulator stuff so far

---

## Assistant

The simulator code was already included in a previous commit. What's left to commit is the README updates and the new documentation. Let me commit those:

---

## Assistant

Done! Committed the simulator documentation:

```
dced4ef Add simulator documentation
```

This commit includes:
- `docs/simulator.md` - Full documentation for the fleet simulator
- `README.md` - Updated repository structure and added Development section

Note: The simulator code itself (`cmd/simulator/`, `pkg/simulator/`, `scenarios/`, Makefile updates) was already committed in a previous session (commit `6479b59`).

---
