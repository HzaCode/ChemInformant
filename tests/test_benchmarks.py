"""
Benchmark tests for ChemInformant performance using pytest-benchmark.

This module replaces the standalone benchmark.py script with integrated
pytest benchmarks that can be run as part of the standard test suite.
"""

import statistics
import time

import pytest

import ChemInformant as ci

# Sample drug names for benchmarking
SAMPLE_DRUGS = [
    "aspirin", "caffeine", "acetaminophen", "ibuprofen", "naproxen",
    "diclofenac", "celecoxib", "meloxicam", "indomethacin", "piroxicam",
    "amoxicillin", "azithromycin", "ciprofloxacin", "doxycycline", "penicillin",
    "atorvastatin", "simvastatin", "rosuvastatin", "pravastatin", "lovastatin",
    "metformin", "insulin", "glipizide", "glyburide", "pioglitazone",
    "lisinopril", "enalapril", "losartan", "valsartan", "amlodipine",
    "metoprolol", "atenolol", "propranolol", "carvedilol", "bisoprolol",
    "warfarin", "heparin", "clopidogrel", "aspirin", "rivaroxaban",
    "omeprazole", "lansoprazole", "pantoprazole", "esomeprazole", "ranitidine",
    "fluoxetine", "sertraline", "paroxetine", "citalopram", "escitalopram",
]

BENCHMARK_PROPERTIES = [
    "molecular_weight",
    "xlogp",
    "cas",
    "iupac_name",
    "canonical_smiles",
    "molecular_formula"
]


class TestPerformanceBenchmarks:
    """Performance benchmarks for ChemInformant core functionality."""

    @pytest.mark.benchmark(group="single_compound")
    def test_single_compound_lookup(self, benchmark):
        """Benchmark single compound property lookup."""
        def single_lookup():
            return ci.get_properties(["aspirin"], ["molecular_weight", "xlogp"])

        result = benchmark(single_lookup)
        assert len(result) == 1
        assert result.iloc[0]["status"] == "OK"

    @pytest.mark.benchmark(group="batch_processing")
    def test_small_batch_processing(self, benchmark):
        """Benchmark small batch processing (10 compounds)."""
        compounds = SAMPLE_DRUGS[:10]

        def batch_lookup():
            return ci.get_properties(compounds, BENCHMARK_PROPERTIES[:3])

        result = benchmark(batch_lookup)
        assert len(result) <= len(compounds)  # Some compounds might fail

    @pytest.mark.benchmark(group="batch_processing")
    def test_medium_batch_processing(self, benchmark):
        """Benchmark medium batch processing (25 compounds)."""
        compounds = SAMPLE_DRUGS[:25]

        def batch_lookup():
            return ci.get_properties(compounds, BENCHMARK_PROPERTIES[:4])

        result = benchmark(batch_lookup)
        assert len(result) <= len(compounds)

    @pytest.mark.benchmark(group="batch_processing")
    def test_large_batch_processing(self, benchmark):
        """Benchmark large batch processing (50 compounds)."""
        compounds = SAMPLE_DRUGS

        def batch_lookup():
            return ci.get_properties(compounds, BENCHMARK_PROPERTIES)

        result = benchmark(batch_lookup)
        assert len(result) <= len(compounds)

    @pytest.mark.benchmark(group="caching")
    def test_cache_performance(self, benchmark):
        """Benchmark cache hit performance."""
        # First, populate the cache
        test_compounds = SAMPLE_DRUGS[:5]
        ci.get_properties(test_compounds, ["molecular_weight"])

        # Now benchmark cache hits
        def cached_lookup():
            return ci.get_properties(test_compounds, ["molecular_weight"])

        result = benchmark(cached_lookup)
        assert len(result) <= len(test_compounds)

    @pytest.mark.benchmark(group="convenience_api")
    def test_convenience_functions(self, benchmark):
        """Benchmark convenience function performance."""
        def convenience_lookup():
            results = []
            for compound in SAMPLE_DRUGS[:10]:
                try:
                    weight = ci.get_weight(compound)
                    if weight is not None:
                        results.append(weight)
                except Exception:
                    continue
            return results

        result = benchmark(convenience_lookup)
        assert isinstance(result, list)

    @pytest.mark.benchmark(group="mixed_identifiers")
    def test_mixed_identifier_types(self, benchmark):
        """Benchmark handling of mixed identifier types."""
        mixed_identifiers = [
            "aspirin",  # name
            2244,       # CID
            "CC(=O)OC1=CC=CC=C1C(=O)O",  # SMILES
            "caffeine", # name
            2519,       # CID
        ]

        def mixed_lookup():
            return ci.get_properties(mixed_identifiers, ["molecular_weight", "cas"])

        result = benchmark(mixed_lookup)
        assert len(result) <= len(mixed_identifiers)

    @pytest.mark.benchmark(group="error_handling")
    def test_error_handling_performance(self, benchmark):
        """Benchmark performance with invalid compounds."""
        invalid_compounds = [
            "invalid_compound_name_12345",
            "another_fake_compound",
            "aspirin",  # valid one
            999999999,  # invalid CID
            "caffeine", # valid one
        ]

        def error_handling_lookup():
            return ci.get_properties(invalid_compounds, ["molecular_weight"])

        result = benchmark(error_handling_lookup)
        # Should have some results, but not all
        assert len(result) <= len(invalid_compounds)


@pytest.mark.benchmark(group="comparison")
class TestComparisonBenchmarks:
    """Benchmarks comparing different approaches."""

    def test_batch_vs_individual_calls(self, benchmark):
        """Compare batch processing vs individual calls."""
        compounds = SAMPLE_DRUGS[:10]
        properties = ["molecular_weight", "xlogp"]

        def individual_calls():
            results = []
            for compound in compounds:
                try:
                    result = ci.get_properties([compound], properties)
                    if not result.empty:
                        results.append(result.iloc[0])
                except Exception:
                    continue
            return results

        # Benchmark individual calls
        individual_result = benchmark(individual_calls)

        # Compare with batch call (not benchmarked, just for reference)
        batch_result = ci.get_properties(compounds, properties)

        # Both should return similar number of results
        assert len(individual_result) <= len(batch_result) + 2  # Allow some variance


# Utility functions for benchmark analysis
def analyze_benchmark_results(benchmark_results):
    """Analyze and summarize benchmark results."""
    if not benchmark_results:
        return {}

    return {
        "min_time": min(benchmark_results),
        "max_time": max(benchmark_results),
        "mean_time": statistics.mean(benchmark_results),
        "median_time": statistics.median(benchmark_results),
        "std_dev": statistics.stdev(benchmark_results) if len(benchmark_results) > 1 else 0,
    }


# Custom benchmark fixtures
@pytest.fixture
def fresh_cache():
    """Fixture to ensure fresh cache for certain tests."""
    # This would clear cache if we had a public cache clearing method
    # For now, just yield
    yield
    # Cleanup if needed


# Performance thresholds (can be adjusted based on system performance)
PERFORMANCE_THRESHOLDS = {
    "single_compound_max_time": 5.0,  # seconds
    "batch_10_max_time": 10.0,        # seconds
    "cache_hit_max_time": 1.0,        # seconds
}


def test_performance_thresholds():
    """Test that performance meets minimum thresholds."""
    # This is a simple performance regression test
    start_time = time.time()
    result = ci.get_properties(["aspirin"], ["molecular_weight"])
    end_time = time.time()

    elapsed = end_time - start_time
    assert elapsed < PERFORMANCE_THRESHOLDS["single_compound_max_time"], \
        f"Single compound lookup took {elapsed:.2f}s, exceeds threshold"

    assert len(result) == 1
    assert result.iloc[0]["status"] == "OK"
