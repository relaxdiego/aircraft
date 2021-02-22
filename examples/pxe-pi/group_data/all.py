from pathlib import Path
import yaml

from aircraft.deploys.ubuntu.models.v1beta3 import (
    DnsmasqData,
    HttpData,
    PxeData,
)

with open(Path(__file__).parent / 'all.yml') as fh:
    group_data = yaml.safe_load(fh)

dnsmasq = DnsmasqData(**group_data['dnsmasq'])
http = HttpData(**group_data['http'])
pxe = PxeData(**group_data['pxe'])
