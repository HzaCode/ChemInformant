# src/api_helpers.py
import requests

def get_cid_by_name(compound_name):
    """Get the PubChem Compound ID (CID) for a chemical compound."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound_name}/cids/JSON"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['IdentifierList']['CID'][0]
        return None
    except Exception as e:
        print(f"Error retrieving CID for {compound_name}: {e}")
        return None

def get_cas_unii(cid):
    """Get the CAS Registry Number and UNII code for a compound."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON"
    cas = "Not found"
    unii = "Not found"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            synonyms = data['InformationList']['Information'][0]['Synonym']
            
            # Find CAS number (format: ###-##-#)
            for synonym in synonyms:
                if '-' in synonym:
                    parts = synonym.split('-')
                    if len(parts) == 3 and all(p.isdigit() for p in parts):
                        cas = synonym
                        break
            
            # Find UNII (10 characters, alphanumeric, starts with a letter)
            for synonym in synonyms:
                if len(synonym) == 10 and synonym.isalnum() and synonym[0].isalpha():
                    unii = synonym
                    break
            
        return cas, unii
    except Exception as e:
        print(f"Error retrieving CAS/UNII for CID {cid}: {e}")
        return "Not found", "Not found"

def get_compound_description(cid):
    """Get the description of a chemical compound."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/description/JSON"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'InformationList' in data and 'Information' in data['InformationList']:
                info = data['InformationList']['Information']
                if info and 'Description' in info[0]:
                    return info[0]['Description']
        return "No description available"
    except Exception as e:
        print(f"Error retrieving description for CID {cid}: {e}")
        return "No description available"

def get_all_synonyms(cid):
    """Get all synonyms for a chemical compound."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'InformationList' in data and 'Information' in data['InformationList']:
                info = data['InformationList']['Information']
                if info and 'Synonym' in info[0]:
                    return info[0]['Synonym']
        return []
    except Exception as e:
        print(f"Error retrieving synonyms for CID {cid}: {e}")
        return []

def get_additional_details(cid):
    """Get additional chemical properties for a compound."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,IUPACName/JSON"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'PropertyTable' in data and 'Properties' in data['PropertyTable']:
                properties = data['PropertyTable']['Properties']
                if properties:
                    return properties[0]
        return {}
    except Exception as e:
        print(f"Error retrieving properties for CID {cid}: {e}")
        return {}