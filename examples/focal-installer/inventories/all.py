# All servers listed here must have key-based SSH auth and password-less
# sudo configured for pyinfra to function correctly.

dhcp_server = [
    # Any Ubuntu server. Could even be a Pi running Ubuntu
    'aircraft-ubuntu-server'
]
pxe_server = [
    # This Synology NAS must already have a volume named 'volume4' and
    # contains the following paths:
    #
    #     * /volume4/pxe/http
    #     * /volume4/pxe/tftpboot
    #
    # The path /volume4/pxe must be shared as 'pxe' in Control Panel >
    # Shared Folder
    #
    # The TFTP server must already have pxe/tftpboot as its root dir
    #
    # Its Web Station (donwloadable from the Synology store) must have a
    # virtual host whose root is pxe/http and its port is whatever
    # the value of pxe_server_port in group_data/all.yml might be.
    #
    # The SFTP service must be enabled. It's under Control Panel > File
    # Services > FTP tab
    'aircraft-synology-nas'
]
