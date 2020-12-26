Use this in a VMware or VirtualBox set up where the machines belong
to a private network that has DHCP turned off and NAT enabled.

1. Make sure the VMs are configured to use UEFI boot.

2. Match the private network's subnet and netmask with the `dhcp.subnet`
   value in `group_data/pxe_server.py`.

3. Match the NAT address with the `dhcp.router` value in the same file.

4. And, of course, you have to manually set up an Ubuntu VM which will serve as
   the PXE server. Configure however you like as long its IP address is within the
   private network's subnet but outside the ranges in dhcp.ranges. Also make sure
   it allows for passwordless sudo.
   (Hint: `sudo sed -i -E 's/^(%sudo.*) ALL$/\1 NOPASSWD:ALL/g' /etc/sudoers`)


Troubleshooting
---------------

In the PXE server, monitor the DHCP transactions via:

```
sudo tcpdump port 67 or port 68 -e -n -vv -i <INTERFACE>
```

While in another window, monitor the TFTP transactions via:

```
sudo tcpdump port 69 -e -n -vv -i <INTERFACE>
```
