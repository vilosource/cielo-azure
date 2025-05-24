import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import unittest
from unittest import mock
from typer.testing import CliRunner

from cielo_azure.models.virtual_machine import VirtualMachineModel
from cielo_azure.fetchers.virtual_machine_fetcher import VirtualMachineFetcher
from cielo_azure.cli.main import app


class TestVirtualMachineFetcher(unittest.TestCase):
    def setUp(self) -> None:
        self.credential = mock.Mock()
        self.fetcher = VirtualMachineFetcher(subscription_id="sub", credential=self.credential)

    @mock.patch("cielo_azure.fetchers.virtual_machine_fetcher.ComputeManagementClient")
    def test_list_resources(self, client_cls: mock.Mock) -> None:
        client = client_cls.return_value
        vm = mock.Mock()
        vm.name = "vm1"
        vm.id = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm1"
        vm.location = "eastus"
        vm.hardware_profile.vm_size = "Standard_DS1_v2"
        vm.tags = {"env": "test"}
        client.virtual_machines.list_all.return_value = [vm]

        result = self.fetcher.list_resources()
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], VirtualMachineModel)
        self.assertEqual(result[0].name, "vm1")

    @mock.patch("cielo_azure.fetchers.virtual_machine_fetcher.ComputeManagementClient")
    def test_get(self, client_cls: mock.Mock) -> None:
        client = client_cls.return_value
        vm = mock.Mock()
        vm.name = "vm1"
        vm.id = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm1"
        vm.location = "eastus"
        vm.hardware_profile.vm_size = "Standard_DS1_v2"
        vm.tags = {"env": "test"}
        client.virtual_machines.get.return_value = vm

        result = self.fetcher.get(vm_name="vm1", resource_group="rg")
        self.assertEqual(result.name, "vm1")


class TestCLI(unittest.TestCase):
    @mock.patch("cielo_azure.cli.main.VirtualMachineFetcher")
    @mock.patch("cielo_azure.cli.main.resolve_provider")
    def test_list_vms_cli(self, resolve_provider: mock.Mock, fetcher_cls: mock.Mock) -> None:
        provider = resolve_provider.return_value
        provider.get.return_value = mock.Mock()
        fetcher = fetcher_cls.return_value
        fetcher.list_resources.return_value = [
            VirtualMachineModel(
                name="vm1",
                id="/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm1",
                location="eastus",
                vm_size="Standard_DS1_v2",
                resource_group="rg",
                tags=None,
            )
        ]
        runner = CliRunner()
        result = runner.invoke(app, ["list-vms", "sub"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("vm1", result.output)

    @mock.patch("cielo_azure.cli.main.VirtualMachineFetcher")
    @mock.patch("cielo_azure.cli.main.resolve_provider")
    def test_get_vms_cli(self, resolve_provider: mock.Mock, fetcher_cls: mock.Mock) -> None:
        provider = resolve_provider.return_value
        provider.get.return_value = mock.Mock()
        fetcher = fetcher_cls.return_value
        fetcher.get.return_value = VirtualMachineModel(
            name="vm1",
            id="/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm1",
            location="eastus",
            vm_size="Standard_DS1_v2",
            resource_group="rg",
            tags=None,
        )
        runner = CliRunner()
        result = runner.invoke(app, ["get-vm", "sub", "vm1", "rg"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("vm1", result.output)


if __name__ == "__main__":
    unittest.main()
