Given
-----

* An L2 network that DOESN'T have a DCHP server but DOES have a gateway
  allowing outgoing connections all the way to the Internet.

* An Ubuntu machine in the L2 network that provides key-based auth SSH
  and passwordless sudo. You may even use https://help.ubuntu.com/community/Installation/MinimalCD
  to set up this initial machine if you want to save bandwidth.


Network Layout
--------------

The network layout is illustrated in [this diagram](https://docs.google.com/drawings/d/1Z63UjXmhbEzeS5o0nO69qRwhTEfhBDok3UZHLW-IXcs/edit?usp=sharing).


How to Run
----------

Provided you've followed the Developer's Guide in the top-lovel README and
the network layout is the same as in the diagram above, then you should be
able to run:

```
pyinfra examples/yaml-group-data/inventories/all.py examples/yaml-group-data/enable_pxe.py
```

Then PXE boot your two machines. Once done, then you're ready to install
MAAS on them. Before you do that, make sure to disable the PXE setup we
created above:

```
pyinfra examples/yaml-group-data/inventories/all.py examples/yaml-group-data/disable_pxe.py
```
