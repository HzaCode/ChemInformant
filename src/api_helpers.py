import requests
from urllib.parse import quote
import xml.etree.ElementTree as ET

def get_cid_by_name(name):
    """Retrieve the first CID for a given compound name."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{quote(name)}/cids/JSON"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        cids = response.json().get('IdentifierList', {}).get('CID', [])
        return cids[0] if cids else None
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching CID for {name}: {e}")
        return None

def get_cas_unii(cid):
    """Retrieve CAS and UNII identifiers for a given CID."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        cas = unii = "Not found"
        if 'Record' in data and 'Reference' in data['Record']:
            for ref in data['Record']['Reference']:
                if ref['SourceName'] == 'CAS Common Chemistry':
                    cas = ref['SourceID']
                if ref['SourceName'] == 'FDA Global Substance Registration System (GSRS)':
                    unii = ref['SourceID']
        return cas, unii
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching CAS/UNII for CID {cid}: {e}")
        return None, None

def get_compound_description(cid):
    """Retrieve the description for a given CID."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/description/XML"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        for info in root.findall('{http://pubchem.ncbi.nlm.nih.gov/pug_rest}Information'):
            description = info.find('{http://pubchem.ncbi.nlm.nih.gov/pug_rest}Description')
            if description is not None:
                return description.text
        return "No description available"
    except (requests.RequestException, ET.ParseError) as e:
        print(f"Error fetching description for CID {cid}: {e}")
        return "No description available"

def get_all_synonyms(cid):
    """Retrieve all synonyms for a given CID as a list."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        synonyms_data = response.json()
        synonyms = synonyms_data.get('InformationList', {}).get('Information', [{}])[0].get('Synonym', [])
        return synonyms
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching synonyms for CID {cid}: {e}")
        return []

def get_additional_details(cid):
    """Retrieve additional properties for a given CID."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/IUPACName,MolecularFormula,MolecularWeight,CanonicalSMILES/JSON"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json().get('PropertyTable', {}).get('Properties', [{}])[0]
        return {
            'IUPACName': data.get('IUPACName', 'N/A'),
            'MolecularFormula': data.get('MolecularFormula', 'N/A'),
            'MolecularWeight': data.get('MolecularWeight', 'N/A'),
            'CanonicalSMILES': data.get('CanonicalSMILES', 'N/A')
        }
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching additional details for CID {cid}: {e}")
        return {'IUPACName': 'N/A', 'MolecularFormula': 'N/A', 'MolecularWeight': 'N/A', 'CanonicalSMILES': 'N/A'}