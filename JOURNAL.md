# 2020-12-12T17:30:00+0800

This new structure which removes the unnecessary abstraction provided by
Aircraft is much cleaner and easier to work with. I also no longer have to
spend any more time thinking about DSLs. I just work with what pyinfra provides,
freeing me for the more important stuff.

I've deleted the old structure via commit 5d024eb


# 2020-12-19T08:00:00+0800

Prototype 1 was abstracting away too much of pyinfra and was becoming
unweildy. For this next prototype, let's aim to re-use as much of pyinfra's
structure, vocabulary, and tooling as possible while allowing for parameterized
re-usable deploys.

Let's see how this one goes.


# 2020-12-15T06:06:00+0800

The `blueprints/` directory really holds a bunch of pyinfra packaged deploys that
do their own thing. So why are their models separated into a totally different
directory (`models/`)? These need to be merged. The end result might be a
manifest file that contains multiple blueprints and could look something
like this (subject to change):

```yaml
kind:        deployment
api_version: v1beta1
name:        Mandanov

inventory:
  hosts:
  - name:        compute-1:
    ip_address:  192.168.100.21/24

  - name:        compute-2
    ip_address:  192.168.100.22/24

  groups:
  - name:         group-1
    ssh_user:     secrets/ssh_user
    ssh_password: secrets/ssh_password
    gateway:      192.168.100.1
    nameservers:
    - 1.1.1.1
    - 8.8.8.8
    - 8.8.4.4
    members:
    - compute-1
    - compute-2

blueprints:
-  kind:        hypervisor.kvm
   api_version: v1beta1
   data:
     # This will contain a declaration of the hypervisor hosts
     # and which of the hosts (VMs) declared in the above inventory
     # belong where. This is going to be an odd blueprint because
     # whereas all other blueprints will use the above inventory
     # to determine which servers to configure, this one will have
     # it's own inventory and will use the above inventory to
     # determine where to create them. I wonder if that's a sign
     # of scope screep.
     ...

- kind:        cicd.gitlab
  api_version: v1
  data:
     # This will contain a declaration of which groups are servers
     # and which ones are runners. It will also contain all other
     # data needed by the blueprint to install gitlab
    ...

- kind:        lma.prometheus
  api_version: v1beta1
  data:
    # This will contain a declaration of which servers will host
    # prometheus plus all other data needed to intall prome.
    ...
```



# 2020-11-30T09:50:00+0800

The StringOrLocator class could potentially support an RFC-1808-compliant
URL but that can be saved for a later time since we also have to consider
the ability to cache retreived values at runtime so as not to slow down
the parsing process too much. This is considerable work in itself but is
not necessary for the MVP.


# 2020-11-28T15:50:00+0800

Commit 77fb2e7 illustrates how secrets management could be implemented.
Yeah, the secrets management thing which I claimed to be of top priority
4 days ago but promptly ignored until now. I've decided to skip sops and
go with [privy](https://pypi.org/project/privy/) instead since the latter
is just another Python library while the former is a separate binary.

Having said that, the door on sops isn't entirely closed just yet. Because
it implements so much more than privy, it's still a viable option. However,
it makes sense to experiment with privy too for the sake of thorougness.


# 2020-11-28T12:05:00+0800

With the previous idea implemented, the next thing to do is to change
aircraft.deployment.inventory.py to iterate through the YAML files in
a DEPLOYSPEC dir in lexicographic order and then run pyinfra against
each.

A separate but related feature would be the option to provide aircraft
with an inventory file in the DEPLOYSPEC. In that case, aircraft should
process that file directly.

---

Keep this thought in mind: with your previous Ansible-based projects,
you had the option to define hooks that do preparatory work on local
dev environments (See relaxdiego/cicd for example). While you had to
create bash hackery to make that work, this could be a built in feature
of aircraft.


# 2020-11-26T20:05:00+0800

I'm starting to think that `operations.yml` is redundant. For example,
if a user creates an inventory of kind `hypvervisor.kv` with api version
`v1beta1`, then we shoul be able to infer the operations necessary to
fulfill the user's requirement.


# 2020-11-26T08:18:00+0800

I've spent way too much time on this but I think these example schemas
are good enough for v1beta1:

KVM host inventory:

```yaml
kind: inventory.hypervisor.kvm
api_version: v1beta1
spec:
  hosts:
  - name: kvm-1
    data:
      ip_address: 192.168.100.11/24
      guests:
      - name: config
      - name: infra-1
      - name: infra-2
      - name: infra-3
  - name: kvm-2
    data:
      ip_address: 192.168.100.12/24
      guests:
      - name: node-1
      - name: node-2

  groups:
  - name: all
    data:
      interface: eno1

  - name: hypervisors
    data:
      gateway: 192.168.100.1
      nameservers:
      - 1.1.1.1
      - 8.8.8.8
      - 8.8.4.4
    members:
    - kvm-1
    - kvm-2
```

Operations

```yaml
kind: operations
api_version: v1beta1
spec:
  operations:
  - blueprints:
    - machine.kvm.install_packages
    - machine.kvm.configure_bridged_network
    - machine.kvm.create_guests
    targets:
    - hypervisors
```


# 2020-11-25T15:25:00+0800

Would be good to have `aircraft exec DEPLOYSPEC`


# 2020-11-24T21:11:00+0800

Something to think about now is how to separate the operations for the
hypervisors vs the operations for the VM hosts. Would it make sense to
create a new construct named `stage`? As in:

```yaml
stages:
- name: stage-1
  operations:
  - blueprints:
    - machine.kvm.install_packages
    - ...
    targets:
    - hypervisors
  - blueprints:
    - ...
    targets:
    - ...

- name: stage-2
  operations:
  - blueprints:
    - service.maas.install_packages
    - ...
    targets:
    - infra-nodes
```

The question now is whether the inventory will fail because it defines
hosts that are not yet reachable (e.g. infra-nodes). There is also the
concern of making the `operations.yml` file too complex.

Maybe we're better off just separating infra node configuration into its
own deployment spec instead.


# 2020-11-24T13:47:00+0800

Would be good to have `aircraft lint DEPLOYSPEC`


# 2020-11-24T10:36:00+0800

The highest priority right now for this prototyping stage is to figure
out the best way to implement secrets management. Being able to use
gpg-based encryption with the password shared off-band similar to what I
described [in this video](https://youtu.be/PweKPLDweO4) is important.


# 2020-11-23T22:46:00+0800

Fixes the problem I described earlier where values that are set lower in
the precedence hierarchy are unset higher up by a level that doesn't have
the same field set.


# 2020-11-23T18:43:00+0800

Shift implementation to using Pyinfra's built-in support for dynamic
inventories data generation inside `inventory.py`. This saves a lot of
coding for sure.

FIXME: If the `all` group defines a field such as `interface` and the
       `kvm` group does not, we end up setting the `interface` value to
       `None` since that's the default value in the group if it's not
       defined. There needs to be a way to account for this and ensure
       that a value is not accidentally undefined.


# 2020-11-23T16:30:00+0800

I've implemented some form of dynamic inventory generation but I'm unsure
if this is the right way to go about it. Perhaps this is too low level and
it may be better to stick to [the method](https://docs.pyinfra.com/en/1.x/examples/dynamic_inventories_data.html)
described by the Pyinfra documentation. That may be doable and more manageable.
We don't expect to have arbitrary set of groups for this project anyway
since the manifest directory is intended to be very specific to putting up
a MAAS cluster and not some arbitrary cluster running arbitrary services.


# 2020-11-23T12:11:00+0800

I've shifted from Fire to [Click](https://click.palletsprojects.com/en/7.x/documentation/)
instead since the former has a richer set of features while Fire is still
in very early stages.


# 2020-11-23T09:52:00+0800

Consider using [Fire](https://google.github.io/python-fire/) for implementing
the CLI tool.


# 2020-11-22T18:15:00+0800

We've implemented the model hierarchy for the inventory YAML file as
spec'd earlier. Up next is to properly implement the CLI launch subcommand.


# 2020-11-22T14:32:00+0800

Let's mock up the CLI interface for launching a deployment as follows:

```
aircraft launch examples/ha-kvm
```

We should also eventually support a `deployment.yml` file which describes
the blueprints to be used for the deployment. The contents of the file
could be as follows (subject to change):

```
meta:
  title: Deployment of HA MAAS on KVM VMs
spec:
- type: machine.kvm
- type: service.maas
  options:
    group: maas-hosts
```


# 2020-11-22T10:55:00+0800

Move the project from terminus to aircraft since I'm not using this
project for anything apart from experimental work on an FSM-based config
management library which is not going anywhere fast enough.

Continuing on my thoughts from yesterday, I would like to ultimately reach
a point where I can define my data in a single yaml file and reference secrets
from a separate, encrypted yaml file. For example, the data could be in
a `main.yml` file with the following contents (schema bound to change):

```
hosts:
  kvm-1:
    data:
      key1: val1
      key2: secret:some.key.in.secrets.yml
  kvm-2:
    data:
      key1: val1
      key2: secret:some.key.in.secrets.yml
  maas-1:
    data:
      key1: val1
      key2: val2
groups:
  kvm:
    data:
      key1: val1
      key2: val2
    hosts:
    - kvm-1
    - kvm-2
  maas:
    data:
      key1: val1
      key2: val2
    hosts:
    - maas-1
```

And a `secrets.yml` would contain `some.key.in.secrets.yml` which can
be auto-decrypted during runtime. We can use [sops](https://github.com/mozilla/sops/)
for this since it already provides many of the requirements that we need.
Furthermore, sops is able to encrypt just the values in a yaml file
rather than the entire file itself. This is handy for code reviews where
the reviewer can easily see which keys in the YAML file has changed.
[Read more about this workflow](https://poweruser.blog/how-to-encrypt-secrets-in-config-files-1dbb794f7352).


# 2020-11-21T19:50:00+0800

I've implemented the notes that I wrote down in my previous entry. This
new set up does offer better flexibility. I would like to get to a point
where I only have to declare group data and host data in a single file
but that can be the next step.

There's the tricky bit where pyinfra (or Jinja2?) does not fail when a
reference host data or fact is not present. We need to ensure that it
fails loudly if the data is not defined otherwise we may end up with
templates that are mis-rendered.


# 2020-11-21T17:30:00+0800

Running the following allows us to print host facts and data. Make sure
to run the following against sha `501458b`.
 
```
pyinfra sample-data/main.py blueprints/10-machines/kvm/main.py
```

It looks like pyinfra doesn't support supplying arbitrary data files via
the CLI so we cannot define group vars outside of the deploy tree. It
might be better to use packaged deploys instead. The initial plan is:

1) Convert the `blueprints/` subdir into a tree of
   [packaged deploys](https://docs.pyinfra.com/en/1.x/api/deploys.html).
   They can all be installed using a common `setup.py` in the root dir.
   Also have requirements-dev.txt (or whichever appropriate file) install
   them as editable modules.

2) Get rid of the `sample-data/` subdir as its name and purpose will be
   obsolete after this change.

3) Create `sample-deploys/` which will then contain an example deploy
   layout. Use the example from [pyinfra-etcd](https://github.com/Fizzadar/pyinfra-etcd/tree/develop/example)
   as reference.


