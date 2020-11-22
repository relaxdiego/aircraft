This is a sample deploy for HA MAAS (3 instances) deployed on KVM VMs directly
connected to the underlying network as per [this diagram](https://docs.google.com/drawings/d/1IYXyQ_sG0gMksttrtztyzmbRIbm7ZwDBmN6bXXkeS-Y/edit?usp=sharing)

To deploy, modify `inventory.py` and `group_vars/all.py` then run the following
from within this directory:

```
pyinfra inventory.py deploy.py
```
