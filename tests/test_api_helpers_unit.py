import tempfile
import time
from pathlib import Path
from unittest import mock

import requests
import requests_cache

from ChemInformant import api_helpers


class TestCacheSetup:
    def test_setup_cache_with_defaults(self):
        api_helpers.setup_cache()
        session = api_helpers.get_session()
        assert isinstance(session, requests_cache.CachedSession)

    def test_setup_cache_with_custom_params(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_path = Path(tmp_dir) / "test_cache"
            api_helpers.setup_cache(
                cache_name=str(cache_path), backend="sqlite", expire_after=3600
            )
            session = api_helpers.get_session()
            assert isinstance(session, requests_cache.CachedSession)
            if hasattr(session.cache, "close"):
                session.cache.close()
            api_helpers._session = None

    def test_get_session_initializes_when_none(self):
        api_helpers._session = None
        session = api_helpers.get_session()
        assert isinstance(session, requests_cache.CachedSession)


class TestNetworkRequests:
    def test_execute_fetch(self):
        with mock.patch.object(api_helpers, "get_session") as mock_get_session:
            mock_session = mock.Mock()
            mock_response = mock.Mock()
            mock_session.get.return_value = mock_response
            mock_get_session.return_value = mock_session

            result = api_helpers._execute_fetch("http://example.com")

            assert result == mock_response
            mock_session.get.assert_called_once_with(
                "http://example.com", timeout=api_helpers.REQUEST_TIMEOUT
            )

    def test_fetch_with_successful_response(self):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"test": "data"}

        with mock.patch.object(
            api_helpers, "_execute_fetch", return_value=mock_response
        ):
            result = api_helpers._fetch_with_ratelimit_and_retry("http://example.com")
            assert result == {"test": "data"}

    def test_fetch_with_404_response(self):
        mock_response = mock.Mock()
        mock_response.status_code = 404

        with mock.patch.object(
            api_helpers, "_execute_fetch", return_value=mock_response
        ):
            result = api_helpers._fetch_with_ratelimit_and_retry("http://example.com")
            assert result is None

    def test_fetch_with_503_response_and_retry(self):
        mock_response_503 = mock.Mock()
        mock_response_503.status_code = 503
        mock_response_503.from_cache = False

        mock_response_200 = mock.Mock()
        mock_response_200.status_code = 200
        mock_response_200.headers = {"Content-Type": "application/json"}
        mock_response_200.json.return_value = {"data": "success"}

        with mock.patch.object(
            api_helpers,
            "_execute_fetch",
            side_effect=[mock_response_503, mock_response_200],
        ):
            with mock.patch("time.sleep"):
                result = api_helpers._fetch_with_ratelimit_and_retry(
                    "http://example.com"
                )
                assert result == {"data": "success"}

    def test_fetch_with_cached_503_response(self):
        mock_response_503 = mock.Mock()
        mock_response_503.status_code = 503
        mock_response_503.from_cache = True
        mock_response_503.request = mock.Mock()

        mock_response_200 = mock.Mock()
        mock_response_200.status_code = 200
        mock_response_200.headers = {"Content-Type": "application/json"}
        mock_response_200.json.return_value = {"data": "success"}

        mock_session = mock.Mock()
        mock_session.cache.create_key.return_value = "test_key"
        mock_session.cache.delete.return_value = None
        mock_session.cache.disabled.return_value.__enter__ = mock.Mock(
            return_value=None
        )
        mock_session.cache.disabled.return_value.__exit__ = mock.Mock(return_value=None)

        with mock.patch.object(api_helpers, "get_session", return_value=mock_session):
            with mock.patch.object(
                api_helpers,
                "_execute_fetch",
                side_effect=[mock_response_503, mock_response_200],
            ):
                result = api_helpers._fetch_with_ratelimit_and_retry(
                    "http://example.com"
                )
                assert result == {"data": "success"}

    def test_fetch_with_network_error(self):
        with mock.patch.object(
            api_helpers,
            "_execute_fetch",
            side_effect=requests.exceptions.RequestException("Network error"),
        ):
            with mock.patch("time.sleep"):
                result = api_helpers._fetch_with_ratelimit_and_retry(
                    "http://example.com"
                )
                assert result is None

    def test_fetch_with_text_response(self):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.text = "plain text response"

        with mock.patch.object(
            api_helpers, "_execute_fetch", return_value=mock_response
        ):
            result = api_helpers._fetch_with_ratelimit_and_retry("http://example.com")
            assert result == "plain text response"


class TestAPIHelperFunctions:
    def test_get_cids_by_smiles_success(self):
        mock_data = {"IdentifierList": {"CID": [2519, 2520]}}

        with mock.patch.object(
            api_helpers, "_fetch_with_ratelimit_and_retry", return_value=mock_data
        ):
            result = api_helpers.get_cids_by_smiles("CC(=O)OC1=CC=CC=C1C(=O)O")
            assert result == [2519, 2520]

    def test_get_cids_by_smiles_not_found(self):
        with mock.patch.object(
            api_helpers, "_fetch_with_ratelimit_and_retry", return_value=None
        ):
            result = api_helpers.get_cids_by_smiles("invalid_smiles")
            assert result is None

    def test_get_cids_by_smiles_invalid_response(self):
        with mock.patch.object(
            api_helpers, "_fetch_with_ratelimit_and_retry", return_value="invalid"
        ):
            result = api_helpers.get_cids_by_smiles("CC(=O)OC1=CC=CC=C1C(=O)O")
            assert result is None

    def test_get_batch_properties_empty_input(self):
        result = api_helpers.get_batch_properties([], [])
        assert result == {}

        result = api_helpers.get_batch_properties([1, 2], [])
        assert result == {}

    def test_get_batch_properties_with_pagination(self):
        first_response = {
            "PropertyTable": {"Properties": [{"CID": 1, "MolecularWeight": "100.0"}]},
            "ListKey": "test_key_123",
        }

        second_response = {
            "PropertyTable": {"Properties": [{"CID": 2, "MolecularWeight": "200.0"}]}
        }

        with mock.patch.object(
            api_helpers,
            "_fetch_with_ratelimit_and_retry",
            side_effect=[first_response, second_response],
        ):
            result = api_helpers.get_batch_properties([1, 2], ["MolecularWeight"])
            assert 1 in result
            assert 2 in result
            assert result[1]["MolecularWeight"] == "100.0"
            assert result[2]["MolecularWeight"] == "200.0"

    def test_get_batch_properties_invalid_response(self):
        with mock.patch.object(
            api_helpers, "_fetch_with_ratelimit_and_retry", return_value="invalid"
        ):
            result = api_helpers.get_batch_properties([1, 2], ["MolecularWeight"])
            assert result == {1: {}, 2: {}}

    def test_get_cas_for_cid_success(self):
        mock_response = {
            "Record": {
                "Section": [
                    {
                        "TOCHeading": "Names and Identifiers",
                        "Section": [
                            {
                                "TOCHeading": "Other Identifiers",
                                "Section": [
                                    {
                                        "TOCHeading": "CAS",
                                        "Information": [
                                            {
                                                "Value": {
                                                    "StringWithMarkup": [
                                                        {"String": "58-08-2"}
                                                    ]
                                                }
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    }
                ]
            }
        }

        with mock.patch.object(
            api_helpers, "_fetch_with_ratelimit_and_retry", return_value=mock_response
        ):
            result = api_helpers.get_cas_for_cid(2519)
            assert result == "58-08-2"

    def test_get_cas_for_cid_not_found(self):
        mock_response = {
            "Record": {"Section": [{"TOCHeading": "Other Section", "Section": []}]}
        }

        with mock.patch.object(
            api_helpers, "_fetch_with_ratelimit_and_retry", return_value=mock_response
        ):
            result = api_helpers.get_cas_for_cid(2519)
            assert result is None

    def test_get_synonyms_for_cid_success(self):
        mock_response = {
            "InformationList": {
                "Information": [
                    {"CID": 2519, "Synonym": ["Caffeine", "1,3,7-trimethylxanthine"]}
                ]
            }
        }

        with mock.patch.object(
            api_helpers, "_fetch_with_ratelimit_and_retry", return_value=mock_response
        ):
            result = api_helpers.get_synonyms_for_cid(2519)
            assert result == ["Caffeine", "1,3,7-trimethylxanthine"]

    def test_get_synonyms_for_cid_empty_response(self):
        with mock.patch.object(
            api_helpers, "_fetch_with_ratelimit_and_retry", return_value=None
        ):
            result = api_helpers.get_synonyms_for_cid(2519)
            assert result == []


class TestRateLimiting:
    def test_rate_limiting_enforced(self):
        api_helpers.last_api_call_time = time.time()

        with mock.patch("time.sleep") as mock_sleep:
            with mock.patch.object(api_helpers, "_execute_fetch") as mock_fetch:
                mock_response = mock.Mock()
                mock_response.status_code = 200
                mock_response.headers = {"Content-Type": "application/json"}
                mock_response.json.return_value = {}
                mock_fetch.return_value = mock_response

                api_helpers._fetch_with_ratelimit_and_retry("http://example.com")

                mock_sleep.assert_called()
