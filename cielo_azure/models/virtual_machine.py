from __future__ import annotations

from typing import Dict, Optional

from pydantic import BaseModel


class VirtualMachineModel(BaseModel):
    """Pydantic model representing an Azure Virtual Machine."""

    name: str
    id: str
    location: str
    vm_size: Optional[str]
    resource_group: str
    tags: Optional[Dict[str, str]] = None
