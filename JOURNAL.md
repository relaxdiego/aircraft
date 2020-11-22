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


