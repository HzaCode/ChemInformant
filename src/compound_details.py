from api_helpers import get_cid_by_name, get_cas_unii, get_compound_description, get_all_synonyms, get_additional_details

def get_compound_details(name):
    """
    Retrieves comprehensive details for a compound by its name.

    Parameters:
    - name: The common name of the compound to fetch details for.

    Returns:
    A dictionary containing various details about the compound, including its CID,
    CAS number, UNII, description, synonyms, and chemical properties.
    """
    details = {}
    cid = get_cid_by_name(name)
    if cid:
        details['CID'] = cid
        details['CAS'], details['UNII'] = get_cas_unii(cid)
        details['Description'] = get_compound_description(cid)
        details['Synonyms'] = get_all_synonyms(cid)
        additional_props = get_additional_details(cid)
        details.update(additional_props)  # Merge additional properties into the details dict
    else:
        details['Error'] = "Compound not found"
    return details
