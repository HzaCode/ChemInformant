from unittest import mock
import pytest
import pandas as pd

from src.ChemInformant import cheminfo_api
from src.ChemInformant.models import Compound, NotFoundError, AmbiguousIdentifierError


class TestResolveCid:

    def test_resolve_integer_cid(self):
        result = cheminfo_api._resolve_to_single_cid(2519)
        assert result == 2519

    def test_resolve_string_digit_cid(self):
        result = cheminfo_api._resolve_to_single_cid("2519")
        assert result == 2519

    def test_resolve_negative_cid_raises_error(self):
        with pytest.raises(ValueError):
            cheminfo_api._resolve_to_single_cid(-1)

    def test_resolve_zero_cid_raises_error(self):
        with pytest.raises(ValueError):
            cheminfo_api._resolve_to_single_cid(0)

    def test_resolve_name_single_result(self):
        with mock.patch('src.ChemInformant.api_helpers.get_cids_by_name', return_value=[2519]):
            result = cheminfo_api._resolve_to_single_cid("caffeine")
            assert result == 2519

    def test_resolve_name_multiple_results_raises_ambiguous(self):
        with mock.patch('src.ChemInformant.api_helpers.get_cids_by_name', return_value=[2519, 2520]):
            with pytest.raises(AmbiguousIdentifierError):
                cheminfo_api._resolve_to_single_cid("ambiguous_name")

    def test_resolve_name_no_results_try_smiles(self):
        with mock.patch('src.ChemInformant.api_helpers.get_cids_by_name', return_value=None):
            with mock.patch.object(cheminfo_api, '_looks_like_smiles', return_value=True):
                with mock.patch('src.ChemInformant.api_helpers.get_cids_by_smiles', return_value=[2519]):
                    result = cheminfo_api._resolve_to_single_cid("CC(=O)OC1=CC=CC=C1C(=O)O")
                    assert result == 2519

    def test_resolve_smiles_multiple_results_raises_ambiguous(self):
        with mock.patch('src.ChemInformant.api_helpers.get_cids_by_name', return_value=None):
            with mock.patch.object(cheminfo_api, '_looks_like_smiles', return_value=True):
                with mock.patch('src.ChemInformant.api_helpers.get_cids_by_smiles', return_value=[2519, 2520]):
                    with pytest.raises(AmbiguousIdentifierError):
                        cheminfo_api._resolve_to_single_cid("CC(=O)OC1=CC=CC=C1C(=O)O")

    def test_resolve_not_found_raises_error(self):
        with mock.patch('src.ChemInformant.api_helpers.get_cids_by_name', return_value=None):
            with mock.patch.object(cheminfo_api, '_looks_like_smiles', return_value=False):
                with pytest.raises(NotFoundError):
                    cheminfo_api._resolve_to_single_cid("unknown_compound")


class TestLooksLikeSmiles:

    def test_simple_smiles(self):
        assert cheminfo_api._looks_like_smiles("C1CCCCC1") == True
        assert cheminfo_api._looks_like_smiles("C(=O)O") == True
        assert cheminfo_api._looks_like_smiles("CCBr") == True

    def test_aromatic_smiles(self):
        assert cheminfo_api._looks_like_smiles("c1ccccc1") == True
        assert cheminfo_api._looks_like_smiles("c1ccc(O)cc1") == True

    def test_branched_smiles(self):
        assert cheminfo_api._looks_like_smiles("CC(C)C") == True
        assert cheminfo_api._looks_like_smiles("C(C)(C)C") == True

    def test_not_smiles(self):
        assert cheminfo_api._looks_like_smiles("caffeine") == False
        assert cheminfo_api._looks_like_smiles("aspirin") == False
        assert cheminfo_api._looks_like_smiles("2519") == True
        assert cheminfo_api._looks_like_smiles("") == False

    def test_edge_cases(self):
        assert cheminfo_api._looks_like_smiles("C") == False
        assert cheminfo_api._looks_like_smiles("O") == False
        assert cheminfo_api._looks_like_smiles("N") == False
        assert cheminfo_api._looks_like_smiles("C2") == True


class TestGetProperties:

    def test_get_properties_empty_inputs(self):
        result = cheminfo_api.get_properties([], [])
        assert result.empty

        result = cheminfo_api.get_properties(["caffeine"], [])
        assert result.empty

    def test_get_properties_unsupported_property_raises_error(self):
        with pytest.raises(ValueError, match="Unsupported properties"):
            cheminfo_api.get_properties(["caffeine"], ["invalid_property"])

    def test_get_properties_success(self):
        mock_batch_data = {2519: {"MolecularWeight": "194.19", "IUPACName": "caffeine"}}
        
        with mock.patch.object(cheminfo_api, '_resolve_to_single_cid', return_value=2519):
            with mock.patch('src.ChemInformant.api_helpers.get_batch_properties', return_value=mock_batch_data):
                with mock.patch('src.ChemInformant.api_helpers.get_cas_for_cid', return_value="58-08-2"):
                    result = cheminfo_api.get_properties(["caffeine"], ["molecular_weight", "iupac_name", "cas"])
                    
                    assert len(result) == 1
                    assert result.iloc[0]["input_identifier"] == "caffeine"
                    assert result.iloc[0]["cid"] == "2519"
                    assert result.iloc[0]["status"] == "OK"
                    assert result.iloc[0]["molecular_weight"] == "194.19"
                    assert result.iloc[0]["cas"] == "58-08-2"

    def test_get_properties_with_failure(self):
        with mock.patch.object(cheminfo_api, '_resolve_to_single_cid', side_effect=NotFoundError("test")):
            result = cheminfo_api.get_properties(["unknown"], ["molecular_weight"])
            
            assert len(result) == 1
            assert result.iloc[0]["input_identifier"] == "unknown"
            assert pd.isna(result.iloc[0]["cid"])
            assert result.iloc[0]["status"] == "NotFoundError"
            assert pd.isna(result.iloc[0]["molecular_weight"])

    def test_get_properties_mixed_success_failure(self):
        def mock_resolve(identifier):
            if identifier == "caffeine":
                return 2519
            else:
                raise NotFoundError(identifier)
        
        mock_batch_data = {2519: {"MolecularWeight": "194.19"}}
        
        with mock.patch.object(cheminfo_api, '_resolve_to_single_cid', side_effect=mock_resolve):
            with mock.patch('src.ChemInformant.api_helpers.get_batch_properties', return_value=mock_batch_data):
                result = cheminfo_api.get_properties(["caffeine", "unknown"], ["molecular_weight"])
                
                assert len(result) == 2
                assert result.iloc[0]["status"] == "OK"
                assert result.iloc[1]["status"] == "NotFoundError"


class TestGetCompound:

    def test_get_compound_success(self):
        mock_df = pd.DataFrame({
            'input_identifier': ['caffeine'],
            'cid': ['2519'],
            'status': ['OK'],
            'molecular_weight': ['194.19'],
            'cas': ['58-08-2']
        })
        
        with mock.patch.object(cheminfo_api, 'get_properties', return_value=mock_df):
            result = cheminfo_api.get_compound("caffeine")
            
            assert isinstance(result, Compound)
            assert result.input_identifier == "caffeine"
            assert result.cid == 2519

    def test_get_compound_failure_raises_error(self):
        mock_df = pd.DataFrame({
            'input_identifier': ['unknown'],
            'cid': [pd.NA],
            'status': ['NotFoundError']
        })
        
        with mock.patch.object(cheminfo_api, 'get_properties', return_value=mock_df):
            with pytest.raises(RuntimeError, match="Failed to fetch compound"):
                cheminfo_api.get_compound("unknown")

    def test_get_compound_empty_dataframe_raises_error(self):
        mock_df = pd.DataFrame()
        
        with mock.patch.object(cheminfo_api, 'get_properties', return_value=mock_df):
            with pytest.raises(RuntimeError, match="Failed to fetch compound"):
                cheminfo_api.get_compound("unknown")


class TestGetCompounds:

    def test_get_compounds_success(self):
        with mock.patch.object(cheminfo_api, 'get_compound') as mock_get_compound:
            mock_compound = Compound(input_identifier="caffeine", cid="2519", status="OK")
            mock_get_compound.return_value = mock_compound
            
            result = cheminfo_api.get_compounds(["caffeine"])
            
            assert len(result) == 1
            assert result[0] == mock_compound
            mock_get_compound.assert_called_once_with("caffeine")


class TestDrawCompound:

    def test_draw_compound_success(self):
        with mock.patch.object(cheminfo_api, '_resolve_to_single_cid', return_value=2519):
            with mock.patch('src.ChemInformant.api_helpers.get_synonyms_for_cid', return_value=["Caffeine"]):
                with mock.patch('requests.get') as mock_get:
                    mock_response = mock.Mock()
                    mock_response.status_code = 200
                    mock_response.content = b"fake_png_data"
                    mock_get.return_value = mock_response
                    
                    with mock.patch('PIL.Image.open') as mock_image_open:
                        mock_img = mock.Mock()
                        mock_image_open.return_value = mock_img
                        
                        with mock.patch('matplotlib.pyplot.show') as mock_show:
                            with mock.patch('matplotlib.pyplot.imshow') as mock_imshow:
                                with mock.patch('matplotlib.pyplot.axis') as mock_axis:
                                    with mock.patch('matplotlib.pyplot.title') as mock_title:
                                        cheminfo_api.draw_compound("caffeine")
                                        mock_show.assert_called_once()

    def test_draw_compound_image_request_fails(self):
        with mock.patch.object(cheminfo_api, '_resolve_to_single_cid', return_value=2519):
            with mock.patch('src.ChemInformant.api_helpers.get_synonyms_for_cid', return_value=["Caffeine"]):
                with mock.patch('requests.get') as mock_get:
                    mock_response = mock.Mock()
                    mock_response.status_code = 404
                    mock_response.content = b"not found"
                    mock_get.return_value = mock_response
                    
                    with mock.patch('builtins.print') as mock_print:
                        result = cheminfo_api.draw_compound("caffeine")
                        assert result is None
                        mock_print.assert_called() 