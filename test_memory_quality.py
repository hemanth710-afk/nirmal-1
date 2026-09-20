"""
Evaluation Suite: Semantic Memory Quality & Contradiction Resolution.

Tests:
1. Relevance precision calculation.
2. Contradiction detection, resolution, and versioning.
3. Outdated facts archiving and avoidance in retrieval.
4. MemoryQualityMetrics tracking across evolving facts.
"""

import time
import pytest
from nirmal.agent.memory.semantic import SemanticMemory


def test_contradiction_resolution_and_versioning():
    sem = SemanticMemory()

    # Store initial fact
    sem.add_fact(
        key="db_endpoint",
        content="primary.cluster.internal:5432",
        category="infrastructure",
        confidence=0.9,
    )
    assert len(sem.facts) == 1
    assert sem.facts["db_endpoint"].version == 1
    assert not sem.facts["db_endpoint"].is_outdated
    assert len(sem.outdated_facts) == 0

    # Store updated contradictory fact with same key
    sem.add_fact(
        key="db_endpoint",
        content="failover.cluster.internal:5432",
        category="infrastructure",
        confidence=0.95,
    )

    # Contradiction should be resolved
    assert len(sem.facts) == 1
    assert sem.facts["db_endpoint"].content == "failover.cluster.internal:5432"
    assert sem.facts["db_endpoint"].version == 2
    assert not sem.facts["db_endpoint"].is_outdated

    # Previous version archived
    assert len(sem.outdated_facts) == 1
    assert sem.outdated_facts[0].content == "primary.cluster.internal:5432"
    assert sem.outdated_facts[0].is_outdated is True


def test_retrieval_excludes_outdated_facts():
    sem = SemanticMemory()
    sem.add_fact(key="service_url", content="http://v1.api", confidence=0.8)
    sem.add_fact(key="service_url", content="http://v2.api", confidence=0.95)

    # Retrieval should return latest active fact
    results = sem.retrieve(query="service_url", top_k=5, include_outdated=False)
    assert len(results) == 1
    assert results[0].content == "http://v2.api"

    # With include_outdated=True, outdated facts are also accessible for historical audit
    all_results = sem.retrieve(query="service_url", top_k=5, include_outdated=True)
    assert len(all_results) == 2


def test_memory_quality_metrics():
    sem = SemanticMemory()
    sem.add_fact(key="gateway", content="gw-primary", confidence=0.9)
    sem.add_fact(key="gateway", content="gw-secondary", confidence=0.9)  # 1 contradiction resolved
    sem.add_fact(key="timeout", content="30s", confidence=0.85)

    metrics = sem.compute_metrics(sample_queries=["gateway", "timeout", "unrelated"])
    assert metrics.total_facts == 2
    assert metrics.outdated_facts == 1
    assert metrics.contradiction_resolution_rate == 1.0
    assert metrics.outdated_error_rate == 0.0
    assert metrics.relevance_precision >= 0.5
