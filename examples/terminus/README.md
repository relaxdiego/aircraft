Given
-----

* Ubiquiti EdgeOS remote as the temporary DHCP server for an L2 network that
  has a route to the Internet with SSH key auth enabled

* Synology DSM OS remote as the PXE server with the following services enabled:
  * SSH (key auth enabled)
  * An empty shared directory which will contain the boot files
  * SFTP enabled
  * TFTP enabled with the shared dir as its root
  * Web Console installed
  * A port based virtual host in the Web console with the shared dir
    as its root, and PHP enabled

NOTE: As much as I wanted to automate all that Synology requirement, there's
      not much documentation on DMS's API to go around. Perhaps in another example
      where I use a Raspberry Pi as both the DHCP and PXE server, we can get
      that working.


Network Layout
--------------

The network layout is illustrated in "Layer 1" of [this diagram](https://docs.google.com/drawings/d/1IYXyQ_sG0gMksttrtztyzmbRIbm7ZwDBmN6bXXkeS-Y/edit)
but the Synology NAS (192.168.86.43, 192.168.100.3) is not shown.


How to Run
----------

Provided you've followed the Developer's Guide in the top-lovel README and
the network layout is the same as in the diagram above, then you should be
able to run:

```
pyinfra examples/terminus/inventories/pxe.py examples/terminus/enable_pxe.py
```

Then PXE boot your two machines. Once done, then you're ready to install
MAAS on them. Before you do that, make sure to disable the PXE setup we
created above:

```
pyinfra examples/terminus/inventories/pxe.py examples/terminus/disable_pxe.py
```
