import time
import ChemInformant as ci
import pandas as pd
import pubchempy as pcp

def benchmark_pubchempy(identifiers, properties_to_map):
    """
    Benchmark using PubChemPy with individual queries as a baseline.
    """
    print("\n[3] Benchmarking PubChemPy (individual queries)...")
    start_time = time.perf_counter()
    
    results = []
    
    for identifier in identifiers:
        record = {'input_identifier': identifier, 'status': 'UnknownError'}
        try:
            compounds = pcp.get_compounds(identifier, 'name')
            if not compounds:
                record['status'] = 'NotFoundError'
                results.append(record)
                continue

            c = compounds[0]
            record.update({'status': 'OK', 'cid': c.cid})
            
            if 'molecular_weight' in properties_to_map:
                record['molecular_weight'] = getattr(c, 'molecular_weight', None)
            if 'molecular_formula' in properties_to_map:
                record['molecular_formula'] = getattr(c, 'molecular_formula', None)
            if 'xlogp' in properties_to_map:
                record['xlogp'] = getattr(c, 'xlogp', None)
            if 'canonical_smiles' in properties_to_map:
                record['canonical_smiles'] = getattr(c, 'canonical_smiles', None)

            if 'cas' in properties_to_map:
                cas_list = [syn for syn in c.synonyms if syn.isdigit() and len(syn.split('-')) == 3]
                record['cas'] = cas_list[0] if cas_list else None
            
            if 'synonyms' in properties_to_map:
                record['synonyms'] = getattr(c, 'synonyms', [])
            
            results.append(record)

        except Exception as e:
            record['status'] = type(e).__name__
            results.append(record)

    duration = time.perf_counter() - start_time
    print(f"    > Done! Took {duration:.4f} seconds.")
    return duration, pd.DataFrame(results)

def run_benchmark(identifiers, properties):
    """
    Run benchmark to measure uncached, cached, and PubChemPy comparison performance.
    """
    print("--- ChemInformant Performance Benchmark ---")
    print(f"Fetching {len(properties)} properties for {len(identifiers)} compounds...")

    ci.setup_cache(backend='memory')
    print("In-memory cache set up. Benchmark starting...")

    # 1. ChemInformant (uncached)
    print("\n[1] ChemInformant (uncached) batch call...")
    start_time_uncached = time.perf_counter()
    df_ci_uncached = ci.get_properties(identifiers, properties)
    duration_uncached = time.perf_counter() - start_time_uncached
    print(f"    > Done! Took {duration_uncached:.4f} seconds.")

    ok_count = (df_ci_uncached['status'] == 'OK').sum()
    error_count = len(identifiers) - ok_count
    print(f"    > Results: {ok_count} success, {error_count} failures.")
    if ok_count == 0:
        print("    > Warning: Failed to fetch any data. Check network connection.")
        return

    # 2. ChemInformant (cached)
    print("\n[2] ChemInformant (cached) second call...")
    start_time_cached = time.perf_counter()
    df_ci_cached = ci.get_properties(identifiers, properties)
    duration_cached = time.perf_counter() - start_time_cached
    print(f"    > Done! Took {duration_cached:.4f} seconds.")

    # 3. PubChemPy (as baseline)
    duration_pubchempy, df_pcp = benchmark_pubchempy(identifiers, properties)

    # 4. Performance Report
    print("\n--- Benchmark Results ---")
    print("Methodology:")
    print("  - ChemInformant (uncached): Single or few batch API calls.")
    print("  - PubChemPy (baseline):     Looping API calls for each compound.")
    print("  - ChemInformant (cached):   Batch read from local cache.\n")

    if duration_cached > 0 and duration_uncached > 0:
        speedup_cache = duration_uncached / duration_cached
        print(f"  Cache vs. Uncached speedup: {speedup_cache:.2f}x")
    
    if duration_pubchempy > 0 and duration_uncached > 0:
        speedup_vs_baseline = duration_pubchempy / duration_uncached
        print(f"  Batch vs. Loop speedup: {speedup_vs_baseline:.2f}x")

    print(f"\n  Baseline (PubChemPy loop):      {duration_pubchempy:.4f}s")
    print(f"  ChemInformant (uncached batch): {duration_uncached:.4f}s")
    print(f"  ChemInformant (cached):       {duration_cached:.4f}s")
    print("--------------------")

    try:
        ci_success = df_ci_uncached[df_ci_uncached['status'] == 'OK'].sort_values('cid').reset_index(drop=True)
        pcp_success = df_pcp[df_pcp['status'] == 'OK'].sort_values('cid').reset_index(drop=True)
        
        common_cols = ['cid', 'molecular_weight', 'molecular_formula', 'xlogp', 'canonical_smiles']
        pd.testing.assert_frame_equal(ci_success[common_cols], pcp_success[common_cols], check_dtype=False, atol=0.01)
        print("\nVerification successful: Core data from both libraries matches.")
    except AssertionError as e:
        print("\nWarning: Data from the two libraries does not match. This might be due to minor differences in the data sources.")
        print(e)
    except Exception as e:
        print(f"\nError during results verification: {e}")

if __name__ == "__main__":
    common_compounds = [
        "aspirin", "caffeine", "paracetamol", "ibuprofen", "morphine",
        "methamphetamine", "ethanol", "water", "benzene", "toluene", 
        "cholesterol", "glucose", "serotonin", "dopamine", "nicotine",
        "vanillin", "menthol", "capsaicin", "ascorbic acid", "citric acid"
    ]
    properties_to_fetch = [
        "molecular_weight",
        "molecular_formula",
        "xlogp",
        "cas",
        "canonical_smiles",
        "synonyms"
    ]
    run_benchmark(common_compounds, properties_to_fetch)