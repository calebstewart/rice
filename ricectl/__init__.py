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

import typer
from git.remote import FetchInfo
from git.repo import Repo
from rich.console import Console
from rich.table import Table, box, Column
from rich.prompt import Prompt, Confirm

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

    try:
        # Ensure the remote is up-to-date
        subprocess.run(
            ["git", "remote", "update", "origin"], cwd=config.repo, check=True
        )
    except subprocess.CalledProcessError:
        console.log("[red]error[/red]: failed to fetch remote changes")

    try:
        # Find the tip of the current branch
        proc = subprocess.run(
            ["git", "rev-parse", "@"],
            cwd=config.repo,
            stdout=subprocess.PIPE,
            check=True,
        )
        local_tip = proc.stdout.strip()
    except subprocess.CalledProcessError:
        console.log(f"[red]error[/red]: failed to get local head")
        return

    try:
        # Find the tip of the upstream branch
        proc = subprocess.run(
            ["git", "rev-parse", "@{u}"],
            cwd=config.repo,
            stdout=subprocess.PIPE,
            check=True,
        )
        remote_tip = proc.stdout.strip()
    except subprocess.CalledProcessError:
        console.log(f"[red]error[/red]: failed to get remote head")
        return

    try:
        # Find the base between the current and upstream branches
        proc = subprocess.run(
            ["git", "merge-base", "@", "@{u}"],
            cwd=config.repo,
            stdout=subprocess.PIPE,
            check=True,
        )
        base = proc.stdout.strip()
    except subprocess.CalledProcessError:
        console.log(f"[red]error[/red]: failed to get base commit")
        return

    # yay, no changes!
    if local_tip == remote_tip:
        console.log(f"Repository up to date.")
        return

    # We've either diverged in two directions or just have pending remote updates.
    if local_tip == base or remote_tip != base:
        console.log("Pulling new remote commits...")
        try:
            subprocess.run(["git", "pull"], cwd=config.repo, check=True)
            # Set the pending flag for the new changes
            config.pending = True
        except subprocess.CalledProcessError:
            console.log(f"[red]error[/red]: 'git pull' failed")
            return

    # Either diverged in two directions or have local changes to push...
    if remote_tip == base or local_tip != base:
        console.log("Found pending local commits:")
        try:
            proc = subprocess.run(
                ["git", "log", "origin/main..HEAD", f"--pretty=tformat:%H\t%s"],
                cwd=config.repo,
                check=True,
                stdout=subprocess.PIPE,
            )
            pending_commits = [
                line.decode("utf-8").split("\t", maxsplit=1)
                for line in proc.stdout.splitlines()
                if line
            ]

            table = Table(
                "indent",
                Column("hash", style="cyan"),
                Column("summary", style="italic dim"),
                box=None,
                pad_edge=False,
                show_header=False,
                show_footer=False,
                highlight=True,
            )
            for hash, message in pending_commits:
                table.add_row("  ", hash[:7], message)
            console.print(table)

            if pending_commits and Confirm.ask(
                "Push pending commits?", console=console
            ):
                try:
                    subprocess.run(["git", "push"], cwd=config.repo, check=True)
                    console.log("pending commits published to repository")
                except subprocess.CalledProcessError:
                    console.log(f"[red]error[/red]: failed to push pending commits")
        except subprocess.CalledProcessError:
            console.log(f"[red]error[/red]: failed to enumerate pending commits")

    console.log("rice update successful")
    config.save()


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
        "--tags",
        ",".join([str(x) for x in config.tags]),
        "site.yml",
    ]

    try:
        subprocess.run(arguments, cwd=config.repo / "ansible", check=True)
        config.pending = False
        config.save()
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

    if Tag.CORE in tags:
        console.log("[yellow]warning[/yellow]: cannot remove 'core' tag")

    config.tags -= set([t for t in tags if t != Tag.CORE])
    config.pending = True
    config.save()


if __name__ == "__main__":
    root()
