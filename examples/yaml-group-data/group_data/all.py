from pathlib import Path
import yaml

from aircraft.deploys.synology.models.v1beta2 import (
    PxeData,
)
from aircraft.deploys.ubuntu.models.v1beta2 import (
    DhcpData,
    DnsmasqData,
    HttpData,
    TftpData,
)

with open(Path(__file__).parent / 'all.yml') as fh:
    group_data = yaml.safe_load(fh)

tftp = TftpData(**group_data['tftp'])
http = HttpData(**group_data['http'])
dhcp = DhcpData(**group_data['dhcp'])
dnsmasq = DnsmasqData(**group_data['dnsmasq'])
pxe = PxeData(**group_data['pxe'])
