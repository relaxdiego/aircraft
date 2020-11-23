import sys

import click

from aircraft.cli.launch_cmd import LaunchCmd


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
def launch(manifest_dir):
    """
    Launches a deployment based on a manifest directory refered to by
    MANIFEST_DIR which can either be a relative or absolute path.
    """
    try:
        LaunchCmd(manifest_dir=manifest_dir).run()
    except Exception as e:
        print(e)
        sys.exit(1)
