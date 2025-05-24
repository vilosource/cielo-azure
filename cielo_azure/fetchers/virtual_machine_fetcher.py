"""Fetcher implementation for Azure Virtual Machines."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

from cielo_azure.core.base_fetcher import BaseFetcher
from cielo_azure.models.virtual_machine import VirtualMachineModel

try:  # pragma: no cover
    from azure.mgmt.compute import ComputeManagementClient
except Exception:  # pragma: no cover - provide stub when azure packages missing
    ComputeManagementClient = None  # type: ignore


class VirtualMachineFetcher(BaseFetcher[VirtualMachineModel]):
    """Fetches Virtual Machines using the Azure SDK."""

    def _client(self) -> "ComputeManagementClient":
        if ComputeManagementClient is None:  # pragma: no cover - azure libs not installed
            raise RuntimeError("Azure SDK is required for this operation")
        return ComputeManagementClient(credential=self.credential, subscription_id=self.subscription_id)

    # OCP: additional methods can be added without modifying BaseFetcher
    def list_resources(self, resource_group: Optional[str] = None) -> List[VirtualMachineModel]:
        client = self._client()
        if resource_group:
            vms = client.virtual_machines.list(resource_group)
        else:
            vms = client.virtual_machines.list_all()
        return [self._to_model(vm) for vm in vms]

    def get(self, vm_name: str, resource_group: str) -> VirtualMachineModel:
        client = self._client()
        vm = client.virtual_machines.get(resource_group, vm_name)
        return self._to_model(vm)

    def _to_model(self, azure_vm: BaseModel) -> VirtualMachineModel:
        # LSP: subclass maintains behavior of returning VirtualMachineModel
        return VirtualMachineModel(
            name=azure_vm.name,
            id=azure_vm.id,
            location=azure_vm.location,
            vm_size=getattr(getattr(azure_vm, "hardware_profile", None), "vm_size", None),
            resource_group=azure_vm.id.split("/")[4],
            tags=azure_vm.tags,
        )
