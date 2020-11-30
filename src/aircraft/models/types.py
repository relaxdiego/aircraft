import os
from pathlib import Path
import privy

from aircraft import get_deployspec_path


# TODO: Support RFC-1808-compliant URLs. The implementation can be a naive
#       one initially where it fetches values each time a URL is encountered.
#       A later optimization may be done by caching the value of a static URL
#       during first encounter at runtime so as to avoid multiple fetches for
#       the same value. Consider though that this caching may be outside the
#       scope of the library and can be left to the underlying network stack.
#       Caching is a whole can of worms, after all.

# Ref: https://pydantic-docs.helpmanual.io/usage/types/#custom-data-types
class StringOrLocator(str):
    """
    Custom pydantic data type used to accept a key value that may be a
    string literal or it may be a variable name in the form of
    [secrets|vars]/name_of_variable.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.fetch_if_locator
        yield cls.coerce_str

    @classmethod
    def coerce_str(cls, data):
        return str(data)

    @classmethod
    def fetch_if_locator(cls, string_or_locator):
        if str(string_or_locator).startswith(("secrets/", "vars/")):
            data = cls._fetch_variable(string_or_locator)
        else:
            data = string_or_locator

        return data

    @classmethod
    def _get_secret_key(cls):
        base_path = Path(os.environ['AIRCRAFT_DEPLOYSPEC'])
        with open(base_path / "cluster_id") as cluster_id_fh:
            cluster_id = cluster_id_fh.readline()

        secret_keys_base_path = Path().home() / '.local' / 'aircraft' / 'secret_keys'
        with open(secret_keys_base_path / cluster_id) as secret_key_fh:
            secret_key = secret_key_fh.read()

        return secret_key

    @classmethod
    def _fetch_variable(cls, rel_path):
        base_path = get_deployspec_path()
        with open(base_path / rel_path) as variable_fh:
            data = variable_fh.read()

        if str(rel_path).startswith("secrets/"):
            # TODO: We'll need to create CLI commands secret and secret key CRUD
            data = privy.peek(data, cls._get_secret_key())

        return data
