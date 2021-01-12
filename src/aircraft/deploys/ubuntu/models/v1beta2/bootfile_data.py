from pydantic import (
    AnyUrl,
)

from .base_model import BaseModel


class BootfileData(BaseModel):
    """
    Contains information on a bootfile (such as grub) as well as which
    PXE client architecture it applies to. For more information on PXE
    client architectures, see https://tools.ietf.org/html/rfc4578#section-2.1
    """
    client_arch: int
    image_source_url: AnyUrl
    image_sha256sum: str

    def get_path(self):
        """
        Returns the path to the file. This may be used by TFTP packaged
        deploy to determine where to save the file as well as by the
        DHCP packaged deploy to determine what value to provide in
        DHCP Option 67 (Bootfile-Name)
        """
        return self.image_source_url.path.lstrip('/')
