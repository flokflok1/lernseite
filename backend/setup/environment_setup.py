"""
LernsystemX Setup - Environment Configuration

Handles environment selection and .env file generation:
- Choose between development and production
- Copy appropriate .env.example template
- Generate secure random keys
- Validate environment configuration

ISO/IEC/IEEE 26515:2018 compliant
"""

import os
import secrets
import string
from pathlib import Path
from typing import Dict, Tuple


class EnvironmentSetup:
    """Handle environment configuration and .env file generation"""

    BACKEND_DIR = Path(__file__).parent.parent
    ENV_FILE = BACKEND_DIR / '.env'
    ENV_DEV_TEMPLATE = BACKEND_DIR / '.env.example'
    ENV_PROD_TEMPLATE = BACKEND_DIR / '.env.production.example'

    @staticmethod
    def generate_secret_key(length: int = 64) -> str:
        """
        Generate a cryptographically secure random key

        Args:
            length: Length of the key (default 64 characters)

        Returns:
            Random hex string of specified length
        """
        return secrets.token_hex(length // 2)

    @staticmethod
    def generate_random_string(length: int = 32, include_special: bool = False) -> str:
        """
        Generate a random alphanumeric string

        Args:
            length: Length of the string
            include_special: Include special characters

        Returns:
            Random string
        """
        alphabet = string.ascii_letters + string.digits
        if include_special:
            alphabet += string.punctuation

        return ''.join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def env_exists() -> bool:
        """Check if .env file already exists"""
        return EnvironmentSetup.ENV_FILE.exists()

    @staticmethod
    def get_template_path(environment: str) -> Path:
        """
        Get the appropriate template file path

        Args:
            environment: 'development' or 'production'

        Returns:
            Path to template file

        Raises:
            ValueError: If environment is invalid
        """
        if environment == 'development':
            return EnvironmentSetup.ENV_DEV_TEMPLATE
        elif environment == 'production':
            return EnvironmentSetup.ENV_PROD_TEMPLATE
        else:
            raise ValueError(f"Invalid environment: {environment}. Must be 'development' or 'production'")

    @staticmethod
    def read_template(environment: str) -> str:
        """
        Read environment template file

        Args:
            environment: 'development' or 'production'

        Returns:
            Template content as string

        Raises:
            FileNotFoundError: If template doesn't exist
            ValueError: If environment is invalid
        """
        template_path = EnvironmentSetup.get_template_path(environment)

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def generate_env_content(environment: str, custom_values: Dict[str, str] = None) -> str:
        """
        Generate .env file content from template with secure keys

        Args:
            environment: 'development' or 'production'
            custom_values: Optional dict of custom key-value pairs to replace

        Returns:
            .env file content with generated keys

        Key replacements:
        - SECRET_KEY: 64-char hex string
        - JWT_SECRET_KEY: 64-char hex string
        - TOKEN_SALT: 32-char hex string
        """
        template = EnvironmentSetup.read_template(environment)

        # Generate secure keys
        secret_key = EnvironmentSetup.generate_secret_key(64)
        jwt_secret = EnvironmentSetup.generate_secret_key(64)
        token_salt = EnvironmentSetup.generate_secret_key(32)

        # Replace placeholder values
        replacements = {
            'your-secret-key-change-this-in-production': secret_key,
            'CHANGE_THIS_TO_RANDOM_SECRET_KEY': secret_key,
            'your-jwt-secret-key-change-this': jwt_secret,
            'CHANGE_THIS_TO_RANDOM_JWT_SECRET': jwt_secret,
            'CHANGE_THIS_TO_RANDOM_SALT': token_salt,
        }

        # Add custom values if provided
        if custom_values:
            replacements.update(custom_values)

        # Apply replacements
        content = template
        for old_value, new_value in replacements.items():
            content = content.replace(old_value, new_value)

        return content

    @staticmethod
    def write_env_file(content: str) -> bool:
        """
        Write .env file to disk

        Args:
            content: .env file content

        Returns:
            True if successful

        Raises:
            IOError: If file cannot be written
        """
        try:
            with open(EnvironmentSetup.ENV_FILE, 'w', encoding='utf-8') as f:
                f.write(content)

            # Set restrictive permissions (owner read/write only)
            if os.name != 'nt':  # Unix/Linux
                os.chmod(EnvironmentSetup.ENV_FILE, 0o600)

            return True

        except Exception as e:
            raise IOError(f"Failed to write .env file: {str(e)}")

    @staticmethod
    def setup_environment(environment: str, custom_values: Dict[str, str] = None, overwrite: bool = False) -> Tuple[bool, str]:
        """
        Complete environment setup process

        Args:
            environment: 'development' or 'production'
            custom_values: Optional custom values to include
            overwrite: Whether to overwrite existing .env file

        Returns:
            Tuple of (success: bool, message: str)

        Steps:
        1. Check if .env already exists
        2. Read appropriate template
        3. Generate secure keys
        4. Apply replacements
        5. Write .env file
        """
        try:
            # Check if .env exists
            if EnvironmentSetup.env_exists() and not overwrite:
                return False, ".env file already exists. Use overwrite=True to replace it."

            # Validate environment
            if environment not in ['development', 'production']:
                return False, f"Invalid environment: {environment}"

            # Generate content
            content = EnvironmentSetup.generate_env_content(environment, custom_values)

            # Write file
            EnvironmentSetup.write_env_file(content)

            return True, f"Environment configured successfully for {environment}"

        except FileNotFoundError as e:
            return False, f"Template file not found: {str(e)}"

        except IOError as e:
            return False, f"Failed to write .env file: {str(e)}"

        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    @staticmethod
    def validate_env() -> Tuple[bool, list]:
        """
        Validate existing .env file

        Returns:
            Tuple of (is_valid: bool, issues: list)

        Checks:
        - .env file exists
        - Required variables are set
        - No placeholder values remain
        """
        issues = []

        # Check if .env exists
        if not EnvironmentSetup.env_exists():
            return False, ["No .env file found"]

        # Read .env
        with open(EnvironmentSetup.ENV_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for placeholder values
        placeholders = [
            'your-secret-key-change-this',
            'CHANGE_THIS_TO_RANDOM',
            'your-jwt-secret-key',
            'username:password@localhost',
        ]

        for placeholder in placeholders:
            if placeholder in content:
                issues.append(f"Placeholder value found: {placeholder}")

        # Check for required variables
        required_vars = [
            'SECRET_KEY',
            'JWT_SECRET_KEY',
            'DATABASE_URL',
            'REDIS_URL',
        ]

        for var in required_vars:
            if f"{var}=" not in content:
                issues.append(f"Missing required variable: {var}")

        is_valid = len(issues) == 0
        return is_valid, issues

    @staticmethod
    def get_environment_info() -> Dict[str, any]:
        """
        Get current environment information

        Returns:
            Dict with environment details
        """
        env_exists = EnvironmentSetup.env_exists()
        is_valid = False
        issues = []

        if env_exists:
            is_valid, issues = EnvironmentSetup.validate_env()

        return {
            'env_file_exists': env_exists,
            'env_file_path': str(EnvironmentSetup.ENV_FILE),
            'is_valid': is_valid,
            'issues': issues,
            'templates_available': {
                'development': EnvironmentSetup.ENV_DEV_TEMPLATE.exists(),
                'production': EnvironmentSetup.ENV_PROD_TEMPLATE.exists(),
            }
        }
