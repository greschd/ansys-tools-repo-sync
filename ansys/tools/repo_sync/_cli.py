"""Tool to copy the content of one repo toward an other.
Run with:

repo-sync -o Organization -r repository -p path_to_protos_directory

"""

import click

from .repo_sync import synchronize as _synchronize


@click.command(short_help="Copy the content of a repository into an other repository.")
@click.option("--organization", "-o", type=str, help="Name of the organization.", default="pyansys")
@click.option("--repository", "-r", type=str, help="Name of the repository.", required=True)
@click.option("--token", "-t", type=str, help="Personal access token.")
@click.option(
    "--protos",
    "-p",
    type=click.Path(file_okay=False, exists=True),
    help="Path to the folder containing the *.protos file to copy.",
    required=True,
)
@click.option(
    "--manifest",
    "-m",
    type=click.Path(dir_okay=False, exists=True),
    help="Manifest to mention prohibited extension files.",
)
@click.option(
    "--dry-run",
    "-d",
    is_flag=True,
    default=False,
    help="Simulate the behavior of the synchronization without performing it.",
)
def synchronize(manifest, repository, token, organization, protos, dry_run):
    _synchronize(
        manifest=manifest,
        repository=repository,
        token=token,
        organization=organization,
        protos_path=protos,
        dry_run=dry_run,
    )