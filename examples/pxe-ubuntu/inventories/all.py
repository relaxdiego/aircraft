# All servers listed here must have key-based SSH auth and password-less
# sudo configured for pyinfra to function correctly.

pxe_server = [
    # Any Ubuntu 18.04 or 20.04 server. Could even be a Pi running Ubuntu
    'aircraft-ubuntu-server'
]
