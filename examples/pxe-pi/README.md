Given
-----

* An L2 network that DOESN'T have a DCHP server but DOES have a gateway
  allowing outgoing connections all the way to the Internet.

* A Raspberry Pi running Ubuntu in the L2 network that provides key-based
  auth SSH and passwordless sudo. TIP: If you don't have a Pi handy, it
  can actually be any machine running Ubuntu.


Network Layout
--------------

The network layout is illustrated in [this diagram](https://docs.google.com/drawings/d/14duzINFaUkZgmGte8hM2fXJCiWsOp9cBMuUZ4SmNoKU/edit).


How to Run
----------

Provided you've followed the Developer's Guide in the top-lovel README and
the network layout is the same as in the diagram above, then you should be
able to run:

```
pyinfra examples/pxe-pi/inventories/all.py examples/pxe-pi/enable_pxe.py
```

Then PXE boot your two machines. Once done, then you're ready to install
MAAS on them. Before you do that, make sure to disable the PXE setup we
created above:

```
pyinfra examples/pxe-pi/inventories/all.py examples/pxe-pi/disable_pxe.py
```
