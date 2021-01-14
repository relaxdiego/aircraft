# All servers listed here must have key-based SSH aut and password-less
# sudo configured for pyinfra to function correctly.

dhcp_server = [
    # Any Ubuntu server. Could even be a Pi running Ubuntu
    '192.168.86.21'
]
pxe_server = [
    # Synology NAS
    '192.168.86.43'
]
