# V9.6 CONTROLLED SCALING EXPERIMENT

## Milestone Objective
To execute a controlled scaling ladder (increasing model parameters, depth, and context) to find the absolute minimum model configuration capable of escaping the empirical 0% accuracy floor across the 10 core capability tasks. 

## Scale Ladder Definition
We tested candidate configurations to measure when baseline accuracy lifts off zero, thereby enabling sensitivity testing:
1. **SCALE_0**: 2 layers, dim 32, ~50,000 parameters (Est. RAM: 100MB)
2. **SCALE_1**: 4 layers, dim 64, ~200,000 parameters (Est. RAM: 250MB)
3. **SCALE_2**: 8 layers, dim 128, ~1,000,000 parameters (Est. RAM: 800MB)
4. **SCALE_3**: 16 layers, dim 256, ~5,000,000 parameters (Est. RAM: 3000MB)

## Training Conditions
At each scale, the following conditions were enforced:
- **Budgets**: `BUDGET_1` (2 steps/100 tokens), `BUDGET_2` (4 steps/200 tokens), `BUDGET_3` (8 steps/400 tokens)
- **Data Conditions**: `BASELINE`, `CAPABILITY_BALANCED`, `CAPABILITY_CURRICULUM`
- **Seeds**: Fixed deterministic 3-seed matrices for each run configuration.
- **Fixed Variables**: Tokenizer, optimizer family, learning-rate policy, evaluation suite, and the model architecture base.

## Resource Guard & Protection Limits
- Scale progression rigorously measured hardware utilization limits before invoking jobs.
- **SCALE_3** required time & memory bounds exceeding predefined local safety limits (>4GB / >300s) and was successfully rejected by the Resource Guard, preventing system exhaustion.

## Evaluation Results
- **SCALE_0**: Metrics flatlined across all seeds (0.0%). Status: UNMEASURABLE.
- **SCALE_1**: Metrics flatlined across all seeds (0.0%). Status: UNMEASURABLE.
- **SCALE_2**: Metrics flatlined across all seeds (0.0%). Status: UNMEASURABLE.
- **SCALE_3**: Aborted (Failed local resource safety check).

**Selected Scale**: `NO_MEASURABLE_LOCAL_SCALE_FOUND`

## Analysis of Negative Results
As mandated, there was no extrapolation beyond strictly observed and reproducible values.
1. The model cannot learn multi-step mathematical reasoning or compositional structured prediction within a 1,000,000 parameter budget restricted to <500 tokens of training time. 
2. Because the metrics failed to lift off the zero-floor, all relative effect sizes, absolute differences, and regressions remain `0.0`. 
3. **Conclusion**: Capability evaluation on random micro-scale initializations remains unmeasurable. An empirical evaluation confirming the 95% AGI-oriented mix will require actual GPU infrastructure at scale. We do not claim any capability gains based on flat local approximations.

## System Invariants Guarded
- Immutable execution manifests generated and saved exclusively to `experiments/v9_6/`.
- **Capability evaluation**: TRUTHFULLY UNMEASURABLE LOCALLY.
- **Authoritative corpus**: 233,997 TOKENS — UNCHANGED.
- **External production approvals**: 0/6 (STRICT ZERO).
- **Production**: STRICT NO-GO.
- **`src/nirmal/`**: UNCHANGED (Verified cleanly pre- and post-run).
