from typing import (
    List,
    Optional,
)

from .base_model import BaseModel
from .dhcp_data import DhcpData
from .dns_data import DnsData
from .tftp_data import TftpData


class DnsmasqData(BaseModel):
    """
    Contains information on which interfaces dnsmasq should listen to for client
    requests. Note that all fields are optional. If the interfaces field is not
    assigned, then it will be assumed that dnsmasq should listen on all interfaces.
    Likewise if dhcp is not assigned, then it is assumed that dnsmasq should not
    serve DHCP requests.
    """
    interfaces: List[str] = []
    dhcp: Optional[DhcpData]
    dns: Optional[DnsData]
    tftp: Optional[TftpData]
