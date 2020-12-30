Given
-----

* An L2 network that DOESN'T have a DCHP server but DOES have a gateway
  allowing outgoing connections all the way to the Internet.

* An Ubuntu machine in the L2 network that provides key-based auth SSH
  and passwordless sudo.

* Synology DSM OS as the PXE server with the following services enabled:
  * SSH (key auth enabled)
  * An empty shared directory which will contain the boot files
  * SFTP enabled
  * TFTP enabled with the shared dir as its root
  * Web Console installed
  * A port based virtual host in the Web console with the shared dir
    as its root

NOTE: As much as I wanted to automate all that Synology requirement, there's
      not much documentation on DMS's API to go around. Perhaps in another example
      where I use a Raspberry Pi as both the DHCP and PXE server, we can get
      that working.


Network Layout
--------------

The network layout is illustrated in [this diagram](https://docs.google.com/drawings/d/1QUKOCMXUo2vTudtBiqDe79aknTaEWyukA7ucoZuZ5tk/edit).
Notice how the Synology NAS does not have to be located in the L2 Lab Net as
long as it is routable. If you have the L2 gateway's configuration properly
set up, then it should work as fine.


How to Run
----------

Provided you've followed the Developer's Guide in the top-lovel README and
the network layout is the same as in the diagram above, then you should be
able to run:

```
pyinfra examples/synology/inventories/all.py examples/synology/enable_pxe.py
```

Then PXE boot your two machines. Once done, then you're ready to install
MAAS on them. Before you do that, make sure to disable the PXE setup we
created above:

```
pyinfra examples/synology/inventories/all.py examples/synology/disable_pxe.py
```
