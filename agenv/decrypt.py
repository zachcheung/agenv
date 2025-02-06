import os
import subprocess
import tempfile
from io import StringIO

from dotenv import load_dotenv

DEFAULT_IDENTITY = os.path.expanduser("~/.age/key")


def decrypt(file: str, identity: str = "") -> str:
    """Decrypts an .age encrypted file and returns its content as a string."""
    temp_key_file_path = ""

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

    cmd = f"age -d -i '{identity}' '{file}'"

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Decryption failed: {e.stderr.strip()}") from e
    finally:
        if temp_key_file_path and os.path.exists(temp_key_file_path):
            os.remove(temp_key_file_path)


def load_age_env(envfile: str = ".env.age", identity: str = "") -> None:
    """Decrypts an .age encrypted environment file and loads it into os.environ."""
    decrypted = decrypt(envfile, identity)
    load_dotenv(stream=StringIO(decrypted))
