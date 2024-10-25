import logging

from acapy_agent.config.injection_context import InjectionContext
from acapy_agent.wallet.did_method import DIDMethod, DIDMethods, HolderDefinedDid
from acapy_agent.wallet.key_type import ED25519, BLS12381G2
from acapy_agent.core.event_bus import EventBus
from acapy_agent.core.plugin_registry import PluginRegistry
from acapy_agent.core.protocol_registry import ProtocolRegistry

LOGGER = logging.getLogger(__name__)


async def setup(context: InjectionContext):
    LOGGER.info("> DID web plugin setup...")
    WEB = DIDMethod(
        name="web",
        key_types=[ED25519, BLS12381G2],
        rotation=True,
        holder_defined_did=HolderDefinedDid.REQUIRED,
    )
    did_methods = context.injector.inject_or(DIDMethods)
    did_methods.register(WEB)

    protocol_registry = context.inject(ProtocolRegistry)
    if not protocol_registry:
        raise ValueError("ProtocolRegistry missing in context")

    plugin_registry = context.inject(PluginRegistry)
    if not plugin_registry:
        raise ValueError("PluginRegistry missing in context")

    bus = context.inject(EventBus)
    if not bus:
        raise ValueError("EventBus missing in context")
    
    LOGGER.info("< DID web plugin setup complete")
