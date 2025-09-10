import tempfile
from unittest import mock

import pandas as pd
import pytest

from ChemInformant import cli
from ChemInformant.models import NotFoundError


class TestMainFetch:

    def test_main_fetch_with_table_format(self):
        test_data = pd.DataFrame({
            'input_identifier': ['caffeine'],
            'cid': ['2519'],
            'status': ['OK'],
            'cas': ['58-08-2'],
            'molecular_weight': ['194.19']
        })

        with mock.patch('sys.argv', ['chemfetch', 'caffeine', '--props', 'cas,molecular_weight']):
            with mock.patch('ChemInformant.cli.get_properties', return_value=test_data):
                with mock.patch('builtins.print') as mock_print:
                    cli.main_fetch()
                    mock_print.assert_called()

    def test_main_fetch_with_csv_format(self):
        test_data = pd.DataFrame({
            'input_identifier': ['caffeine'],
            'cid': ['2519'],
            'status': ['OK'],
            'cas': ['58-08-2']
        })

        with mock.patch('sys.argv', ['chemfetch', 'caffeine', '--format', 'csv']):
            with mock.patch('ChemInformant.cli.get_properties', return_value=test_data):
                with mock.patch('builtins.print') as mock_print:
                    cli.main_fetch()
                    mock_print.assert_called()
                    call_args = str(mock_print.call_args)
                    assert 'caffeine' in call_args

    def test_main_fetch_with_json_format(self):
        test_data = pd.DataFrame({
            'input_identifier': ['caffeine'],
            'cid': ['2519'],
            'status': ['OK']
        })

        with mock.patch('sys.argv', ['chemfetch', 'caffeine', '--format', 'json']):
            with mock.patch('ChemInformant.cli.get_properties', return_value=test_data):
                with mock.patch('builtins.print') as mock_print:
                    cli.main_fetch()
                    mock_print.assert_called()

    def test_main_fetch_with_sql_format(self):
        test_data = pd.DataFrame({
            'input_identifier': ['caffeine'],
            'cid': ['2519'],
            'status': ['OK']
        })

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            tmp_path = tmp_file.name

        with mock.patch('sys.argv', ['chemfetch', 'caffeine', '--format', 'sql', '-o', tmp_path]):
            with mock.patch('ChemInformant.cli.get_properties', return_value=test_data):
                with mock.patch('ChemInformant.cli.df_to_sql') as mock_df_to_sql:
                    with mock.patch('builtins.print') as mock_print:
                        cli.main_fetch()
                        mock_df_to_sql.assert_called_once()
                        mock_print.assert_called()

    def test_main_fetch_sql_without_output_fails(self):
        with mock.patch('sys.argv', ['chemfetch', 'caffeine', '--format', 'sql']):
            with pytest.raises(SystemExit):
                cli.main_fetch()

    def test_main_fetch_empty_dataframe(self):
        empty_df = pd.DataFrame()

        with mock.patch('sys.argv', ['chemfetch', 'caffeine']):
            with mock.patch('ChemInformant.cli.get_properties', return_value=empty_df):
                with mock.patch('builtins.print') as mock_print:
                    cli.main_fetch()
                    assert mock_print.called

    def test_main_fetch_value_error_handling(self):
        with mock.patch('sys.argv', ['chemfetch', 'caffeine']):
            with mock.patch('ChemInformant.cli.get_properties', side_effect=ValueError("Invalid property")):
                with mock.patch('builtins.print') as mock_print:
                    with pytest.raises(SystemExit) as exc_info:
                        cli.main_fetch()
                    assert exc_info.value.code == 1
                    mock_print.assert_called()

    def test_main_fetch_general_exception_handling(self):
        with mock.patch('sys.argv', ['chemfetch', 'caffeine']):
            with mock.patch('ChemInformant.cli.get_properties', side_effect=Exception("Unexpected error")):
                with mock.patch('builtins.print') as mock_print:
                    with pytest.raises(SystemExit) as exc_info:
                        cli.main_fetch()
                    assert exc_info.value.code == 1
                    mock_print.assert_called()

    def test_main_fetch_multiple_identifiers(self):
        test_data = pd.DataFrame({
            'input_identifier': ['caffeine', 'aspirin'],
            'cid': ['2519', '2244'],
            'status': ['OK', 'OK']
        })

        with mock.patch('sys.argv', ['chemfetch', 'caffeine', 'aspirin']):
            with mock.patch('ChemInformant.cli.get_properties', return_value=test_data):
                with mock.patch('builtins.print') as mock_print:
                    cli.main_fetch()
                    mock_print.assert_called()

    def test_main_fetch_custom_properties(self):
        test_data = pd.DataFrame({
            'input_identifier': ['caffeine'],
            'cid': ['2519'],
            'status': ['OK'],
            'molecular_formula': ['C8H10N4O2'],
            'xlogp': ['1.23']
        })

        with mock.patch('sys.argv', ['chemfetch', 'caffeine', '--props', 'molecular_formula,xlogp']):
            with mock.patch('ChemInformant.cli.get_properties', return_value=test_data):
                with mock.patch('builtins.print') as mock_print:
                    cli.main_fetch()
                    mock_print.assert_called()


class TestMainDraw:

    def test_main_draw_basic(self):
        with mock.patch('sys.argv', ['chemdraw', 'caffeine']):
            with mock.patch('ChemInformant.cli.draw_compound') as mock_draw:
                with mock.patch('builtins.print'):
                    cli.main_draw()
                    mock_draw.assert_called_once_with('caffeine')

    def test_main_draw_with_output_file(self):
        with mock.patch('sys.argv', ['chemdraw', 'caffeine']):
            with mock.patch('ChemInformant.cli.draw_compound') as mock_draw:
                cli.main_draw()
                mock_draw.assert_called_once()

    def test_main_draw_not_found_error(self):
        with mock.patch('sys.argv', ['chemdraw', 'invalid_compound']):
            with mock.patch('ChemInformant.cli.draw_compound', side_effect=NotFoundError('invalid_compound')):
                with mock.patch('builtins.print') as mock_print:
                    with pytest.raises(SystemExit) as exc_info:
                        cli.main_draw()
                    assert exc_info.value.code == 1
                    mock_print.assert_called()

    def test_main_draw_general_exception(self):
        with mock.patch('sys.argv', ['chemdraw', 'caffeine']):
            with mock.patch('ChemInformant.cli.draw_compound', side_effect=Exception("Drawing failed")):
                with mock.patch('builtins.print') as mock_print:
                    with pytest.raises(SystemExit) as exc_info:
                        cli.main_draw()
                    assert exc_info.value.code == 1
                    mock_print.assert_called()


class TestArgumentParsing:

    def test_fetch_help_message(self):
        with mock.patch('sys.argv', ['chemfetch', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                cli.main_fetch()
            assert exc_info.value.code == 0

    def test_draw_help_message(self):
        with mock.patch('sys.argv', ['chemdraw', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                cli.main_draw()
            assert exc_info.value.code == 0
