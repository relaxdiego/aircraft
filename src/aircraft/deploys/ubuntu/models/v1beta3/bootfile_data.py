from pydantic import (
    AnyUrl,
    root_validator,
    validator,
)
import re
from typing import (
    List,
    Union,
)

from .base_model import BaseModel


class BootfileData(BaseModel):
    """
    Contains information on a bootfile (such as grub) as well as which
    PXE client architecture it applies to. For more information on PXE
    client architectures, see https://tools.ietf.org/html/rfc4578#section-2.1
    """
    client_name: str
    client_arch: Union[int, str] = None
    dhcp_macs: List[str] = None
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

    @validator('dhcp_macs', each_item=True)
    def ensure_each_mac_is_valid_and_uses_colon_hexadecimal_notation(cls, value):
        valid_pattern = r'^[0-9a-f]{2}(:[0-9a-f]{2}){2}(:([0-9a-f]{2}|\*)){3}$'
        if re.match(valid_pattern, value) is None:
            raise ValueError(f'{value} does not use a valid colon-hex '
                             'mac address notation')
        return value

    @root_validator
    def ensure_client_arch_xor_dhcp_mac_is_defined(cls, values):
        if values.get('client_arch') is None and \
           values.get('dhcp_macs') is None:
            raise ValueError('Either client_arch or dhcp_mac must be defined')

        return values
