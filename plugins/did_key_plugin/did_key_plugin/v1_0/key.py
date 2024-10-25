"""Key DID Resolver.

Resolution is performed using the IndyLedger class.
"""

from typing import Optional, Pattern, Sequence, Text

from acapy_agent.config.injection_context import InjectionContext
from acapy_agent.core.profile import Profile
from acapy_agent.messaging.valid import DIDKey as DIDKeyType

from acapy_agent.resolver.base import BaseDIDResolver, DIDNotFound, ResolverType

from did_key_plugin.v1_0.did_key import DIDKey


class KeyDIDResolver(BaseDIDResolver):
    """Key DID Resolver."""

    def __init__(self):
        """Initialize Key Resolver."""
        super().__init__(ResolverType.NATIVE)

    async def setup(self, context: InjectionContext):
        """Perform required setup for Key DID resolution."""

    @property
    def supported_did_regex(self) -> Pattern:
        """Return supported_did_regex of Key DID Resolver."""
        return DIDKeyType.PATTERN

    async def _resolve(
        self,
        profile: Profile,
        did: str,
        service_accept: Optional[Sequence[Text]] = None,
    ) -> dict:
        """Resolve a Key DID."""
        try:
            did_key = DIDKey.from_did(did)

        except Exception as e:
            raise DIDNotFound(f"Unable to resolve did: {did}") from e

        return did_key.did_doc
