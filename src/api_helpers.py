import requests

def get_cid_by_name(name):
    """Retrieve the first CID for a given compound name."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/cids/JSON"
    response = requests.get(url)
    if response.status_code == 200:
        cids = response.json().get('IdentifierList', {}).get('CID', [])
        return cids[0] if cids else None
    else:
        return None

def get_cas_unii(cid):
    """Retrieve CAS and UNII identifiers for a given CID."""
    url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        cas = unii = "Not found"
        if 'Record' in data and 'Reference' in data['Record']:
            for ref in data['Record']['Reference']:
                if ref['SourceName'] == 'CAS Common Chemistry':
                    cas = ref['SourceID']
                if ref['SourceName'] == 'FDA Global Substance Registration System (GSRS)':
                    unii = ref['SourceID']
        return cas, unii
    return None, None

def get_compound_description(cid):
    """Retrieve the description for a given CID."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/description/XML"
    response = requests.get(url)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        for info in root.findall('{http://pubchem.ncbi.nlm.nih.gov/pug_rest}Information'):
            description = info.find('{http://pubchem.ncbi.nlm.nih.gov/pug_rest}Description')
            if description is not None:
                return description.text
    return "No description available"

def get_all_synonyms(cid):
    """Retrieve all synonyms for a given CID."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON"
    response = requests.get(url)
    if response.status_code == 200:
        synonyms_data = response.json()
        synonyms = synonyms_data.get('InformationList', {}).get('Information', [{}])[0].get('Synonym', [])
        return ", ".join(synonyms)
    else:
        return "Synonyms not found"
