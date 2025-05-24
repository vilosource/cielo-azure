# Azure Resource Fetcher Library

## Overview
This project implements a modular, extensible Python library for fetching Azure resources.
The initial implementation focuses on Virtual Machines using the Azure SDK and is designed
for single-subscription support, with a clean architecture for multi-subscription support later.

The implementation must follow:
- **SOLID principles** (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion)
- **Design patterns** (Strategy, Registry, Dependency Injection, CLI Command pattern)

All fetchers must:
- Return validated **Pydantic v2 models**
- Include full type annotations
- Be fully tested with mocked Azure SDK responses
- Pass **mypy** static type checking
- Be exposed via a **Typer CLI** and **Poetry tool scripts**

---

## Project Structure

```
cielo_azure/
├── __init__.py
├── core/
│   ├── base_fetcher.py               # Abstract base for all fetchers
│   ├── auth.py                       # SOLID-compliant credential strategy + registry
│   ├── utils.py                      # (optional) Shared helpers
├── fetchers/
│   ├── virtual_machine_fetcher.py    # VM fetcher returning Pydantic models
├── models/
│   ├── virtual_machine.py            # Pydantic model for VM
├── cli/
│   └── main.py                       # Typer CLI with one command per fetcher
├── tests/
│   └── test_virtual_machine_fetcher.py  # Unit tests using unittest and mock
├── config.py                         # (optional)
├── constants.py                      # (optional)
```

---

## Authentication (core/auth.py)

Authentication must follow the **Strategy pattern** using a `CredentialProvider` interface.
Use a decorator to register new providers in a global registry, enabling **Open/Closed** compliance.

Supported modes:
- `default`: Uses `DefaultAzureCredential`
- `managed`: Uses `ManagedIdentityCredential`
- `cli`: Uses `AzureCliCredential`
- `service_principal`: Uses `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`

Use:
```python
from core.auth import resolve_provider
provider = resolve_provider("default")
credential = provider.get()
```

---

## Fetcher Requirements

**core/base_fetcher.py**:
- Abstract class `BaseFetcher`:
  - `__init__(self, subscription_id: str, credential: TokenCredential)`
  - `abstract list_resources(...) -> List[PydanticModel]`

**fetchers/virtual_machine_fetcher.py**:
- `VirtualMachineFetcher(BaseFetcher)`:
  - `list_resources(resource_group: Optional[str]) -> List[VirtualMachineModel]`
  - `get(vm_name: str, resource_group: str) -> VirtualMachineModel`

**models/virtual_machine.py**:
- Pydantic v2 model:
```python
class VirtualMachineModel(BaseModel):
    name: str
    id: str
    location: str
    vm_size: Optional[str]
    resource_group: str
    tags: Optional[Dict[str, str]] = None
```

---

## Typer CLI (cli/main.py)

- Use `typer.Typer(name="cielo")` to register commands.
- Each fetcher must expose CLI commands such as:
  - `cielo list-vms`
  - `cielo get-vm`
- Print output using `.model_dump_json(indent=2)`
- If no parameters are provided, the CLI should automatically display help.

Example:
```python
@app.command("list-vms")
def list_vms(subscription_id: str, resource_group: Optional[str] = None):
    ...
```

### Poetry CLI Tool Integration
Define commands in `pyproject.toml`:
```toml
[tool.poetry.scripts]
cielo = "cielo_azure.cli.main:app"
```

This exposes a unified `cielo` CLI entry point with subcommands like:
```bash
poetry run cielo list-vms
poetry run cielo get-vm
```

---

## Testing
- Use `unittest` and `unittest.mock`
- Cover all fetchers and CLI commands
- Validate that providers and CLI function without Azure calls
- Use `typer.testing.CliRunner` for CLI tests

---

## Static Typing
- All public methods must have type annotations
- No use of `Any`
- Must pass:
```bash
poetry run mypy cielo_azure
```

---

## Dependencies (pyproject.toml)
```toml
[tool.poetry.dependencies]
python = "^3.10"
azure-identity = "^1.15.0"
azure-mgmt-compute = "^30.1.0"
pydantic = "^2.7"
typer = {extras = ["all"], version = "^0.12.0"}

[tool.poetry.group.dev.dependencies]
pytest = "^8.1"
mypy = "^1.10"
```

---

## Future Enhancements
- Add `MultiSubscriptionVMFetcher`
- Add fetchers: NICs, IPs, Disks, Storage, KeyVaults, etc.
- Add `EnrichedVMFetcher` to compose related resources
- Add config file (.toml or .env)
- Output options: JSON, YAML, pandas DataFrame

