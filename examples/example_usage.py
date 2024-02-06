from src.api_helpers import get_cid_by_name, get_cas_unii, get_compound_description, get_all_synonyms, get_additional_details

def display_compound_details(name):
    cid = get_cid_by_name(name)
    if cid:
        cas, unii = get_cas_unii(cid)
        description = get_compound_description(cid)
        synonyms = get_all_synonyms(cid)
        properties = get_additional_details(cid)

        print(f"Details for {name}:")
        print(f"CID: {cid}")
        print(f"CAS: {cas}")
        print(f"UNII: {unii}")
        print(f"Description: {description}")
        print(f"Synonyms: {', '.join(synonyms[:5])}")  # Display only first 5 synonyms for brevity
        print(f"IUPAC Name: {properties.get('IUPACName', 'N/A')}")
        print(f"Molecular Formula: {properties.get('MolecularFormula', 'N/A')}")
        print(f"Molecular Weight: {properties.get('MolecularWeight', 'N/A')}")
        print(f"Canonical SMILES: {properties.get('CanonicalSMILES', 'N/A')}")
    else:
        print(f"No details found for {name}.")

# Example usage
if __name__ == "__main__":
    compound_name = "Aspirin"  # Replace with the compound name of your choice
    display_compound_details(compound_name)
