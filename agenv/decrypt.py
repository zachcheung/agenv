import os
import subprocess
import tempfile
from io import StringIO
from typing import Union, IO

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

DEFAULT_IDENTITY = os.path.expanduser("~/.age/age.key")


def decrypt(file: Union[str, IO], identity: str = "") -> str:
    """Decrypts an .age encrypted file and returns its content as a string.

    Args:
        file: A path to the .age file or a file-like object.
        identity: Optional path to an age identity key file.

    Returns:
        The decrypted content as a string.
    """
    temp_key_file_path, file_path = "", ""

    if not identity:
        age_secret_key = os.getenv("AGE_SECRET_KEY")
        if age_secret_key:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as fp:
                fp.write(age_secret_key)
                temp_key_file_path = fp.name
                identity = temp_key_file_path
        else:
            age_secret_key_file = os.getenv("AGE_SECRET_KEY_FILE")
            if age_secret_key_file:
                identity = age_secret_key_file
            else:
                identity = DEFAULT_IDENTITY

    if isinstance(file, str):
        file_path = file
    elif hasattr(file, "name"):
        file_path = file.name
    else:
        raise TypeError("file must be a path or a file-like object with a 'name' attribute")

    cmd = ["age", "-d", "-i", identity, file_path]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Decryption failed: {e.stderr.strip()}") from e
    finally:
        if temp_key_file_path and os.path.exists(temp_key_file_path):
            os.remove(temp_key_file_path)


def load_age_env(envfile: str = ".env.age", identity: str = "") -> None:
    """Decrypts an .age encrypted environment file and loads it into os.environ."""
    if not DOTENV_AVAILABLE:
        raise ImportError(
            "The 'python-dotenv' package is required to use load_age_env. "
            "Install it with `pip install agenv[dotenv]`."
        )

    decrypted = decrypt(envfile, identity)
    load_dotenv(stream=StringIO(decrypted))
