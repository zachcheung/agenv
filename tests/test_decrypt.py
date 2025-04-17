import os
import subprocess
import pytest
from unittest.mock import patch

from agenv import load_age_env


@pytest.fixture(scope="module")
def generate_age_key_and_env():
    """Fixture to generate an age key and encrypted .env.age file for testing."""

    # Step 1: Generate an age key
    key_file = "test_key.txt"
    subprocess.run(["age-keygen", "-o", key_file], check=True)

    # Step 2: Prepare environment variables as a string (instead of using a file)
    env_content = "SECRET_KEY=some-secret-value\n"

    # Step 3: Encrypt the content using the key via stdin
    encrypted_file = ".env.age"
    subprocess.run(
        ["age", "-e", "-i", key_file, "-o", encrypted_file],
        input=env_content.encode(),  # Pass the content via stdin
        check=True
    )

    yield encrypted_file, key_file

    # Cleanup after tests
    os.remove(encrypted_file)
    os.remove(key_file)


@pytest.fixture
def mock_env_vars():
    """Fixture to clear AGE_SECRET_KEY and AGE_SECRET_KEY_FILE between tests."""
    with patch.dict(os.environ, {}, clear=True):
        yield


def test_load_with_age_secret_key(mock_env_vars, generate_age_key_and_env):
    """Test loading environment variables when AGE_SECRET_KEY is set."""
    # Set the AGE_SECRET_KEY from the generated key for this test
    _, key_file = generate_age_key_and_env
    with open(key_file, "r") as f:
        age_secret_key = f.readlines()[-1].strip()  # Get the last line of the key file

    os.environ["AGE_SECRET_KEY"] = age_secret_key  # Set AGE_SECRET_KEY for the test

    encrypted_file, _ = generate_age_key_and_env
    try:
        load_age_env(encrypted_file)
        # After loading, check that the SECRET_KEY is set in os.environ
        assert os.environ["SECRET_KEY"] == "some-secret-value", "SECRET_KEY was not set correctly"
    except Exception as e:
        pytest.fail(f"Decryption failed with AGE_SECRET_KEY: {e}")


def test_load_with_age_secret_key_file(mock_env_vars, generate_age_key_and_env):
    """Test loading environment variables when AGE_SECRET_KEY_FILE is set."""
    encrypted_file, key_file = generate_age_key_and_env
    os.environ["AGE_SECRET_KEY_FILE"] = key_file
    try:
        load_age_env(encrypted_file)
        # After loading, check that the SECRET_KEY is set in os.environ
        assert os.environ["SECRET_KEY"] == "some-secret-value", "SECRET_KEY was not set correctly"
    except Exception as e:
        pytest.fail(f"Decryption failed with AGE_SECRET_KEY_FILE: {e}")


def test_load_with_explicit_key_file(mock_env_vars, generate_age_key_and_env):
    """Test loading environment variables when an explicit key file is provided."""
    encrypted_file, key_file = generate_age_key_and_env
    try:
        load_age_env(encrypted_file, key_file)  # Explicit key file path
        # After loading, check that the SECRET_KEY is set in os.environ
        assert os.environ["SECRET_KEY"] == "some-secret-value", "SECRET_KEY was not set correctly"
    except Exception as e:
        pytest.fail(f"Decryption failed with explicit key file: {e}")


def test_load_without_any_key(mock_env_vars, generate_age_key_and_env):
    """Test loading environment variables when no key is provided and AGE_SECRET_KEY_FILE is set."""
    encrypted_file, key_file = generate_age_key_and_env
    os.environ["AGE_SECRET_KEY_FILE"] = key_file
    try:
        load_age_env()
        # After loading, check that the SECRET_KEY is set in os.environ
        assert os.environ["SECRET_KEY"] == "some-secret-value", "SECRET_KEY was not set correctly"
    except Exception as e:
        pytest.fail(f"Decryption failed with no key set: {e}")

def test_load_with_file_object(mock_env_vars, generate_age_key_and_env):
    """Test loading environment variables when the encrypted file is passed as a file object."""
    encrypted_file, key_file = generate_age_key_and_env
    os.environ["AGE_SECRET_KEY_FILE"] = key_file

    try:
        with open(encrypted_file, "r") as f:
            load_age_env(f)  # Pass file object instead of path
        assert os.environ["SECRET_KEY"] == "some-secret-value", "SECRET_KEY was not set correctly"
    except Exception as e:
        pytest.fail(f"Decryption failed with file object: {e}")
