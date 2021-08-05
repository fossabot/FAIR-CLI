#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command Line Interface
======================

Main command line interface setup script for creation of commands used to
interact with the synchronisation tool.
"""

__date__ = "2021-06-24"

import click
import typing
import os
import sys

import fair.session as fdp_session
import fair.common as fdp_com
import fair.history as fdp_hist
import fair.configuration as fdp_conf
import fair.exceptions as fdp_exc
import fair.server as fdp_svr

__author__ = "Scottish COVID Response Consortium"
__credits__ = ["Nathan Cummings (UKAEA)", "Kristian Zarebski (UKAEA)"]
__license__ = "BSD-2-Clause"
__status__ = "Development"
__copyright__ = "Copyright 2021, FAIR Data Pipeline"


@click.group()
@click.version_option()
def cli():
    """Welcome to FAIR-CLI, the FAIR data pipeline command-line interface."""
    pass


@cli.command()
@click.option("--debug/--no-debug", help="Run in debug mode", default=False)
def status(debug) -> None:
    """Get the status of files under staging"""
    with fdp_session.FAIR(os.getcwd(), debug=debug) as fair_session:
        fair_session.status()


@cli.command()
@click.option("--debug/--no-debug", help="Run in debug mode", default=False)
def yaml(debug) -> None:
    """Generate a new FAIR repository user YAML config file"""
    click.echo(
        f"Generating new 'config.yaml' in '{fdp_com.find_fair_root(os.getcwd())}'"
    )
    with fdp_session.FAIR(os.getcwd(), debug=debug) as fair_session:
        fair_session.make_starter_config()


@cli.command()
@click.option(
    "--config",
    help="Specify alternate location for generated config.yaml",
    default=fdp_com.local_user_config(os.getcwd()),
)
@click.option("--debug/--no-debug", help="Run in debug mode", default=False)
def init(config: str, debug: bool) -> None:
    """Initialise repository in current location"""
    try:
        with fdp_session.FAIR(
            os.getcwd(), config, debug=debug
        ) as fair_session:
            fair_session.initialise()
    except fdp_exc.FAIRCLIException as e:
        e.err_print()
        if e.level.lower() == "error":
            sys.exit(e.exit_code)


@cli.command()
@click.option(
    "--glob/--loc",
    help="Delete global FAIR-CLI directories",
    default=False,
)
def purge(glob) -> None:
    """Resets the repository deleting all local caches"""
    _purge = click.prompt(
        "Are you sure you want to reset FAIR tracking, "
        "this is not reversible [Y/N]? ",
        type=click.BOOL,
    )
    if _purge:
        try:
            with fdp_session.FAIR(os.getcwd()) as fair_session:
                fair_session.purge(glob)
        except fdp_exc.FAIRCLIException as e:
            e.err_print()
            if e.level.lower() == "error":
                sys.exit(e.exit_code)


@cli.group()
def registry() -> None:
    """Commands relating to control of the local registry server"""
    pass


@registry.command()
def start() -> None:
    """Start the local registry server"""
    try:
        fdp_session.FAIR(os.getcwd(), mode=fdp_svr.SwitchMode.USER_START)
    except fdp_exc.FAIRCLIException as e:
        e.err_print()
        if e.level.lower() == "error":
            sys.exit(e.exit_code)


@registry.command()
@click.option("--force/--no-force", help="Force server stop", default=False)
def stop(force) -> None:
    """Stop the local registry server"""
    _mode = (
        fdp_svr.SwitchMode.FORCE_STOP
        if force
        else fdp_svr.SwitchMode.USER_STOP
    )
    try:
        fdp_session.FAIR(os.getcwd(), mode=_mode)
    except fdp_exc.FAIRCLIException as e:
        e.err_print()
        if e.level.lower() == "error":
            sys.exit(e.exit_code)


@cli.command()
def log() -> None:
    """Show a full run history"""
    fdp_hist.show_history(os.getcwd())


@cli.command()
@click.argument("run_id")
def view(run_id: str) -> None:
    """View log for a given run"""
    fdp_hist.show_run_log(os.getcwd(), run_id)


@cli.command()
@click.argument("file_paths", type=click.Path(exists=True), nargs=-1)
@click.option("--debug/--no-debug", help="Run in debug mode", default=False)
def reset(file_paths: typing.List[str], debug: bool) -> None:
    """Removes files/runs from staging"""
    try:
        with fdp_session.FAIR(os.getcwd(), debug=debug) as fair_session:
            for file_name in file_paths:
                fair_session.change_staging_state(file_name, False)
    except fdp_exc.FAIRCLIException as e:
        e.err_print()
        if e.level.lower() == "error":
            sys.exit(e.exit_code)


@cli.command()
@click.argument("file_paths", type=click.Path(exists=True), nargs=-1)
@click.option("--debug/--no-debug", help="Run in debug mode", default=False)
def add(file_paths: typing.List[str], debug: bool) -> None:
    """Add a file to staging"""
    try:
        with fdp_session.FAIR(os.getcwd(), debug=debug) as fair_session:
            for file_name in file_paths:
                fair_session.change_staging_state(file_name, True)
    except fdp_exc.FAIRCLIException as e:
        e.err_print()
        if e.level.lower() == "error":
            sys.exit(e.exit_code)


@cli.command()
@click.argument("file_paths", type=click.Path(exists=True), nargs=-1)
@click.option("--debug/--no-debug", help="Run in debug mode", default=False)
@click.option(
    "--cached/--not-cached",
    default=False,
    help="remove from tracking but do not delete from file system",
)
def rm(
    file_paths: typing.List[str], cached: bool = False, debug: bool = False
) -> None:
    """Removes files from system or just tracking"""
    try:
        with fdp_session.FAIR(os.getcwd(), debug=debug) as fair_session:
            for file_name in file_paths:
                fair_session.remove_file(file_name, cached)
    except fdp_exc.FAIRCLIException as e:
        e.err_print()
        if e.level.lower() == "error":
            sys.exit(e.exit_code)


@cli.group(invoke_without_command=True)
@click.pass_context
@click.option(
    "--config",
    help="Specify alternate location for generated config.yaml",
    default=fdp_com.local_user_config(os.getcwd()),
)
@click.option("--debug/--no-debug", help="Run in debug mode", default=False)
def run(ctx, config: str, debug: bool):
    """Initialises a run with the option to specify a bash command"""
    if not ctx.invoked_subcommand:
        try:
            with fdp_session.FAIR(
                os.getcwd(), config, debug=debug, mode=fdp_svr.SwitchMode.CLI
            ) as fair_session:
                fair_session.run()
        except fdp_exc.FAIRCLIException as e:
            e.err_print()
            if e.level.lower() == "error":
                sys.exit(e.exit_code)


@run.command()
@click.argument("bash_command")
@click.option(
    "--config",
    help="Specify alternate location for generated config.yaml",
    default=fdp_com.local_user_config(os.getcwd()),
)
@click.option("--debug/--no-debug", help="Run in debug mode", default=False)
def bash(bash_command: str, config: str, debug: bool):
    """Run a BASH command and set this to be the default run command"""
    try:
        with fdp_session.FAIR(
            os.getcwd(), config, debug=debug
        ) as fair_session:
            fair_session.run(bash_command)
    except fdp_exc.FAIRCLIException as e:
        e.err_print()
        if e.level.lower() == "error":
            sys.exit(e.exit_code)


@cli.group(invoke_without_command=True)
@click.option("--verbose/--no-verbose", "-v/")
@click.option("--debug/--no-debug", help="Run in debug mode", default=False)
@click.pass_context
def remote(ctx, verbose: bool = False, debug: bool = False):
    """List remotes if no additional command is provided"""
    if not ctx.invoked_subcommand:
        try:
            with fdp_session.FAIR(os.getcwd(), debug=debug) as fair_session:
                fair_session.list_remotes(verbose)
        except fdp_exc.FAIRCLIException as e:
            e.err_print()
            if e.level.lower() == "error":
                sys.exit(e.exit_code)


@remote.command()
@click.argument("options", nargs=-1)
@click.option("--debug/--no-debug", help="Run in debug mode", default=False)
def add(options: typing.List[str], debug: bool) -> None:
    """Add a remote registry URL with option to give it a label if multiple
    remotes may be used.

    Parameters
    ----------
    options : typing.List[str]
        size 1 or 2 list containing either:
            - label, url
            - url
    """
    _url = options[1] if len(options) > 1 else options[0]
    _label = options[0] if len(options) > 1 else "origin"

    try:
        with fdp_session.FAIR(os.getcwd(), debug=debug) as fair_session:
            fair_session.add_remote(_url, _label)
    except fdp_exc.FAIRCLIException as e:
        e.err_print()
        if e.level.lower() == "error":
            sys.exit(e.exit_code)


@remote.command()
@click.argument("label")
@click.option("--debug/--no-debug", help="Run in debug mode", default=False)
def remove(label: str, debug: bool) -> None:
    """Removes the specified remote from the remotes list

    Parameters
    ----------
    label : str
        label of remote to remove
    """
    try:
        with fdp_session.FAIR(os.getcwd(), debug=debug) as fair_session:
            fair_session.remove_remove(label)
    except fdp_exc.FAIRCLIException as e:
        e.err_print()
        if e.level.lower() == "error":
            sys.exit(e.exit_code)


@remote.command()
@click.argument("label")
@click.argument("url")
@click.pass_context
@click.option("--debug/--no-debug", help="Run in debug mode", default=False)
def modify(ctx, label: str, url: str, debug: bool) -> None:
    """Modify a remote address"""
    try:
        with fdp_session.FAIR(os.getcwd(), debug=debug) as fair_session:
            fair_session.modify_remote(label, url)
    except fdp_exc.FAIRCLIException as e:
        e.err_print()
        if e.level.lower() == "error":
            sys.exit(e.exit_code)


@cli.command()
@click.argument("api-token")
def push(api_token: str):
    """
    Push new files (generated from write: and register:) to the remote data store

    record metadata in the data registry (whilst editing relevant entries, e.g. storage_root)
    """
    click.echo(f"push command called")
    # headers = {
    #     'Authorization': 'token: api_token'
    # }
    #
    # data = {
    #
    # }
    #
    # requests.put('https://data.scrc.uk/api/object/', data, headers=headers)


@cli.group()
def config():
    """Configure user information"""
    pass


@config.command(name="user.name")
@click.argument("user_name")
def config_user(user_name: str) -> None:
    """
    TODO: should update a user file in .scrc containing user information
    (API token, associated namespace, local data
    store, login node, and so on).
    """
    fdp_conf.set_user(os.getcwd(), user_name)


@config.command(name="user.email")
@click.argument("user_email")
def config_email(user_email: str) -> None:
    fdp_conf.set_email(os.getcwd(), user_email)


if __name__ in "__main__":
    cli(ob={})