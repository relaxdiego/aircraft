import pytest
from unittest import TestCase


from aircraft.deploys.ubuntu.models.v1beta3 import BootfileData


class BootFileDataTest(TestCase):

    def test__it_requires_the_client_name_field(self):
        with pytest.raises(ValueError):
            BootfileData(
                client_arch=1,
                image_source_url="http://some.domain.com/some/path",
                image_sha256sum="someshahere",
            )

    def test__it_returns_the_correct_expected_path(self):
        the_path = 'some/path/to/a/file.txt'

        bootfile = BootfileData(
            client_name="some-client",
            client_arch=1,
            image_source_url=f"http://some.domain.com/{the_path}",
            image_sha256sum="someshahere",
        )

        assert str(bootfile.get_path()) == the_path

    def test__it_accepts_an_integer_for_the_client_arch_field(self):
        BootfileData(
            client_name="some-client",
            client_arch=1,
            image_source_url="http://some.domain.com/some/path",
            image_sha256sum="someshahere",
        )

    def test__it_accepts_a_string_for_the_client_arch_field(self):
        BootfileData(
            client_name="some-client",
            client_arch='some-client-arch-substring',
            image_source_url="http://some.domain.com/some/path",
            image_sha256sum="someshahere",
        )
