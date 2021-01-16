from unittest import TestCase

from aircraft.deploys.ubuntu.models.v1beta3 import HttpData


class HttpDataTest(TestCase):

    def test__it_sets_sftp_root_dir_if_not_provided(self):
        http = HttpData(
            hostname='1.1.1.1',
            root_dir='/some/path'
        )

        assert http.sftp_root_dir == http.root_dir

    def test__it_does_not_overwrite_sftp_root_dir_if_provided(self):
        sftp_root_dir = '/a/different/path'

        http = HttpData(
            hostname='1.1.1.1',
            root_dir='/some/path',
            sftp_root_dir=sftp_root_dir,
        )

        assert str(http.sftp_root_dir) == sftp_root_dir
