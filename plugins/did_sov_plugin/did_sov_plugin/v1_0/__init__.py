import logging

from acapy_agent.config.injection_context import InjectionContext
from acapy_agent.wallet.did_method import DIDMethod, DIDMethods, HolderDefinedDid
from acapy_agent.wallet.key_type import ED25519
from acapy_agent.core.event_bus import EventBus
from acapy_agent.core.plugin_registry import PluginRegistry
from acapy_agent.core.protocol_registry import ProtocolRegistry

LOGGER = logging.getLogger(__name__)


async def setup(context: InjectionContext):
    LOGGER.info("> DID sov plugin setup...")
    SOV = DIDMethod(
        name="sov",
        key_types=[ED25519],
        rotation=True,
        holder_defined_did=HolderDefinedDid.ALLOWED,
    )
    did_methods = context.injector.inject_or(DIDMethods)
    did_methods.register(SOV)

    protocol_registry = context.inject(ProtocolRegistry)
    if not protocol_registry:
        raise ValueError("ProtocolRegistry missing in context")

    plugin_registry = context.inject(PluginRegistry)
    if not plugin_registry:
        raise ValueError("PluginRegistry missing in context")

    bus = context.inject(EventBus)
    if not bus:
        raise ValueError("EventBus missing in context")
    LOGGER.info("< DID sov plugin setup complete")
