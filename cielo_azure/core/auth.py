"""Authentication utilities following the Strategy pattern."""

from __future__ import annotations

import os
from typing import Callable, Dict, Protocol, Type

try:  # pragma: no cover - imported for type checking
    from azure.core.credentials import TokenCredential
    from azure.identity import (
        AzureCliCredential,
        DefaultAzureCredential,
        ManagedIdentityCredential,
        ClientSecretCredential,
    )
except Exception:  # pragma: no cover - fallback types for environments without azure packages
    class TokenCredential(Protocol):
        """Minimal TokenCredential protocol used for type hints."""

        def get_token(self, *scopes: str) -> str:
            ...

    class DefaultAzureCredential:  # type: ignore[empty-body]
        pass

    class ManagedIdentityCredential:  # type: ignore[empty-body]
        pass

    class AzureCliCredential:  # type: ignore[empty-body]
        pass

    class ClientSecretCredential:  # type: ignore[empty-body]
        def __init__(self, tenant_id: str, client_id: str, client_secret: str) -> None:  # noqa: D401 E501
            pass


class CredentialProvider(Protocol):
    """Strategy interface for providing Azure credentials."""

    def get(self) -> TokenCredential:  # pragma: no cover - simple getter
        ...


_REGISTRY: Dict[str, Type[CredentialProvider]] = {}


def register_provider(name: str) -> Callable[[Type[CredentialProvider]], Type[CredentialProvider]]:
    """Decorator to register credential providers."""

    def decorator(cls: Type[CredentialProvider]) -> Type[CredentialProvider]:
        _REGISTRY[name] = cls
        return cls

    return decorator


def resolve_provider(name: str) -> CredentialProvider:
    """Resolve a credential provider by name, enforcing the Open/Closed principle."""

    provider_cls = _REGISTRY.get(name)
    if not provider_cls:
        raise ValueError(f"Unknown credential provider: {name}")
    return provider_cls()


@register_provider("default")
class DefaultCredentialProvider:
    """Provides DefaultAzureCredential."""

    def get(self) -> TokenCredential:
        return DefaultAzureCredential()


@register_provider("managed")
class ManagedIdentityCredentialProvider:
    """Provides ManagedIdentityCredential."""

    def get(self) -> TokenCredential:
        return ManagedIdentityCredential()


@register_provider("cli")
class AzureCliCredentialProvider:
    """Provides AzureCliCredential."""

    def get(self) -> TokenCredential:
        return AzureCliCredential()


@register_provider("service_principal")
class ServicePrincipalCredentialProvider:
    """Provides ClientSecretCredential using environment variables."""

    def get(self) -> TokenCredential:
        return ClientSecretCredential(
            tenant_id=os.environ["AZURE_TENANT_ID"],
            client_id=os.environ["AZURE_CLIENT_ID"],
            client_secret=os.environ["AZURE_CLIENT_SECRET"],
        )
