from unittest import TestCase


from aircraft.deploys.ubuntu.models.v1beta3 import TftpData


class TftpDataTest(TestCase):

    def test__it_sets_sftp_root_dir_if_not_provided(self):
        tftp = TftpData(
            hostname='1.1.1.1',
            root_dir='/some/path'
        )

        assert tftp.sftp_root_dir == tftp.root_dir

    def test__it_does_not_overwrite_sftp_root_dir_if_provided(self):
        sftp_root_dir = '/a/different/path'

        tftp = TftpData(
            hostname='1.1.1.1',
            root_dir='/some/path',
            sftp_root_dir=sftp_root_dir,
        )

        assert str(tftp.sftp_root_dir) == sftp_root_dir
