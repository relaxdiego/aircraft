import os

import click

from aircraft import aircraft_dir


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    pass


@main.command()
@click.argument('manifest_dir',
                type=click.Path(file_okay=False,
                                dir_okay=True,
                                exists=True,
                                resolve_path=True,
                                readable=True))
def apply(manifest_dir):
    """
    Applies the configuration defined in MANIFEST_DIR against the hosts
    declared within said directory. MANIFEST_DIR may be a relative or
    absolute path.
    """
    os.environ['AIRCRAFT_MANIFEST_DIR'] = manifest_dir

    cmd = f"cd {aircraft_dir / 'deployment'} && " \
          f"pyinfra inventory.py operations.py"
    os.system(cmd)
