# Nirmal-1 Experiments & Ablation Directory

This directory tracks empirical runs, scaling studies, and architectural ablations for Nirmal-1.

## Experiment Protocol

1. **Deterministic Seeds**: All benchmarks and ablations must fix random seeds for `torch`, `numpy`, and Python's `random`.
2. **Logged Metrics**:
   - Training loss, validation perplexity, router auxiliary loss, and router z-loss.
   - Expert utilization entropy: $-\sum_{i=1}^E f_i \ln f_i$ to measure load balance.
   - Memory consumption (peak VRAM / RSS RAM).
   - Throughput (tokens/sec in training and autoregressive generation).
3. **Ablation Axes**:
   - DeltaNet recurrence vs. Pure Causal Attention (KV cache size & latency vs context length).
   - Full Attention Interval ($I_{attn} \in \{2, 4, 8, \infty\}$).
   - Number of Experts & Active Top-$k$ ($E=8, k=2$ vs. $E=16, k=2$ vs. Dense).
   - Key Normalization and Decay bounding in DeltaNet.
