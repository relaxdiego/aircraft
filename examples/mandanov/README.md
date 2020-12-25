Use this in a VMware or VirtualBox set up where the machines belong
to a private network that has DHCP turned off and NAT enabled.

1. Make sure the VMs are configured to use UEFI boot.

2. Match the private network's subnet and netmask with the `dhcp.subnet`
   value in `group_data/pxe_server.py`.

3. Match the NAT address with the `dhcp.router` value in the same file.

4. For the two PXE clients, match their MAC addresses with the addresses
   specified in `pxe.machines` in the same file.

5. And, of course, you have to set up an Ubuntu VM which will serve as
   the PXE server. Configure however you like as long as the IP matches
   what's in `inventories/pxe_server.py` and that passwordless sudo is
   enabled (Hint: `sudo sed -i -E 's/^(%sudo.*) ALL$/\1 NOPASSWD:ALL/g' /etc/sudoers`)
