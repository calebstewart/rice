#!/opt/rice/env/bin/python3
# Name: ricectl.py
# Description: Control rice setup, installation, and upgrading
# Usage: ricectl.py command [options...]
# Author: Caleb Stewart <caleb.stewart94@gmail.com>
import functools
import subprocess
import sys
from pathlib import Path
from typing import List
import tempfile

import typer
from git.remote import FetchInfo
from git.repo import Repo
from rich.console import Console
from rich.table import Table
import ansible_runner

from ricectl.config import Config, Tag

# Root typer application
root = typer.Typer(help="Manage RICE installation, update and synchronization")
config_app = typer.Typer(help="Manage configuration")
root.add_typer(config_app)

# Load configuration
config = Config()

# Create a global console instance
console = Console(log_path=False)


def update_progress(status, prefix, op_code, cur_count, max_count=None, message=""):
    if message != "":
        status.update(f"{prefix}: {message}")


@root.command("sync")
def rice_sync():
    """Synchronize the RICE repository with remote"""

    # Load the repository
    repo = Repo(config.repo)

    infos = repo.remotes.origin.fetch()
    for info in infos:
        if (info.flags & FetchInfo.HEAD_UPTODATE) != 0:
            break
    else:
        console.log(
            f"Already up-to-date on {repo.active_branch.name}@{repo.active_branch.commit.hexsha[:7]} ({repo.active_branch.commit.summary})"
        )
        return

    with console.status("Merging remote") as status:
        repo.remotes.origin.pull(
            progress=functools.partial(update_progress, status, "Merging remote")
        )

    with console.status("Pushing changes") as status:
        repo.remotes.origin.push(
            progress=functools.partial(update_progress, status, "Pushing changes")
        )


@root.command("apply")
def rice_apply():
    """Apply the current state of the RICE using Ansible"""

    venv_bin = Path(sys.executable).parent
    if not (venv_bin / "ansible-playbook").is_file():
        console.log(
            f"[red]error[/red]: unable to find [cyan]ansible-playbook[/cyan] in [blue]{venv_bin}[/blue]"
        )
        return

    console.log(
        f"Executing [cyan]ansible-playbook[/cyan] with tags {list(config.tags)}"
    )

    arguments = [
        venv_bin / "ansible-playbook",
        "--ask-become-pass",
        "site.yml",
    ]

    if config.tags:
        arguments.extend(
            [
                "--tags",
                ",".join([str(x) for x in config.tags]),
            ]
        )

    try:
        subprocess.run(arguments, cwd=config.repo / "ansible", check=True)
    except subprocess.CalledProcessError as exc:
        console.log("[red]error[/red]: [cyan]ansible-playbook[/cyan] failed")


@root.command("update")
def rice_update():
    """Synchronize the RICE repository and then apply the updated state with Ansible if there were changes."""

    # Sync the repository
    rice_sync()

    # Apply any changes
    rice_apply()


@root.command("status")
def rice_status():
    """Retrieve the current state of the RICE repository"""

    repo = Repo(config.repo)

    table = Table(
        "icon",
        "comment",
        box=None,
        pad_edge=False,
        show_header=False,
        show_footer=False,
        highlight=True,
    )

    repo_path = config.repo.absolute()
    if repo_path.is_relative_to(Path.home()):
        repo_path = "$HOME/" + str(repo_path.relative_to(Path.home()))

    table.add_row(
        ":rice:",
        f"respository at [cyan]{repo_path}[/cyan] on [blue]{repo.active_branch.name}[/blue]@[green]{repo.active_branch.commit.hexsha[:7]}[/green] ([dim]{repo.active_branch.commit.summary}[/dim])",
    )

    if config.tags:
        table.add_row(":label:", f"using tags {list(config.tags)}")

    if config.pending:
        table.add_row(
            ":warning:",
            "pending changes waiting for application (use [dim]`ricectl apply`[/dim])",
        )
    if repo.is_dirty():
        table.add_row(
            ":warning:",
            "repository has local changes or commits (use [dim]`ricectl sync`[/dim])",
        )

    console.print(table)


@root.command("add-tag")
def rice_add_tag(tags: List[Tag]):
    """Add a new tag for this host. These tags are passed to Ansible on the
    next call to apply, and may modify your configuration."""

    config.tags |= set(tags)
    config.pending = True
    config.save()


@root.command("remove-tag")
def rice_remove_tag(tags: List[Tag]):
    """Remove a tag from this host. Removing tags does not necessarily make
    any new changes to your system or remove the changes added by the tag,
    but does stop those changes from being made during apply operations."""

    config.tags -= set(tags)
    config.pending = True
    config.save()


if __name__ == "__main__":
    root()
