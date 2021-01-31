Given
-----

* An L2 network that DOES NOT have a DCHP server but DOES have a gateway
  allowing outgoing connections all the way to the Internet.

* An Ubuntu machine in the L2 network that provides key-based SSH auth
  and passwordless sudo. No other services are required.

* A machine that has UEFI-based PXE booting. It must have a PXE client architecture
  of EFI Bytcode (Type 7 as per https://tools.ietf.org/html/rfc4578#section-2.1)


Network Layout
--------------

The network layout is illustrated in [this diagram](https://docs.google.com/drawings/d/1Z63UjXmhbEzeS5o0nO69qRwhTEfhBDok3UZHLW-IXcs/edit).


How to Run
----------

Provided you've followed the Developer's Guide in the top-lovel README and
the network layout is the same as in the diagram above, then you should be
able to run:

```
pyinfra inventories/all.py enable_pxe.py
```

Then PXE boot your machine(s). After all machines have PXE booted, disable
the PXE server as follows:

```
pyinfra inventories/all.py disable_pxe.py
```
