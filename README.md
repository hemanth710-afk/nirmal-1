# Nirmal-1 Final Capability Benchmark Evaluation Holdout

**Classification**: STRICT ISOLATION / ACCESS-CONTROLLED  
**Milestone**: V8.2+ Capability Evaluation Holdout  

---

## Security & Leakage Prevention Protocol

This directory serves as the protected boundary for final evaluation metadata, evaluation prompt seeds, and benchmark ground-truth references.

### Invariants Enforced:
1. **Zero Pretraining Exposure**: Zero files in this directory are permitted to enter the data loading pipeline, tokenizer training corpora, or pretraining shards.
2. **Zero Symbolic Leakage**: Test entities, questions, and reference answers are cryptographically hashed using SHA-256 and verified against the pretraining corpus before training launches.
3. **Restricted Access**: Benchmark answers and evaluation seeds are maintained in encrypted / checksum-locked archives during active model development.
4. **Single-Shot Evaluation**: The final held-out capability test suite is evaluated strictly once post-training. It is never used for validation, early stopping, or hyperparameter selection.
