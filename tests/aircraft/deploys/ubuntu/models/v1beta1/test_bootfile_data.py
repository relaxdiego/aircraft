from unittest import TestCase


from aircraft.deploys.ubuntu.models.v1beta1 import BootfileData


class BootFileDataTest(TestCase):

    def test__it_returns_the_correct_expected_path(self):
        the_path = 'some/path/to/a/file.txt'

        bootfile = BootfileData(
            client_arch=1,
            image_source_url=f"http://some.domain.com/{the_path}",
            image_sha256sum="someshahere",
        )

        assert str(bootfile.get_path()) == the_path
