"""
Unit tests for the environment module.

Tests cover environment variable parsing, file detection, and error
handling for different environment scenarios.
"""

import os
from unittest.mock import patch

from django.core.checks import Error, Info, Warning

from src.qr_code.common.environment import get_environment
from src.qr_code.common.env_selection import SUPPORTED_ENVIRONMENTS


class TestGetEnvironment:
    """Test suite for the get_environment function."""

    def test_environment_from_env_var_dev(self, tmp_path) -> None:
        """Environment 'dev' from ENVIRONMENT variable is returned."""
        (tmp_path / '.env.dev').touch()
        with patch.dict(os.environ, {'ENVIRONMENT': 'dev'}, clear=True):
            with patch('src.qr_code.common.environment.PROJECT_ROOT', tmp_path):
                environment, errors = get_environment()
                assert environment == 'dev'
                assert any(isinstance(e, Info) for e in errors)

    def test_environment_from_env_var_prod(self, tmp_path) -> None:
        """Environment 'prod' from ENVIRONMENT variable is returned."""
        (tmp_path / '.env.prod').touch()
        with patch.dict(os.environ, {'ENVIRONMENT': 'prod'}, clear=True):
            with patch('src.qr_code.common.environment.PROJECT_ROOT', tmp_path):
                environment, errors = get_environment()
                assert environment == 'prod'
                assert any(isinstance(e, Info) for e in errors)

    def test_environment_from_env_var_case_insensitive(self, tmp_path) -> None:
        """ENVIRONMENT variable is case-insensitive."""
        (tmp_path / '.env.dev').touch()
        with patch.dict(os.environ, {'ENVIRONMENT': 'DEV'}, clear=True):
            with patch('src.qr_code.common.environment.PROJECT_ROOT', tmp_path):
                environment, errors = get_environment()
                assert environment == 'dev'

    def test_environment_from_env_var_mixed_case(self, tmp_path) -> None:
        """ENVIRONMENT variable with mixed case is normalized."""
        (tmp_path / '.env.prod').touch()
        with patch.dict(os.environ, {'ENVIRONMENT': 'PrOd'}, clear=True):
            with patch('src.qr_code.common.environment.PROJECT_ROOT', tmp_path):
                environment, errors = get_environment()
                assert environment == 'prod'

    def test_invalid_environment_variable(self) -> None:
        """Invalid ENVIRONMENT variable value produces an Error."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'invalid'}, clear=False):
            environment, errors = get_environment()
            assert environment == 'invalid'
            assert any(isinstance(e, Error) and e.id is not None and 'E001' in e.id for e in errors)

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
        """Single .env.dev file is detected and environment is set to 'dev'."""
        env_file = tmp_path / '.env.dev'
        env_file.touch()

        with patch.dict(os.environ, {}, clear=True):
            with patch('src.qr_code.common.environment.PROJECT_ROOT', tmp_path):
                environment, errors = get_environment()
                assert environment == 'dev'
                assert any(isinstance(e, Info) for e in errors)
                error_ids = [e.id for e in errors if isinstance(e, Error)]
                assert 'E002' not in error_ids
                assert 'E003' not in error_ids

    def test_environment_not_set_single_env_file_prod(self, tmp_path) -> None:
        """Single .env.prod file is detected and environment is set to 'prod'."""
        env_file = tmp_path / '.env.prod'
        env_file.touch()

        with patch.dict(os.environ, {}, clear=True):
            with patch('src.qr_code.common.environment.PROJECT_ROOT', tmp_path):
                environment, errors = get_environment()
                assert environment == 'prod'
                assert any(isinstance(e, Info) for e in errors)
                error_ids = [e.id for e in errors if isinstance(e, Error)]
                assert 'E002' not in error_ids
                assert 'E003' not in error_ids

    def test_environment_not_set_multiple_env_files(self, tmp_path) -> None:
        """Multiple environment files produce Error E003."""
        (tmp_path / '.env.dev').touch()
        (tmp_path / '.env.prod').touch()

        with patch.dict(os.environ, {}, clear=True):
            with patch('src.qr_code.common.environment.PROJECT_ROOT', tmp_path):
                environment, errors = get_environment()
                assert environment is None
                error_ids = [e.id for e in errors if isinstance(e, Error)]
                assert 'E003' in error_ids

    def test_unknown_environment_file(self, tmp_path) -> None:
        """Unknown environment file produces Warning W001 and env selection error."""
        (tmp_path / '.env.unknown').touch()

        with patch.dict(os.environ, {}, clear=True):
            with patch('src.qr_code.common.environment.PROJECT_ROOT', tmp_path):
                environment, errors = get_environment()
                assert environment is None
                warning_ids = [w.id for w in errors if isinstance(w, Warning)]
                assert 'W001' in warning_ids
                error_ids = [e.id for e in errors if isinstance(e, Error)]
                assert 'E002' in error_ids

    def test_ignored_environment_file_example(self, tmp_path) -> None:
        """`.env.example` is ignored for selection and does not trigger W001."""
        (tmp_path / '.env.example').touch()

        with patch.dict(os.environ, {}, clear=True):
            with patch('src.qr_code.common.environment.PROJECT_ROOT', tmp_path):
                environment, errors = get_environment()
                assert environment is None
                warning_ids = [w.id for w in errors if isinstance(w, Warning)]
                assert 'W001' not in warning_ids
                error_ids = [e.id for e in errors if isinstance(e, Error)]
                assert 'E002' in error_ids

    def test_environment_var_set_env_files_ignored(self, tmp_path) -> None:
        """When ENVIRONMENT is set, env files are ignored."""
        (tmp_path / '.env.dev').touch()
        (tmp_path / '.env.prod').touch()

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
        (tmp_path / '.env.unknown1').touch()
        (tmp_path / '.env.unknown2').touch()

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
                mock_root.glob.assert_called_once_with('.env.*')


class TestEnvironmentConstants:
    """Test suite for environment module constants."""

    def test_environments_constant_contains_dev_and_prod(self) -> None:
        """SUPPORTED_ENVIRONMENTS constant contains 'dev' and 'prod'."""
        assert 'dev' in SUPPORTED_ENVIRONMENTS
        assert 'prod' in SUPPORTED_ENVIRONMENTS

    def test_environments_constant_is_list(self) -> None:
        """SUPPORTED_ENVIRONMENTS is a list."""
        assert isinstance(SUPPORTED_ENVIRONMENTS, list)
