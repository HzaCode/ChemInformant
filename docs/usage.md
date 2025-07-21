# Usage Guide

This guide provides detailed examples of how to use ChemInformant's core features.

## Installation

Install ChemInformant directly from PyPI:

```bash
pip install cheminformant
```

To include optional dependencies for structure drawing, you can install the `plot` extra:
```bash
pip install "cheminformant[plot]"
```

## Basic Usage: Convenience Functions

For quick lookups of a single property for a single compound, use the convenience functions. They are simple and direct.

```python
import ChemInformant as ci

# Get the CAS number for Ibuprofen
cas = ci.get_cas("ibuprofen")
# > '15687-27-1'

# Get the molecular weight for Aspirin (using its CID)
weight = ci.get_weight(2244)
# > 180.16

# Get a list of synonyms for Caffeine
synonyms = ci.get_synonyms("caffeine")
# > ['1,3,7-Trimethylxanthine', 'Guaranine', 'Methyltheobromine', ...]
```

## Core Functionality: Batch Processing

The real power of ChemInformant lies in its batch processing capabilities. The `get_properties()` function is the workhorse for high-throughput tasks.

### Retrieving Multiple Properties

You can fetch multiple properties for multiple identifiers in a single call. Notice the input list contains a mix of names and a CID.

```python
import ChemInformant as ci

df = ci.get_properties(
    identifiers=["aspirin", "caffeine", 1983, "invalid_identifier"],
    properties=["molecular_weight", "xlogp", "cas"]
)

print(df)
```

**Output DataFrame:**

The output is a clean Pandas DataFrame, perfect for data analysis. It includes a `status` column that tells you the outcome for each identifier.

| | input_identifier | cid | status | molecular_weight | xlogp | cas |
|---|---|---|---|---|---|---|
| 0 | aspirin | 2244 | OK | 180.160 | 1.2 | 50-78-2 |
| 1 | caffeine | 2519 | OK | 194.190 | -0.1 | 58-08-2 |
| 2 | 1983 | 1983 | OK | 151.160 | 1.2 | 103-90-2 |
| 3 | invalid_identifier | None | NotFoundError | NaN | NaN | None |


### Working with Compound Objects

For a more object-oriented approach, you can retrieve data as `Compound` objects. These are Pydantic models that provide type-hinting and a structured way to access data.

```python
compound = ci.get_compound("paracetamol")

print(f"Name: {compound.iupac_name}")
print(f"Formula: {compound.molecular_formula}")
print(f"PubChem URL: {compound.pubchem_url}")
```

### Drawing a 2D Structure

If you have `matplotlib` and `pillow` installed, you can easily visualize a compound's structure.

```python
# This will open a Matplotlib window with the structure
ci.draw_compound("taxol")
```

## Caching

ChemInformant uses a persistent cache by default (`pubchem_cache.sqlite`). The first time you query an identifier, the result is saved. Subsequent queries for the same data will be nearly instantaneous.

You can customize the cache behavior using `setup_cache()`:
```python
# Store cache in a different file and set expiration to 1 day
ci.setup_cache(cache_name="my_project_cache", expire_after=86400)
```
