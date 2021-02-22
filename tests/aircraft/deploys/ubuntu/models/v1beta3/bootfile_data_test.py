import pytest
from unittest import TestCase
from uuid import uuid4


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

    def test__it_requires_client_arch_xor_dhcp_macs_to_be_set(self):
        # Neither client_arc nor dhcp_macs are set
        with pytest.raises(ValueError):
            BootfileData(
                client_name="some-client",
                image_source_url="http://some.domain.com/some/path",
                image_sha256sum="someshahere",
            )

        # client_arc is set
        BootfileData(
            client_name="some-client",
            client_arch='some-client-arch-substring',
            image_source_url="http://some.domain.com/some/path",
            image_sha256sum="someshahere",
        )

        # dhcp_mac is set
        BootfileData(
            client_name="some-client",
            dhcp_macs=['b8:27:eb:*:*:*', 'dc:a6:32:*:*:*', 'e4:5f:01:*:*:*'],
            image_source_url="http://some.domain.com/some/path",
            image_sha256sum="someshahere",
        )

    def test__it_requires_colon_hexadecimal_notation_for_dhcp_macs(self):
        with pytest.raises(ValueError):
            BootfileData(
                client_name="some-client",
                dhcp_macs=['b8:27:eb:not:a:mac:address'],
                image_source_url="http://some.domain.com/some/path",
                image_sha256sum="someshahere",
            )

    def test__accepts_valid_macs_using_colon_hex_notation(self):
        valid_macs = ['b8:27:eb:dc:a6:32', 'e4:5f:01:aa:bb:cc']

        data = BootfileData(
            client_name="some-client",
            dhcp_macs=valid_macs,
            image_source_url="http://some.domain.com/some/path",
            image_sha256sum="someshahere",
        )

        assert data.dhcp_macs == valid_macs

    def test__accepts_macs_with_wildcards_for_last_3_octets(self):
        valid_macs = ['b8:27:eb:*:*:*', 'e4:5f:01:*:*:*']

        data = BootfileData(
            client_name="some-client",
            dhcp_macs=valid_macs,
            image_source_url="http://some.domain.com/some/path",
            image_sha256sum="someshahere",
        )

        assert data.dhcp_macs == valid_macs

    def test__it_allows_a_single_wildcard_for_each_of_the_last_3_octets(self):
        with pytest.raises(ValueError):
            BootfileData(
                client_name="some-client",
                dhcp_macs=['b8:27:eb:**:*:*'],
                image_source_url="http://some.domain.com/some/path",
                image_sha256sum="someshahere",
            )

        with pytest.raises(ValueError):
            BootfileData(
                client_name="some-client",
                dhcp_macs=['b8:27:eb:*:**:*'],
                image_source_url="http://some.domain.com/some/path",
                image_sha256sum="someshahere",
            )

        with pytest.raises(ValueError):
            BootfileData(
                client_name="some-client",
                dhcp_macs=['b8:27:eb:*:*:**'],
                image_source_url="http://some.domain.com/some/path",
                image_sha256sum="someshahere",
            )

    def test__it_allows_setting_dhcp_options(self):
        dhcp_options = {
            43: str(uuid4())
        }

        bootfile = BootfileData(
            client_name="some-client",
            client_arch=1,
            dhcp_options=dhcp_options,
            image_source_url="http://some.domain.com/the/path",
            image_sha256sum="someshahere",
        )

        assert bootfile.dhcp_options == dhcp_options
