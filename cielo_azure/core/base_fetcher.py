"""Base classes for Azure resource fetchers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

from pydantic import BaseModel

try:  # pragma: no cover
    from azure.core.credentials import TokenCredential as AzureTokenCredential
except Exception:  # pragma: no cover - fallback if azure packages missing
    from typing import Protocol

    class AzureTokenCredential(Protocol):
        def get_token(self, *scopes: str) -> str:
            ...

TokenCredential = AzureTokenCredential

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseFetcher(ABC, Generic[ModelT]):
    """Abstract base class for all resource fetchers."""

    def __init__(self, subscription_id: str, credential: TokenCredential) -> None:
        # SRP: this class only manages interaction with Azure clients
        self.subscription_id = subscription_id
        self.credential = credential

    @abstractmethod
    def list_resources(self, *args, **kwargs) -> List[ModelT]:
        """List resources from Azure."""

    # Additional methods can be defined for reuse by concrete fetchers
