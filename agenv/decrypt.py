import os
import subprocess
from io import StringIO

from dotenv import load_dotenv

DEFAULT_IDENTITY = os.path.expanduser("~/.age/key")

def decrypt(infile: str, identity: str = "") -> str:
    """Decrypts an .age encrypted file and returns its content as a string."""
    if not identity:
        age_secret_key = os.getenv("AGE_SECRET_KEY")
        if age_secret_key:
            identity = f"<(echo {age_secret_key})"
        else:
            age_secret_key_file = os.getenv("AGE_SECRET_KEY_FILE")
            if age_secret_key_file:
                identity = age_secret_key_file
            else:
                identity = DEFAULT_IDENTITY

    cmd = f"age -d -i {identity} '{infile}'"

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Decryption failed: {e.stderr.strip()}") from e

def load_age_env(envfile: str = ".env.age", identity: str = "") -> None:
    """Decrypts an .age encrypted environment file and loads it into os.environ."""
    decrypted = decrypt(envfile, identity)
    load_dotenv(stream=StringIO(decrypted))
