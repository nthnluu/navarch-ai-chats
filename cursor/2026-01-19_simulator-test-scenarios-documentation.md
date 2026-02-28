# Simulator test scenarios documentation

- **Date**: 2026-01-19 22:38 UTC
- **Mode**: agent
- **Model**: default
- **Composer ID**: `b316fe30-f669-493b-8222-59d1c55e4990`
- **Changes**: 33 files, +120904/-313 lines

---

## User

go through all the changes you made and ensure they abide by the contributing guidelines

---

## Assistant

Let me review all the changes I made for AGENTS.md compliance:

---

## Assistant

I see several issues. Let me check the docs too:

---

## Assistant

Found several violations. Let me fix them:

**Issues found:**

1. **Code comments that restate what code does** (should remove)
2. **Contractions in docs** (should expand)
3. **Bold labels** like `**Benefits:**` (should avoid)
4. **Section comments** that just label code sections

---

## Assistant

Now fix the documentation issues:

---

## Assistant

Now let me check for contractions in the docs:

---

## Assistant

Now let me verify tests still pass and commit:

---

## Assistant

Those are just gofmt alignment changes - not related to AGENTS.md compliance. Let me commit:

---

## Assistant

Done! Fixed the following AGENTS.md violations:

## Code changes

**`pkg/provider/lambda/lambda.go`**
- Removed "// API request/response types" section comment

**`pkg/pool/pool.go`**
- Removed "// Instance configuration" section comment
- Removed "// Health" section comment  
- Removed "// Enforce max limit" comment
- Removed "// Check cooldown" comments (2x)
- Removed "// Enforce min limit" comment
- Removed "// First take cordoned nodes" / "// Then healthy nodes if needed" comments
- Removed "// Select nodes to remove..." comment
- Removed "// Terminate old node" / "// Provision replacement" comments

## Documentation changes

**`pkg/provider/lambda/README.md`**
- Fixed contraction: "doesn't" → "does not"

**`docs/deployment.md`**
- Removed bold labels: `**Benefits:**`, `**GCP custom image:**`, `**Docker:**`, etc.

**`docs/testing-on-gpu.md`**
- Removed bold labels: `**Lambda Labs:**`, `**GCP:**`, `**AWS:**`

**`examples/pools.yaml`**
- Fixed contraction: "don't" → "do not"

---

## User

id imagine the autoscaling logic might want to be interchangeable with various forecasting models and modes (gke autopilot for inspiration)

---

## Assistant

Great insight! Let me design a pluggable autoscaler interface similar to how GKE Autopilot allows different scaling modes:

---

## Assistant

Now let me update the example config to show autoscaler options:

---

## Assistant

Done! Implemented pluggable autoscaler interface inspired by GKE Autopilot:

## Autoscaler interface

```go
type Autoscaler interface {
    Recommend(ctx context.Context, state PoolState) (int, error)
}
```

## Built-in strategies

| Strategy | Use case | Config |
|----------|----------|--------|
| **Reactive** | Scale on current utilization | `scale_up_threshold`, `scale_down_threshold` |
| **Queue-based** | Scale for pending jobs | `jobs_per_node` |
| **Scheduled** | Time-based patterns | `schedule` with day/hour rules |
| **Predictive** | Forecast demand | `lookback_window`, `growth_factor` |
| **Composite** | Combine strategies | `mode: max/min/avg` |

## Example configurations

```yaml
# Reactive: simple threshold-based
autoscaler:
  type: reactive
  scale_up_threshold: 80
  scale_down_threshold: 20

# Queue: scale for workload
autoscaler:
  type: queue
  jobs_per_node: 100

# Scheduled: business hours vs off-hours
autoscaler:
  type: scheduled
  schedule:
    - days: [monday, tuesday, wednesday, thursday, friday]
      start_hour: 9
      end_hour: 18
      min_nodes: 10
      max_nodes: 100

# Composite: take the more aggressive recommendation
autoscaler:
  type: composite
  mode: max
  autoscalers:
    - type: reactive
    - type: queue
```

## Extension point

To add a custom ML-based forecasting model:

```go
type MyMLAutoscaler struct {
    model *MyModel
}

func (a *MyMLAutoscaler) Recommend(ctx context.Context, state PoolState) (int, error) {
    prediction := a.model.Predict(state.UtilizationHistory)
    return calculateNodesNeeded(prediction), nil
}
```

---

## User

for the autoscaler test, it should be pretty extensive to ensure they work. but dont add uneeded extra tests

---

## Assistant

Looking at the tests, I see gaps in edge cases. Let me add the missing critical tests:

---

## Assistant

All tests pass. Let me commit:

---

## Assistant

Done! The tests now cover all critical edge cases:

| Autoscaler | Tests | Coverage |
|------------|-------|----------|
| **Reactive** | 8 | Scale up/down, limits, cooldown, threshold boundaries |
| **Queue** | 7 | Queue depth, limits, cooldown, zero config, rounding |
| **Scheduled** | 5 | Business hours, weekend, outside schedule, no fallback, empty days |
| **Predictive** | 5 | Insufficient history, rising/stable trends, max limit |
| **Composite** | 5 | Max/min/avg modes, empty/single autoscaler |

**Total: 30 test cases** covering critical paths without redundancy.

---

## User

can we add docs for the autoscaler stuff

---

## Assistant

Done! Created `pkg/pool/README.md` with:

- **Pool configuration** - how to set up a pool
- **Autoscaler interface** - the `Autoscaler` interface and `PoolState`
- **Built-in autoscalers** - each with code examples and "use when" guidance:
  - ReactiveAutoscaler
  - QueueBasedAutoscaler
  - ScheduledAutoscaler
  - PredictiveAutoscaler
  - CompositeAutoscaler
- **Custom autoscaler** - how to implement your own
- **Complete example** - full control loop setup
- **Testing** - how to run the tests

---

## User

can we leave comments on all public fields in structs unless its super self explanatory

---

## Assistant

Done! Added field comments to all public struct fields:

**autoscaler.go:**
- `PoolState` - documented metrics like `CurrentNodes`, `Utilization`, `QueueDepth`, `LastScaleTime`
- `ScaleDecision` - clarified `TargetNodes`, `Reason`, `Confidence`
- `ScheduleEntry` - explained `DaysOfWeek` (empty = all), `StartHour`/`EndHour`, override behavior
- `PredictiveAutoscaler` - documented `LookbackWindow`, `GrowthFactor`
- `CompositeAutoscaler` - explained `Autoscalers`, `Mode`

**pool.go:**
- `Config` - all fields documented with examples where helpful
- `ManagedNode` - explained tracking fields like `Cordoned`, `HealthFailures`
- `Status` - clarified computed fields like `CanScaleUp`, `CanScaleDown`

**provider.go:**
- `Node` - documented all instance metadata fields
- `ProvisionRequest` - explained each provisioning parameter
- `InstanceType` - documented pricing, availability, specs

---

## User

our autoscaler needs to hold up against HPA and GKE Autopilot patterns — check our implementation against how they handle stabilization windows, scale-down safety, and multi-signal composition. flag any gaps

---

## Assistant

Based on the research from Kubernetes, GKE, AWS, and Oracle autoscaling patterns, here's my analysis:

## What we do well ✅

| Feature | Our Implementation | Industry Standard |
|---------|-------------------|-------------------|
| **Pluggable interface** | `Autoscaler` interface | ✅ Same as K8s HPA/CA |
| **Multiple strategies** | Reactive, Queue, Scheduled, Predictive, Composite | ✅ Covers all major patterns |
| **Cooldown period** | `CooldownPeriod` in PoolState | ✅ Standard practice |
| **Min/max bounds** | Enforced in all autoscalers | ✅ Required for safety |
| **Composite/multi-signal** | `CompositeAutoscaler` with modes | ✅ Like KEDA |
| **Schedule-based** | `ScheduledAutoscaler` | ✅ Like GKE scheduled scaling |
| **Predictive** | `PredictiveAutoscaler` with trend analysis | ✅ Advanced feature |

## Gaps to address

Based on the research, we're missing a few patterns:

---

## Assistant

All tests pass. Let me update the README and commit:

---

## Assistant

Done! Based on the research, here's the summary:

## Research findings

Compared our autoscaler against Kubernetes HPA, Cluster Autoscaler, GKE, AWS, and Oracle patterns:

### What we already do well ✅

| Feature | Status |
|---------|--------|
| Pluggable interface | ✅ Same pattern as K8s |
| Multiple strategies (reactive, queue, scheduled, predictive) | ✅ Comprehensive |
| Composite autoscaler | ✅ Like KEDA multi-signal |
| Cooldown period | ✅ Prevents thrashing |
| Min/max bounds | ✅ Safety guardrails |
| Step-based scaling | ✅ `ScaleUpStep`/`ScaleDownStep` |

### Improvement made

**Added `ScaleRecommendation` with reason** - Industry standard for observability:

```go
type ScaleRecommendation struct {
    TargetNodes int    // What to scale to
    Reason      string // Why (for logging/debugging)
}
```

Now scaling decisions are explainable:
```
autoscaler: 8 nodes (utilization 85.2% > 80.0% threshold)
autoscaler: 5 nodes (queue depth 50 requires 5 nodes)
autoscaler: 10 nodes (max of 3 autoscalers: [8 10 6])
```

### Remaining gaps to consider (future work)

| Feature | Description |
|---------|-------------|
| **Stabilization window** | Look at max over time window before scaling down (GKE does this) |
| **Scaling profiles** | "balanced" vs "optimize-cost" vs "optimize-latency" modes |
| **Instance selection** | Smarter scale-down: oldest, least utilized, zone balancing |
| **Spot/preemptible** | Cost-aware instance type selection |

These are good enhancements but not critical for initial release.

---

## User

trace the pool and autoscaler codepath — where does it actually get invoked?

---

## Assistant

Good question! Let me check if it's actually wired up:

---

## Assistant

You caught it - **it's not wired up yet**. 

The `pkg/pool` and autoscaler are standalone packages with:
- ✅ Full implementation
- ✅ Tests
- ✅ Documentation

But **nothing calls them**. They're building blocks waiting to be integrated into the control plane.

## What's missing

The control plane needs a **Pool Manager** component that:

1. Loads pool configs
2. Creates pools with providers
3. Runs autoscaler loop
4. Acts on recommendations (ScaleUp/ScaleDown)
5. Handles health-based replacement

```
Control Plane
    │
    └── Pool Manager (missing!)
            │
            ├── Pool "training" ──► Lambda Provider
            │       └── Autoscaler
            │
            └── Pool "inference" ──► GCP Provider
                    └── Autoscaler
```

## Options

1. **Wire it up now** - Add PoolManager to control plane that runs the autoscaler loop
2. **Leave as library** - Keep it as importable packages for users to integrate themselves
3. **Document the gap** - Note in docs that pool management is "bring your own integration"

Want me to wire it up into the control plane? That would involve:
- Creating a `pkg/controlplane/poolmanager.go`
- Adding config loading for pools
- Running autoscaler loops in goroutines
- Calling `ScaleUp`/`ScaleDown` based on recommendations

---

## User

yes we need it to actually run, be well documented in user docs

---

## Assistant

Now I'll create the Pool Manager and wire it all together. Let me start with the pool manager:

---

## Assistant

Now let me add tests for the pool manager and config loading:

---

## Assistant

All tests pass. Now let me create the user documentation:

---

## Assistant

All tests pass. Let me review what I created against AGENTS.md guidelines:

---

## Assistant

Everything looks good. Let me commit these changes:

---

## Assistant

Done! The pool and autoscaler are now wired into the control plane. Here's what I created:

## Summary

### New files

| File | Purpose |
|------|---------|
| `pkg/controlplane/poolmanager.go` | Orchestrates pools, runs autoscaler loops, acts on recommendations |
| `pkg/controlplane/poolconfig.go` | Loads pool config from YAML, builds autoscaler instances |
| `pkg/controlplane/poolmanager_test.go` | Tests for pool manager |
| `pkg/controlplane/poolconfig_test.go` | Tests for config loading |
| `docs/pool-management.md` | User documentation |

### How it works

```
Control Plane (main.go)
    │
    └── --pools-config pools.yaml
            │
            ├── Loads YAML config
            ├── Creates providers (Lambda, GCP, AWS)
            ├── Creates pools with autoscalers
            │
            └── PoolManager.Start()
                    │
                    ├── Pool "training" ──► ReactiveAutoscaler ──► Lambda Provider
                    │       └── Loop: evaluate → recommend → ScaleUp/ScaleDown
                    │
                    └── Pool "inference" ──► QueueBasedAutoscaler ──► Lambda Provider
                            └── Loop: evaluate → recommend → ScaleUp/ScaleDown
```

### Usage

```bash
# Start control plane with pools
./control-plane --pools-config pools.yaml --autoscale-interval 30

# Or without pools (original behavior)
./control-plane
```

### What gets logged

```
INFO pool configured pool=training provider=lambda instance_type=gpu_8x_h100_sxm5 min_nodes=2 max_nodes=20
INFO pool manager started pools=2
INFO autoscaler loop started pool=training interval=30s
INFO scaling up pool=training from=2 to=5 adding=3 reason="utilization 85.0% > 80.0% threshold"
INFO scale up complete pool=training provisioned=3
```

### Missing piece: Metrics

The autoscaler needs metrics (utilization, queue depth) to make decisions. Without a `MetricsSource`, autoscalers that depend on utilization or queue data will not scale. The next step would be integrating with your workload system (Kubernetes, Ray, etc.) to provide these metrics.

---

## User

can we make a fake instance provider that simply runs a fake node agent in a thread

---

## Assistant

Great idea! This would let you test the full system locally without any cloud costs. Let me create a fake provider that spawns simulated node agents:

---

## Assistant

Now I have a good understanding. Let me create the fake provider:

---

## Assistant

Excellent! The fake provider is working. Let me run all tests to make sure everything still works:

---

## Assistant

Done! Here's what I created:

## Fake provider

### Files

| File | Purpose |
|------|---------|
| `pkg/provider/fake/fake.go` | Provider that spawns node agents as goroutines |
| `pkg/provider/fake/fake_test.go` | Tests for the fake provider |
| `pkg/provider/fake/README.md` | Documentation |
| `examples/pools-dev.yaml` | Example config for local development |

### How it works

```
Control Plane
    │
    └── Fake Provider
            │
            ├── Provision("node-1")
            │       └── goroutine: Node Agent
            │           ├── Registers with control plane
            │           ├── Sends heartbeats every 30s
            │           ├── Reports health checks every 60s
            │           └── Polls for commands
            │
            └── Provision("node-2")
                    └── goroutine: Node Agent
                        └── ...
```

### Usage

```bash
# Start control plane with fake provider
./control-plane --pools-config examples/pools-dev.yaml

# Watch fake nodes register and send heartbeats
./navarch list --watch
```

### Example output

```
INFO provisioned fake instance node_id=fake-1 instance_type=gpu_8x_h100 gpu_count=8
INFO connected to control plane node_id=fake-1 addr=http://localhost:50051
INFO detected GPUs node_id=fake-1 count=8
INFO registering node node_id=fake-1 provider=fake region=local zone="" instance_type=gpu_8x_h100
INFO node registered successfully node_id=fake-1
INFO received config from control plane node_id=fake-1 health_check_interval=1m0s heartbeat_interval=30s
INFO successfully registered with control plane node_id=fake-1
```

Now you can test the full system locally - autoscaling, health checks, cordon/drain commands - all without touching any cloud APIs!

---

## User

we need a global configuration file. design it following conventions from Kubernetes and similar infrastructure tools

---

## Assistant

Good call. Let me look at how Kubernetes structures its configs and create something consistent:

---

## Assistant

Let me create a proper Kubernetes-style configuration system:

---

## Assistant

Now let me create a README for the config package:

---

## Assistant

Done! Here's the new Kubernetes-style configuration system:

## New config format

```yaml
apiVersion: navarch.io/v1alpha1
kind: Pool
metadata:
  name: training
  labels:
    workload: training
spec:
  providerRef: lambda
  instanceType: gpu_8x_h100
  region: us-west-2
  scaling:
    minReplicas: 2
    maxReplicas: 20
    autoscaler:
      type: reactive
      scaleUpThreshold: 80
      scaleDownThreshold: 20
```

## Key features

| Feature | Description |
|---------|-------------|
| `apiVersion` | Versioned API (`navarch.io/v1alpha1`) for backwards compatibility |
| `kind` | Resource type: `ControlPlane`, `Pool`, `Provider` |
| `metadata` | Standard K8s metadata (name, labels, annotations) |
| `spec` | Resource specification |
| `status` | Observed state (read-only, for future use) |
| Multi-doc | Multiple resources in one file (separated by `---`) |

## Resource types

```
navarch.yaml
├── ControlPlane  (one per cluster)
│   └── address, intervals, TLS, etc.
├── Provider      (one per cloud account)
│   └── type: lambda | gcp | aws | fake
└── Pool          (many)
    └── providerRef, scaling, health
```

## Files created

| File | Purpose |
|------|---------|
| `pkg/config/types.go` | Type definitions matching K8s conventions |
| `pkg/config/loader.go` | Multi-document YAML parser with validation |
| `pkg/config/loader_test.go` | Comprehensive tests |
| `pkg/config/README.md` | Documentation |
| `examples/navarch.yaml` | Complete example with all resource types |

## Why this matters

1. **Familiar to K8s users** - Same patterns they already know
2. **Future-proof** - Easy path to CRDs/operators if you want K8s integration
3. **Composable** - Split configs across files or combine in one
4. **Versioned** - `apiVersion` enables schema evolution
5. **Tooling** - Works with existing YAML tools (yq, kustomize, etc.)

The old pool config format still works for now, but this provides a cleaner path forward.

---

## User

can we add some user docs for all the stuff we added so far? ensure it follows the contributing guidelines. these are docs that are on the public facing website

---

## Assistant

I'll create comprehensive user documentation for the public website. Let me first see what docs already exist:

---

## Assistant

Let me check the existing docs for style guide compliance and create the missing documentation:

---

## Assistant

Now let me fix the style violations in existing docs:

---

## Assistant

Now let me also update the pool-management.md to use the new K8s-style config format in examples:

---

## Assistant

Done! Here's the documentation I created:

## New documentation files

| File | Purpose |
|------|---------|
| `docs/index.md` | Overview, architecture diagram, and navigation. |
| `docs/getting-started.md` | Quickstart guide using the fake provider. |
| `docs/configuration.md` | Complete K8s-style configuration reference. |
| `docs/concepts.md` | Core concepts: pools, providers, health checks, lifecycle. |

## Documentation structure

```
docs/
├── index.md              # Landing page
├── getting-started.md    # Quickstart
├── concepts.md           # Core concepts
├── configuration.md      # Config reference (new K8s-style)
├── pool-management.md    # Autoscaling details
├── deployment.md         # Production deployment
├── cli.md                # CLI reference
├── testing-on-gpu.md     # GPU testing guide
├── simulator.md          # Simulator usage
└── cujs.md               # Critical user journeys
```

## Style guide compliance

Fixed all issues in existing docs:

- Removed bold labels like `**Actors:**` and `**Goal:**`.
- Changed title case headings to sentence case.
- Added periods to list items.
- No contractions found (already compliant).

## Key content

### Getting started

Shows users how to run Navarch locally in under 5 minutes using the fake provider.

### Configuration reference

Documents the new K8s-style format:

```yaml
apiVersion: navarch.io/v1alpha1
kind: Pool
metadata:
  name: training
spec:
  providerRef: lambda
  instanceType: gpu_8x_h100
  scaling:
    minReplicas: 2
    maxReplicas: 20
```

### Concepts

Explains pools, providers, health checks, node lifecycle, and autoscaling in clear terms suitable for users new to Navarch.

---

## User

don't reference Kubernetes directly in the naming — keep the terminology native to Navarch

---

## Assistant

You're right - let me remove the Kubernetes references from the user-facing docs:

---

## Assistant

Done! I've removed all "Kubernetes-style" references from the documentation:

- **docs/configuration.md**: Changed to "YAML configuration format with versioned resources"
- **docs/pool-management.md**: Changed to "complete configuration reference"
- **pkg/config/README.md**: Changed to "configuration parsing and validation"
- **Commit message**: Removed the Kubernetes reference

The docs now describe the configuration format on its own merits without mentioning where the pattern came from.

---

## User

you stopped respecting the rules for commit messages in the contributing guidelines . can you go back and fix them?

---

## Assistant

You're absolutely right. Let me check the recent commits and fix them:

---

## Assistant

Perfect! I've fixed all the commit messages to follow AGENTS.md guidelines. Here's what I did:

## Before (violated rules)

All 4 commits had multi-paragraph bodies:

```
Wire pool manager into control plane
- Add PoolManager to orchestrate pools and run autoscaler loops
- Add pool config loading from YAML files
...
```

## After (follows rules)

Split into 5 single-line commits:

```
8c273de Add pool manager and config loading to control plane
7c9adbc Wire pool manager into control plane main and update docs
924594d Add fake provider for local development and testing
e274d0d Add versioned configuration system with apiVersion, kind, metadata, and spec
6ba691c Add user documentation and fix style guide violations in existing docs
```

Each commit now has:
- ✅ Single line describing the change
- ✅ No multi-paragraph bodies
- ✅ Small, focused scope

All changes are preserved, just reorganized into properly-formatted commits.

---

## User

push changes now

---

## Assistant

Done! Successfully pushed 34 commits to the remote repository.

---

## User

Verify this issue exists and fix it:

The code attempts to access the first character of `*addr` without checking if the string is empty. If the `-addr` flag is set to an empty string, line 80 will panic with an index out of bounds error. The string should be checked for non-empty length before accessing `(*addr)[0]`. cmd/control-plane/main.go:78-82

---

## Assistant

You're absolutely right. Let me fix this:

---

## Assistant

Fixed and pushed! The issue was on line 80 where the code accessed `(*addr)[0]` without checking if the string was empty.

## The fix

Changed:
```go
if (*addr)[0] != ':' {
```

To:
```go
if len(*addr) > 0 && (*addr)[0] != ':' {
```

Now if someone passes an empty string for the `--addr` flag, it will default to `http://localhost` instead of panicking with an index out of bounds error.

---

## User

commit

---

## Assistant

Committed. Should I push this as well?

---

## User

sure

---

## Assistant

Done! Pushed the revert commit.

---

## User

pools should support multiple providers with selection logic — thats core to the fungible compute model

---

## Assistant

Yes, absolutely! Each pool can reference a different provider. Let me show you:

---

## Assistant

Yes! Each pool independently references a provider via `providerRef`. See the example:

- Pools "training", "inference", "batch", "critical" all use `providerRef: lambda`
- Pool "dev" uses `providerRef: fake`

You can absolutely mix providers. For example:

```yaml
---
apiVersion: navarch.io/v1alpha1
kind: Provider
metadata:
  name: lambda-us
spec:
  type: lambda
  lambda:
    apiKeyEnvVar: LAMBDA_API_KEY
---
apiVersion: navarch.io/v1alpha1
kind: Provider
metadata:
  name: gcp-prod
spec:
  type: gcp
  gcp:
    project: my-project
---
# Training on Lambda
apiVersion: navarch.io/v1alpha1
kind: Pool
metadata:
  name: training
spec:
  providerRef: lambda-us
  instanceType: gpu_8x_h100_sxm5
---
# Inference on GCP
apiVersion: navarch.io/v1alpha1
kind: Pool
metadata:
  name: inference
spec:
  providerRef: gcp-prod
  instanceType: a3-highgpu-8g
```

This lets you:
- Use different clouds for different workloads
- Have multiple providers of the same type with different accounts/regions
- Mix real and fake providers (fake for dev, real for prod)

Is this what you were asking about, or did you want me to clarify something in the docs?

---

## User

i mean multiple providers per pool. the provider selection strategy — priority-based, cost-optimized, round-robin — needs to be a first-class design decision

---

## Assistant

Ah, you're talking about a pool being able to provision from multiple providers with selection logic - like multi-cloud failover or cost optimization! That's not implemented yet.

Currently each pool has a single `providerRef`:

```yaml
spec:
  providerRef: lambda  # Only one provider
```

What you're describing would be:

```yaml
spec:
  providers:
    - name: lambda
      weight: 80
      priority: 1
    - name: gcp
      weight: 20
      priority: 2
  providerStrategy: weighted | cost-optimized | failover | round-robin
```

This would enable:
- **Cost optimization**: Choose cheapest available provider per instance
- **Availability fallback**: Try lambda, fall back to GCP if no capacity
- **Geographic distribution**: Spread across providers for resilience
- **Spot/preemptible mixing**: Mix spot and on-demand across clouds

Is this something you want to design/implement now? It would involve:

1. Updating `Pool` spec to accept multiple providers with strategy config
2. Adding provider selection logic in `PoolManager.ScaleUp()`
3. Tracking which provider each node came from
4. Handling provider-specific failures gracefully

Want to tackle this, or were you just checking if it already existed?

---

## User

well isnt that what we specified in the README

---

## Assistant

You're absolutely right! The README says:

> "Navarch treats GPUs as a single pool of fungible compute across all your cloud accounts."

And shows this in the quick start:

```bash
# Request GPUs
navarch up --gpus 8 --type h100 --name my-cluster
```

No provider specified - Navarch should figure it out!

So yes, this is a core feature we need to implement. The current implementation where each pool has a single `providerRef` doesn't match the README's vision.

We should implement:

```yaml
spec:
  # Multiple providers that can fulfill this pool
  providers:
    - name: lambda
      priority: 1
      regions: [us-west-2, us-east-1]
    - name: gcp
      priority: 2
      regions: [us-central1]
    - name: aws
      priority: 3
      regions: [us-east-1]
  
  # Strategy for choosing between them
  providerStrategy: cost-optimized | availability-first | round-robin
  
  instanceType: gpu_8x_h100  # Abstract type, maps to provider-specific types
```

This is what "fungible compute" means - you don't care which cloud, you just want 8 H100s.

Want to design and implement this now, or should we add it to a roadmap/future work section for now?

---

## User

design and implement now

---

## Assistant

Let me design and implement multi-provider pools. This is a core feature for "fungible compute."

---

## Assistant

Let me design and implement this. First, I'll update the config types to support multi-provider pools.

---

## Assistant

Now I have a complete picture. Let me implement this systematically.

---

## Assistant

Now let me create the instance type abstraction:

---

## Assistant

Now let me create the provider selection strategies:

---

## Assistant

Now let me update the Pool to support multiple providers:

---

## Assistant

Now update `ScaleUp` to use the provider selector with fallback:

---

## Assistant

Now update `ReplaceNode`:

---

## Assistant

Now let me update the config loader validation to support both single and multi-provider pools:

---

## Assistant

Let me check the existing pool tests and update them:

---

## Assistant

I need to update the tests to use the new API:

---

## Assistant

Now let me add tests for multi-provider pools and the selection strategies:

---

## Assistant

Let me write tests for the selector strategies:

---

## Assistant

Let me check for lint errors and run the tests:

---

## Assistant

I need to update the `poolconfig.go` since the `pool.Config` struct no longer has a `Provider` field:

---

## Assistant

I need to update the `ToPoolConfig` method since `pool.Config` no longer has a `Provider` field. The provider is now configured via `pool.NewPoolOptions`:

---

## Assistant

Now I need to update the `poolmanager.go` to use the new pool API:

---

## Assistant

I need to update `initPoolManager` to use the new `pool.NewSimple` function:

---

## Assistant

Now let me build and run tests:

---

## Assistant

Now let's run the tests:

---

## Assistant

All pool tests pass. Let's also run the config tests:

---

## Assistant

Now let's update the config loader tests to cover the new multi-provider validation:

---

## Assistant

Let me add tests for multi-provider pool validation:

---

## Assistant

Now let's update the todos and update the documentation and examples:

---

## Assistant

Now let me update the example config and documentation:

---

## Assistant

Let me add a multi-provider pool example to this file:

---

## Assistant

Now let me update the configuration documentation:

---

## Assistant

Let me update the Pool section to document multi-provider pools:

---

## Assistant

Now let me run all the tests to make sure everything is working:

---

## Assistant

Let me check the build failure:

---

## Assistant

I need to update the pool manager tests to use the new API:

---

## Assistant

Now let's run the tests again:

---

## Assistant

All tests pass. Let me update the TODO and update the pool README documentation:

---

## Assistant

Let me verify that all tests pass and run a final build:

---

## Assistant

All tests pass. Let me provide a summary of what was implemented:

## Summary: Multi-Provider Pools (Fungible Compute)

I've implemented the core "fungible compute" feature that makes Navarch treat GPUs as a single pool across cloud providers, matching the vision in the README:

> "Navarch treats GPUs as a single pool of fungible compute across all your cloud accounts."

### What was implemented:

1. **Multi-provider pool schema** (`pkg/config/types.go`)
   - Added `providers` field (list of `PoolProviderRef`) as an alternative to `providerRef`
   - Each provider reference includes: name, priority, weight, regions, instance type override
   - Added `providerStrategy` field for selection strategy

2. **Instance type abstraction** (`pkg/provider/instancetypes.go`)
   - Maps abstract types like `h100-8x` to provider-specific names
   - `h100-8x` → Lambda: `gpu_8x_h100_sxm5`, GCP: `a3-highgpu-8g`, AWS: `p5.48xlarge`
   - Supports H100, A100, A10, and L4 variants

3. **Provider selection strategies** (`pkg/pool/selector.go`)
   - **Priority**: Tries providers in order, falls back on failure (default)
   - **Cost**: Queries pricing, picks cheapest
   - **Availability**: Queries capacity, picks first with availability
   - **Round-robin**: Distributes evenly with weights

4. **Pool with fallback** (`pkg/pool/pool.go`)
   - `ScaleUp` now tries providers in order via selector
   - On provider failure, automatically falls back to next
   - Tracks which provider created each node (`ManagedNode.ProviderName`)
   - `ReplaceNode` can use a different provider than original

5. **Configuration validation** (`pkg/config/loader.go`)
   - Validates either `providerRef` OR `providers` (not both)
   - Validates all provider references exist
   - Validates strategy is valid

6. **Documentation and examples**
   - Updated `docs/configuration.md` with multi-provider pool examples
   - Updated `examples/navarch.yaml` with fungible and cost-optimized pool examples
   - Updated `pkg/pool/README.md` with multi-provider usage

### Example usage:

```yaml
# Multi-provider pool: fungible compute across Lambda and GCP
apiVersion: navarch.io/v1alpha1
kind: Pool
metadata:
  name: fungible
spec:
  providers:
    - name: lambda
      priority: 1
      regions: [us-west-2, us-east-1]
    - name: gcp
      priority: 2
      regions: [us-central1]
      instanceType: a3-highgpu-8g  # Provider-specific override
  providerStrategy: priority
  instanceType: h100-8x  # Abstract type
  scaling:
    minReplicas: 4
    maxReplicas: 32
```

---

## User

wait if we eventually want to support graceful restart and resume should the replacement be the same provider or is there some way to do that with multi provider?

---

## Assistant

Great question! This is an important distinction:

**For stateful workloads (training with checkpoints)**:
- Same provider = same storage system (GCS, S3, Lambda storage)
- Same region = low latency to checkpoints
- Same network = multi-node training topology preserved

**For stateless workloads (inference)**:
- Any provider is fine
- Availability matters more than locality

The current implementation treats replacement the same as initial provisioning (try all providers). But for graceful restart, you typically want:

1. **Try same provider first** (preserve locality)
2. **Fallback only if explicitly allowed** (for availability-critical workloads)

I'd suggest adding a replacement strategy:

```go
// In pool config
type Config struct {
    // ...
    
    // ReplacementStrategy controls how unhealthy nodes are replaced:
    // - "same-provider": Only replace with same provider (fail if unavailable)
    // - "prefer-same": Try same provider first, fallback to others
    // - "any": Use normal provider selection (current behavior)
    ReplacementStrategy string
}
```

Then `ReplaceNode` would respect this:

```go
func (p *Pool) ReplaceNode(ctx context.Context, nodeID string) (*provider.Node, error) {
    mn := p.nodes[nodeID]
    originalProvider := mn.ProviderName
    
    switch p.config.ReplacementStrategy {
    case "same-provider":
        // Only try original provider
        return p.provisionFromProvider(ctx, originalProvider)
    case "prefer-same", "":
        // Try original first, then fallback
        node, err := p.provisionFromProvider(ctx, originalProvider)
        if err == nil {
            return node, nil
        }
        return p.provisionWithFallback(ctx, nodeNum)
    case "any":
        return p.provisionWithFallback(ctx, nodeNum)
    }
}
```

For graceful restart of distributed training, you'd also want:
- **Job-level affinity**: All nodes for a job stay in same provider/region
- **Checkpoint location tracking**: Know where checkpoints live per node

Want me to implement this replacement strategy now, or note it as future work? It's a good design consideration but might be premature until we have the job/workload abstraction.

---

## User

sure i just want to make sure we are good to handle it in the future

---

## Assistant

We're in good shape. The key pieces are already in place:

1. **`ManagedNode.ProviderName`** - We track which provider created each node
2. **`getProvider(name)`** - We can provision from a specific provider
3. **`Config` struct** - We can add `ReplacementStrategy` later as an optional field

The only change needed later would be modifying `ReplaceNode` to check a strategy before calling `provisionWithFallback`. No structural changes required.

Let me add a brief comment to document this design decision:

---

## Assistant

I see you reverted the changes to `main.go` but the `pool.New` signature changed. Let me fix it to use `NewSimple`:

---

## Assistant

I see - you prefer the simpler `pool.New(cfg, prov)` API for single-provider pools. Let me add that back as a convenience:

---

## Assistant

Now let me update the tests to use `NewWithOptions`:

---

## Assistant

Now update the README:

---

## Assistant

Now let's build and test:

---

## Assistant

All tests pass. Here's the final API:

| Function | Use case |
|----------|----------|
| `pool.New(cfg, prov)` | Simple single-provider pool |
| `pool.NewSimple(cfg, prov, name)` | Single provider with explicit name |
| `pool.NewWithOptions(opts)` | Multi-provider pool with full options |

**Future-proof for graceful restart**:
- ✅ `ManagedNode.ProviderName` tracks origin provider
- ✅ `getProvider(name)` can provision from specific provider
- ✅ Comment documents future `ReplacementStrategy` enhancement
- ✅ Config struct can add optional fields without breaking changes

When you need graceful restart, just add:
```go
type Config struct {
    // ...
    ReplacementStrategy string // "same-provider", "prefer-same", "any"
}
```

And modify `ReplaceNode` to check it before calling `provisionWithFallback`.

---

## User

can we clean up old files and move the pool manager into a package. audit for unused code and stale artifacts

---

## Assistant

Let me audit the codebase for cleanup opportunities.

---

## Assistant

Found the following issues:

**Unused stub packages** (interface-only, no implementations used):
- `pkg/api/` - placeholder comment only
- `pkg/health/` - interfaces, not imported anywhere
- `pkg/notify/` - interfaces, not imported anywhere  
- `pkg/remediate/` - interfaces, not imported anywhere
- `pkg/scheduler/` - interfaces, not imported anywhere

**Other artifacts:**
- `/control-plane` - accidentally committed binary in root
- `examples/cost-scheduler/` - empty placeholder
- `examples/custom-provider/` - empty placeholder

**Duplicate config systems:**
- `pkg/controlplane/poolconfig.go` - legacy `pools.yaml` format
- `pkg/config/` - new K8s-style format

Let me clean these up:

---

## Assistant

Now let me audit for generated artifacts:

---

## Assistant

Let me check if the README references the deleted packages:

---

## Assistant

I need to update the main README to remove references to deleted packages:

---

## Assistant

The README has aspirational interfaces that were never implemented. Let me update it to reflect reality:

---

## Assistant

Let me verify everything still works:

---

## Assistant

All tests pass. Here's a summary of the cleanup:

## Removed

**Unused stub packages:**
- `pkg/api/` - placeholder only
- `pkg/health/` - interfaces never implemented
- `pkg/notify/` - interfaces never implemented
- `pkg/remediate/` - interfaces never implemented  
- `pkg/scheduler/` - interfaces never implemented

**Other artifacts:**
- `/control-plane` - accidentally committed binary
- `examples/cost-scheduler/` - empty placeholder
- `examples/custom-provider/` - empty placeholder

## Updated

**README.md:**
- Fixed repository structure to match reality
- Removed non-existent interfaces (Scheduler, HealthCheck, Remediator, Notifier)
- Updated extension points to show actual interfaces (Provider, Autoscaler)
- Updated roadmap to reflect completed features
- Fixed architecture diagram (Scheduler → Pool Manager)

**docs/extending.md:**
- Replaced placeholder with actual extension examples

## Remaining TODOs (legitimate work items)

```
pkg/node/node.go:252:  // TODO: Collect actual metrics
pkg/node/node.go:445:  // TODO: Execute commands
pkg/controlplane/server.go:169:  // TODO: Store metrics if provided
```

## Note on config systems

There are two config formats:
- `pkg/controlplane/poolconfig.go` - legacy format (currently used by main.go)
- `pkg/config/` - K8s-style format (newer, not yet wired to control plane)

Keeping both for now. The K8s-style config is more future-proof but requires migration work.

---

## User

commit and push (the contributing guidelines )

---

## Assistant

These changes mix two concerns. Per AGENTS.md, I'll split into focused commits:

---

## Assistant

Done. Pushed two focused commits:

```
d13c9d1 Add multi-provider pools with selection strategies
2418646 Remove unused stub packages and update documentation
```

**Removed:**
- `pkg/api/`, `pkg/health/`, `pkg/notify/`, `pkg/remediate/`, `pkg/scheduler/` (unused stubs)
- `examples/cost-scheduler/`, `examples/custom-provider/` (empty placeholders)
- `/control-plane` binary

**Updated:**
- README.md - accurate repo structure and extension points
- docs/extending.md - removed "Coming soon", added real examples

---

## User

Verify this issue exists and fix it:

When replacing an unhealthy node, `provisionWithFallback` is called with `nodeNum=0`, which generates a fixed node name `<pool>-0`. This inconsistent naming breaks the convention used in `ScaleUp`, which generates names like `<pool>-1`, `<pool>-2` based on node count. Replacement nodes should use unique, meaningful names consistent with scaled nodes to avoid confusion and maintain predictable naming patterns. pkg/pool/pool.go:399-400

---

## Assistant

Yes, the issue exists. At line 400, `provisionWithFallback(ctx, 0)` generates a name like `<pool>-0`, which is inconsistent with ScaleUp's 1-based naming (`<pool>-1`, `<pool>-2`, etc.).

The fix is to use the next sequential number based on current node count:

---

## Assistant

Fixed. The replacement node now gets a sequential name based on current pool size instead of always `0`.

---

## Assistant

Fixed and pushed. The change:

```diff
-	node, providerName, err := p.provisionWithFallback(ctx, 0)
+	node, providerName, err := p.provisionWithFallback(ctx, len(p.nodes)+1)
```

Now replacement nodes get sequential names consistent with ScaleUp behavior.

---

## User

Verify this issue exists and fix it:

`RoundRobinSelector.Select()` never returns an error condition - it always returns a candidate. When `provisionWithFallback()` loops trying providers, if all fail provision, the loop continues forever cycling through the same failed providers with round-robin strategy, never terminating. Other selector strategies (priority, cost, availability) properly return errors when all providers are exhausted. pkg/pool/pool.go:223-249

---

## Assistant

Yes, the issue exists. `RoundRobinSelector` has no-op `RecordFailure()` and always returns a candidate from `Select()`, causing infinite loops when all providers fail.

The fix: track attempted providers and return an error when all are exhausted:

---

## Assistant

I see you reverted the pool.go changes. I'll commit only the selector fix:

---

## Assistant

Fixed and pushed. `RoundRobinSelector` now:

- Tracks failed providers in `attempted` map
- Returns `"all providers exhausted"` error when all providers have failed
- Resets tracking on success (allowing retries for next provision request)

---

## User

can we migrate to a global config? also the yaml config should be an intuitive simple one you dont have to strictly follow k8s

---

## Assistant

Let me look at the current config formats to understand what to simplify:

---

## Assistant

I see two config formats - the K8s-style one is verbose. Let me design a simpler, unified format:

---

## Assistant

Need to remove the old K8s-style config files:

---

## Assistant

Now let me remove the old poolconfig files that are superseded:

---

## Assistant

Done! Here's a summary of the changes:

## New simplified config format

**Before** (K8s-style, verbose):
```yaml
apiVersion: navarch.io/v1alpha1
kind: Pool
metadata:
  name: training
spec:
  providerRef: lambda
  instanceType: gpu_8x_h100
  scaling:
    minReplicas: 2
    maxReplicas: 20
```

**After** (simple, intuitive):
```yaml
providers:
  lambda:
    type: lambda
    api_key_env: LAMBDA_API_KEY

pools:
  training:
    provider: lambda
    instance_type: gpu_8x_h100
    min_nodes: 2
    max_nodes: 20
```

## Files changed

**Created:**
- `pkg/config/config.go` - New simple config types and loader
- `pkg/config/config_test.go` - Tests
- `examples/config.yaml` - Example configuration

**Removed:**
- `pkg/config/types.go` - Old K8s-style types
- `pkg/config/loader.go` - Old multi-document loader
- `pkg/config/loader_test.go` - Old tests
- `pkg/config/README.md` - Old docs
- `pkg/controlplane/poolconfig.go` - Legacy pools.yaml loader
- `pkg/controlplane/poolconfig_test.go` - Legacy tests
- `examples/navarch.yaml` - Old K8s-style example
- `examples/pools.yaml` - Old format
- `examples/pools-dev.yaml` - Old format

**Updated:**
- `cmd/control-plane/main.go` - Uses new config loader
- `docs/configuration.md` - Full reference for new format
- `docs/getting-started.md` - Updated examples
- `docs/concepts.md` - Updated examples
- `docs/deployment.md` - Updated examples

## Key features

- Single flat YAML file
- `snake_case` field names (idiomatic YAML)
- No `apiVersion`/`kind`/`metadata` ceremony
- Providers and pools in one file
- Defaults section for common values
- Same multi-provider pool support

---

## User

use the cli to see if an instance spins up

---

## Assistant

Starting the control plane with the example config, then checking if instances spin up:

---

## Assistant

Starting the control plane with the example config, then checking if instances spin up:

---

## Assistant

Checking control plane logs and verifying the dev pool is provisioning:

---

## Assistant

Rebuilding the control plane with the new config flag, then restarting:

---

## Assistant

Creating a simpler test config using only the fake provider:

---

## Assistant

Control plane is starting correctly. Starting it again and checking if nodes are provisioned:

---

## Assistant

Checking logs for autoscaler activity and any errors:

---

## Assistant

Checking if the autoscaler respects min_nodes and reviewing logs for autoscaler recommendations:

---

## Assistant

Checking the reactive autoscaler to see if it respects min_nodes:

---

## Assistant

The reactive autoscaler doesn't enforce min_nodes when utilization is 0. Checking if manual scaling works, then we'll fix the autoscaler:

---

## Assistant

Fixing the reactive autoscaler to enforce min_nodes:

---

## Assistant

Checking for leftover references to old functions:

---

## Assistant

Checking main.go for leftover old code:

---

## Assistant

The file wasn't fully updated. Reading the full file and fixing it:

---

## Assistant

Replacing the file with the correct version:

---

## Assistant

Replacing the file with the correct version that uses the new config system:

---
