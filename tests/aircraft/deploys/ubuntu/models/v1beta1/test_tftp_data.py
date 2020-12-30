from unittest import TestCase


from aircraft.deploys.ubuntu.models.v1beta1 import TftpData


class TftpDataTests(TestCase):

    def test__it_sets_sftp_root_dir_if_not_provided(self):
        tftp = TftpData(
            hostname='1.1.1.1',
            root_dir='/some/path'
        )

        assert tftp.sftp_root_dir == tftp.root_dir
