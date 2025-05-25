"""Base classes for Azure resource fetchers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

from pydantic import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for static type checking
    from azure.core.credentials import TokenCredential
else:  # pragma: no cover - runtime fallback if azure packages missing
    try:
        from azure.core.credentials import TokenCredential
    except Exception:
        from typing import Protocol

        class TokenCredential(Protocol):
            def get_token(self, *scopes: str) -> str:
                ...

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
