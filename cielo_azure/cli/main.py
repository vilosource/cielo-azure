"""Typer CLI entry point for the cielo_azure package."""

from __future__ import annotations

from typing import Optional

import typer

from cielo_azure.core.auth import resolve_provider
from cielo_azure.fetchers.virtual_machine_fetcher import VirtualMachineFetcher

app = typer.Typer(name="cielo")


@app.command("list-vms")
def list_vms(subscription_id: str, resource_group: Optional[str] = None, auth_mode: str = "default") -> None:
    """List virtual machines."""

    credential = resolve_provider(auth_mode).get()
    fetcher = VirtualMachineFetcher(subscription_id, credential)
    vms = fetcher.list_resources(resource_group)
    for vm in vms:
        typer.echo(vm.model_dump_json(indent=2))


@app.command("get-vm")
def get_vm(subscription_id: str, vm_name: str, resource_group: str, auth_mode: str = "default") -> None:
    """Get a single virtual machine."""

    credential = resolve_provider(auth_mode).get()
    fetcher = VirtualMachineFetcher(subscription_id, credential)
    vm = fetcher.get(vm_name, resource_group)
    typer.echo(vm.model_dump_json(indent=2))


if __name__ == "__main__":  # pragma: no cover - manual execution
    app()
