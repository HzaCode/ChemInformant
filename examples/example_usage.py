import os
import sys

# === Add 'src' directory to Python path ===
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(CURRENT_DIR, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

print("Added module path:", SRC_PATH)

# === Try importing from api_helpers.py ===
try:
    from api_helpers import (
        get_cid_by_name,
        get_cas_unii,
        get_compound_description,
        get_all_synonyms,
        get_additional_details
    )
    print("Successfully imported from api_helpers")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# === Test function ===
def test_display_compound_details(name):
    print(f"\n=== Testing compound: {name} ===")
    cid = get_cid_by_name(name)
    if cid:
        cas, unii = get_cas_unii(cid)
        description = get_compound_description(cid)
        synonyms = get_all_synonyms(cid)
        properties = get_additional_details(cid)

        print(f"CID: {cid}")
        print(f"CAS: {cas}")
        print(f"UNII: {unii}")
        print(f"Description: {description}")
        print(f"Synonyms: {', '.join(synonyms[:5])}")
        print(f"IUPAC Name: {properties.get('IUPACName', 'N/A')}")
        print(f"Molecular Formula: {properties.get('MolecularFormula', 'N/A')}")
        print(f"Molecular Weight: {properties.get('MolecularWeight', 'N/A')}")
        print(f"Canonical SMILES: {properties.get('CanonicalSMILES', 'N/A')}")
    else:
        print("No information found for this compound.")

# === Run test ===
if __name__ == "__main__":
    print("Running api_helpers test...")
    test_display_compound_details("Aspirin")
    print("Test complete!")
