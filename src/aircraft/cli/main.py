import os

import click

from aircraft import aircraft_dir


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    pass


@main.command()
@click.argument('deploy_spec',
                type=click.Path(file_okay=False,
                                dir_okay=True,
                                exists=True,
                                resolve_path=True,
                                readable=True))
@click.option('-v', '--verbose', count=True,
              help="Print meta (-v), input (-vv) and output (-vvv)")
def apply(deploy_spec, verbose):
    """
    Applies DEPLOY_SPEC where DEPLOY_SPEC is a directory containing files
    that lists the host inventory, deployment-specific data, and the
    operations that must be executed against the deployment. DEPLOY_SPEC
    may either be a relative or absolute path.
    """
    os.environ['AIRCRAFT_DEPLOY_SPEC'] = deploy_spec

    verbosity = ''
    if verbose > 0:
        verbosity = f"-{'v' * verbose}"

    old_path = os.getcwd()
    os.chdir(aircraft_dir / 'deployment')
    os.system(f"pyinfra {verbosity} inventory.py operations.py")
    os.chdir(old_path)


@main.command()
@click.argument('deploy_spec',
                type=click.Path(file_okay=False,
                                dir_okay=True,
                                exists=True,
                                resolve_path=True,
                                readable=True))
def debug(deploy_spec):
    """
    Prints out inventory and oeration debug information for DEPLOY_SPEC
    and then exits. It will connect to the hosts to be able to generate
    the oeprations list but it will not execute any of them.
    """
    os.environ['AIRCRAFT_DEPLOY_SPEC'] = deploy_spec

    old_path = os.getcwd()
    os.chdir(aircraft_dir / 'deployment')
    os.system("pyinfra inventory.py debug-inventory")
    os.system("pyinfra --debug-operations inventory.py operations.py")
    os.chdir(old_path)
