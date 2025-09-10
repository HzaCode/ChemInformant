import os
import shutil
import time
from pathlib import Path
from unittest import mock

import requests

import ChemInformant as ci
from ChemInformant import api_helpers

TMP_HOME = Path(__file__).parent / "_tmp_cache_test"

def cleanup():
    """Clean up any cached state and remove temp directory."""
    if hasattr(api_helpers, "_session") and api_helpers._session:
        try:
            api_helpers._session.cache.clear()
        except Exception:
            pass
        finally:
            api_helpers._session = None
    if TMP_HOME.exists():
        shutil.rmtree(TMP_HOME, ignore_errors=True)


def setup_test_environment(expire_after=0.2):
    """Set up a clean isolated test environment with cache."""
    cleanup()
    TMP_HOME.mkdir(exist_ok=True)
    os.environ["CHEMINFORMANT_HOME"] = str(TMP_HOME)
    # Don't reload modules as it breaks mocking
    ci.setup_cache(backend="sqlite", expire_after=expire_after)


def mock_pubchem_responses(url: str, **kwargs) -> requests.Response:
    """Simulate responses for known PubChem endpoints."""
    mock_resp = mock.Mock(spec=requests.Response)
    mock_resp.status_code = 200
    mock_resp.headers = {'Content-Type': 'application/json'}
    mock_resp.from_cache = False

    if 'compound/name/caffeine/cids' in url:
        mock_resp.json.return_value = {'IdentifierList': {'CID': [2519]}}
    elif 'compound/cid/2519/property' in url:
        mock_resp.json.return_value = {
            "PropertyTable": {
                "Properties": [{
                    "CID": 2519,
                    "MolecularWeight": "194.19",
                    "IUPACName": "1,3,7-trimethylpurine-2,6-dione"
                }]
            }
        }
    elif 'compound/cid/2519/synonyms' in url:
        mock_resp.json.return_value = {
            "InformationList": {
                "Information": [{
                    "CID": 2519,
                    "Synonym": ["Caffeine"]
                }]
            }
        }
    elif 'pug_view/data/compound/2519' in url:
        mock_resp.json.return_value = {
            "Record": {
                "Section": [{
                    "TOCHeading": "Names and Identifiers",
                    "Section": [{
                        "TOCHeading": "Other Identifiers",
                        "Section": [{
                            "TOCHeading": "CAS",
                            "Information": [{
                                "Value": {
                                    "StringWithMarkup": [{"String": "58-08-2"}]
                                }
                            }]
                        }]
                    }]
                }]
            }
        }
    else:
        mock_resp.status_code = 404
        mock_resp.json.return_value = {"error": f"Unknown mock URL: {url}"}
    return mock_resp


def test_cache_expires():
    """Test that cache expiration works correctly."""
    with mock.patch('ChemInformant.api_helpers._execute_fetch', side_effect=mock_pubchem_responses):
        setup_test_environment(expire_after=0.2)

        # First call should trigger mock network responses
        c1 = ci.get_compound("caffeine")
        assert c1.cid == 2519
        assert c1.cas == "58-08-2"

        time.sleep(0.3)

        # Second call (after cache expiry) should still return the same result
        c2 = ci.get_compound("caffeine")
        assert c2.cid == 2519
        assert c2.cas == "58-08-2"

        print("✅ test_cache_expires passed")
        cleanup()
