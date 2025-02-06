# agenv

A simple Python package for securely loading environment variables from age encrypted file.

## Installation

```sh
pip install agenv
```

> [!NOTE]
> [age](https://github.com/FiloSottile/age#installation) must be installed separately, as there is no native Python implementation of age.

## Usage

#### Loading Environment Variables

```python
from agenv import load_age_env

# Decrypts and loads environment variables from a .env.age file
load_age_env(".env.age")
```

#### Decrypting and Loading YAML Data

```python
import yaml
from agenv import decrypt

# Decrypts the .age encrypted file and loads the content as a YAML object
yaml_str = decrypt("database.yml.age")
data = yaml.safe_load(yaml_str)
print(data)
```

### Identity Key Selection Order

agenv determines the age identity key in the following order:

1. The `identity` parameter provided to `load_age_env()`
2. The `AGE_SECRET_KEY` environment variable
3. The `AGE_SECRET_KEY_FILE` environment variable (path to key file)
4. The default key file: `~/.age/key`

If no valid identity is found, decryption will fail.

## License

[MIT](LICENSE)
