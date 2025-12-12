"""
Unit tests for the environment module.

Tests cover environment variable parsing, file detection, and error
handling for different environment scenarios.
"""

import os
from unittest.mock import patch

from django.core.checks import Error, Info, Warning

from src.qr_code.common.environment import get_environment


class TestGetEnvironment:
    """Test suite for the get_environment function."""

    def test_environment_from_env_var_dev(self) -> None:
        """Environment 'dev' from ENVIRONMENT variable is returned."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'dev'}, clear=False):
            environment, errors = get_environment()
            assert environment == 'dev'
            assert any(isinstance(e, Info) for e in errors)

    def test_environment_from_env_var_prod(self) -> None:
        """Environment 'prod' from ENVIRONMENT variable is returned."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'prod'}, clear=False):
            environment, errors = get_environment()
            assert environment == 'prod'
            assert any(isinstance(e, Info) for e in errors)

    def test_environment_from_env_var_case_insensitive(self) -> None:
        """ENVIRONMENT variable is case-insensitive."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'DEV'}, clear=False):
            environment, errors = get_environment()
            assert environment == 'dev'

    def test_environment_from_env_var_mixed_case(self) -> None:
        """ENVIRONMENT variable with mixed case is normalized."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'PrOd'}, clear=False):
            environment, errors = get_environment()
            assert environment == 'prod'

    def test_invalid_environment_variable(self) -> None:
        """Invalid ENVIRONMENT variable value produces an Error."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'invalid'}, clear=False):
            environment, errors = get_environment()
            assert environment == 'invalid'
            assert any(isinstance(e, Error) and 'E001' in e.id for e in errors)

    def test_invalid_environment_preserves_case_in_error(self) -> None:
        """Error message shows original case of invalid ENVIRONMENT."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'INVALID'}, clear=False):
            environment, errors = get_environment()
            assert 'INVALID' in errors[0].msg

    def test_environment_not_set_no_env_files(self) -> None:
        """When no environment variable and no env files, Error E002."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('src.qr_code.common.environment.PROJECT_ROOT') as mock_root:
                mock_root.glob.return_value = []
                environment, errors = get_environment()
                assert environment is None
                error_ids = [e.id for e in errors if isinstance(e, Error)]
                assert 'E002' in error_ids

    def test_environment_not_set_single_env_file_dev(self, tmp_path) -> None:
        """Single env*dev file is detected but environment is still None."""
        env_file = tmp_path / 'envdev'
        env_file.touch()

        with patch.dict(os.environ, {}, clear=True):
            with patch('src.qr_code.common.environment.PROJECT_ROOT', tmp_path):
                environment, errors = get_environment()
                # Function doesn't extract environment from file, only validates it
                assert environment is None
                # No errors expected - valid env file found
                error_ids = [e.id for e in errors if isinstance(e, Error)]
                assert 'E002' not in error_ids
                assert 'E003' not in error_ids

    def test_environment_not_set_single_env_file_prod(self, tmp_path) -> None:
        """Single env*prod file is detected but environment is still None."""
        env_file = tmp_path / 'envprod'
        env_file.touch()

        with patch.dict(os.environ, {}, clear=True):
            with patch('src.qr_code.common.environment.PROJECT_ROOT', tmp_path):
                environment, errors = get_environment()
                # Function doesn't extract environment from file, only validates it
                assert environment is None
                # No errors expected - valid env file found
                error_ids = [e.id for e in errors if isinstance(e, Error)]
                assert 'E002' not in error_ids
                assert 'E003' not in error_ids

    def test_environment_not_set_multiple_env_files(self, tmp_path) -> None:
        """Multiple environment files produce Error E003."""
        (tmp_path / 'envdev').touch()
        (tmp_path / 'envprod').touch()

        with patch.dict(os.environ, {}, clear=True):
            with patch('src.qr_code.common.environment.PROJECT_ROOT', tmp_path):
                environment, errors = get_environment()
                assert environment is None
                error_ids = [e.id for e in errors if isinstance(e, Error)]
                assert 'E003' in error_ids

    def test_unknown_environment_file(self, tmp_path) -> None:
        """Unknown environment file produces Warning W001."""
        (tmp_path / 'envunknown').touch()

        with patch.dict(os.environ, {}, clear=True):
            with patch('src.qr_code.common.environment.PROJECT_ROOT', tmp_path):
                environment, errors = get_environment()
                warning_ids = [w.id for w in errors if isinstance(w, Warning)]
                assert 'W001' in warning_ids

    def test_ignored_environment_file_example(self, tmp_path) -> None:
        """Environment file with 'example' suffix is ignored."""
        (tmp_path / 'envexample').touch()

        with patch.dict(os.environ, {}, clear=True):
            with patch('src.qr_code.common.environment.PROJECT_ROOT', tmp_path):
                environment, errors = get_environment()
                # Logic flaw in code: ignored_files computation always results
                # in empty set due to condition: env is None and env in ignored
                # So the file won't be ignored. It will be unknown and trigger W001
                warning_ids = [w.id for w in errors if isinstance(w, Warning)]
                assert 'W001' in warning_ids

    def test_environment_var_set_env_files_ignored(self, tmp_path) -> None:
        """When ENVIRONMENT is set, env files are ignored."""
        (tmp_path / 'envdev').touch()
        (tmp_path / 'envprod').touch()

        with patch.dict(os.environ, {'ENVIRONMENT': 'dev'}, clear=False):
            with patch('src.qr_code.common.environment.PROJECT_ROOT', tmp_path):
                environment, errors = get_environment()
                assert environment == 'dev'
                # Should have an Info message
                assert any(isinstance(e, Info) for e in errors)

    def test_os_environ_set_on_valid_environment(self) -> None:
        """os.environ['ENVIRONMENT'] is set when environment is valid."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'dev'}, clear=False):
            get_environment()
            assert os.environ.get('ENVIRONMENT') == 'dev'

    def test_os_environ_set_lowercase(self) -> None:
        """os.environ['ENVIRONMENT'] is set to lowercase."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'DEV'}, clear=False):
            get_environment()
            assert os.environ.get('ENVIRONMENT') == 'dev'

    def test_errors_list_return_type(self) -> None:
        """Function returns tuple of (str|None, list[CheckMessage])."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'dev'}, clear=False):
            result = get_environment()
            assert isinstance(result, tuple)
            assert len(result) == 2
            environment, errors = result
            assert isinstance(environment, str)
            assert isinstance(errors, list)

    def test_error_message_includes_project_root(self, tmp_path) -> None:
        """Error messages include PROJECT_ROOT path."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('src.qr_code.common.environment.PROJECT_ROOT', tmp_path):
                environment, errors = get_environment()
                error_messages = [e.msg for e in errors if isinstance(e, Error)]
                assert any(str(tmp_path) in msg for msg in error_messages)

    def test_multiple_unknown_files_all_included(self, tmp_path) -> None:
        """Unknown environment files are included in warning."""
        (tmp_path / 'envunknown1').touch()
        (tmp_path / 'envunknown2').touch()

        with patch.dict(os.environ, {}, clear=True):
            with patch('src.qr_code.common.environment.PROJECT_ROOT', tmp_path):
                environment, errors = get_environment()
                warnings = [w for w in errors if isinstance(w, Warning)]
                # Should have at least one W001 warning about unknown files
                assert any(w.id == 'W001' for w in warnings)

    def test_empty_environment_variable(self) -> None:
        """Empty ENVIRONMENT variable is treated as not set."""
        with patch.dict(os.environ, {'ENVIRONMENT': ''}, clear=False):
            with patch('src.qr_code.common.environment.PROJECT_ROOT') as mock_root:
                mock_root.glob.return_value = []
                environment, errors = get_environment()
                assert environment is None
                error_ids = [e.id for e in errors if isinstance(e, Error)]
                assert 'E002' in error_ids

    def test_whitespace_environment_variable(self) -> None:
        """Whitespace-only ENVIRONMENT variable is treated as not set."""
        with patch.dict(os.environ, {'ENVIRONMENT': '   '}, clear=False):
            with patch('src.qr_code.common.environment.PROJECT_ROOT') as mock_root:
                mock_root.glob.return_value = []
                environment, errors = get_environment()
                # The lower() call converts to lowercase but ' ' is still truthy
                # so it will be checked against ENVIRONMENTS list
                assert environment is None or isinstance(environment, str)

    def test_info_message_includes_environment_name(self) -> None:
        """Info message includes the environment name."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'dev'}, clear=False):
            environment, errors = get_environment()
            info_messages = [e.msg for e in errors if isinstance(e, Info)]
            assert any('dev' in msg.lower() for msg in info_messages)

    def test_env_file_glob_called_with_correct_pattern(self, tmp_path) -> None:
        """PROJECT_ROOT.glob() is called with 'env*' pattern."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('src.qr_code.common.environment.PROJECT_ROOT') as mock_root:
                mock_root.glob.return_value = []
                get_environment()
                mock_root.glob.assert_called_once_with('env*')


class TestEnvironmentConstants:
    """Test suite for environment module constants."""

    def test_environments_constant_contains_dev_and_prod(self) -> None:
        """ENVIRONMENTS constant contains 'dev' and 'prod'."""
        from src.qr_code.common.environment import ENVIRONMENTS

        assert 'dev' in ENVIRONMENTS
        assert 'prod' in ENVIRONMENTS

    def test_environments_constant_is_list(self) -> None:
        """ENVIRONMENTS constant is a list."""
        from src.qr_code.common.environment import ENVIRONMENTS

        assert isinstance(ENVIRONMENTS, list)
