import sys

import click

from aircraft.cli.apply_cmd import ApplyCmd


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
    try:
        ApplyCmd(manifest_dir=manifest_dir).run()
    except Exception as e:
        print(e)
        sys.exit(1)
