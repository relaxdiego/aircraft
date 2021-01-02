# All servers listed here must have key-based SSH aut and password-less
# sudo configured for pyinfra to function correctly.

dhcp_server = [
    # Any Ubiquiti router running Edge OS
    '192.168.86.250'
]
pxe_server = [
    # Synology NAS
    '192.168.86.43'
]
