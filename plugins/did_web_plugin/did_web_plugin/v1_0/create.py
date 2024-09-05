import logging
import requests

from aiohttp import web
from aiohttp_apispec import docs, request_schema, response_schema

from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.wallet.base import BaseWallet, WalletError
from aries_cloudagent.wallet.did_method import (
    PEER2,
    PEER4,
    DIDMethods,
    HolderDefinedDid,
)
from aries_cloudagent.wallet.key_type import ED25519, KeyTypes
from aries_cloudagent.wallet.did_info import DIDInfo
from aries_cloudagent.wallet.did_posture import DIDPosture
from aries_cloudagent.wallet.routes import DIDCreateSchema, DIDResultSchema

LOGGER = logging.getLogger(__name__)

key_verification_mapping = {
    "ed25519": "Ed25519VerificationKey2018",
    "bls12381g2": "Bls12381G2Key2020",
}


def format_did_info(info: DIDInfo):
    """Serialize a DIDInfo object."""
    if info:
        return {
            "did": info.did,
            "verkey": info.verkey,
            "posture": DIDPosture.get(info.metadata).moniker,
            "key_type": info.key_type.key_type,
            "method": info.method.method_name,
            "metadata": info.metadata,
        }


@docs(
    tags=["DID Web Plugin"],
    summary="Register a new DID. DID should be already present in the DID server. Updates verkey in the DID server.",
)
@request_schema(DIDCreateSchema())
@response_schema(DIDResultSchema, 200, description="")
async def plugin_add_did(request: web.BaseRequest):
    """Request handler for creating a new local DID in the wallet.

    Args:
        request: aiohttp request object

    Returns:
        The DID info

    """
    context: AdminRequestContext = request["context"]

    try:
        body = await request.json()
    except Exception:
        body = {}

    seed = body.get("seed") or None
    if seed and not context.settings.get("wallet.allow_insecure_seed"):
        raise web.HTTPBadRequest(reason="Seed support is not enabled")
    info = None
    async with context.session() as session:
        did_methods = session.inject(DIDMethods)

        method = did_methods.from_method(body.get("method", "web"))
        if not method:
            raise web.HTTPForbidden(
                reason=f"method {body.get('method')} is not supported by the agent."
            )

        key_types = session.inject(KeyTypes)
        # set default method and key type for backwards compat
        key_type = (
            key_types.from_key_type(body.get("options", {}).get("key_type", ""))
            or ED25519
        )
        if not method.supports_key_type(key_type):
            raise web.HTTPForbidden(
                reason=(
                    f"method {method.method_name} does not"
                    f" support key type {key_type.key_type}"
                )
            )

        did = body.get("options", {}).get("did")
        if method.holder_defined_did() == HolderDefinedDid.NO and did:
            raise web.HTTPForbidden(
                reason=f"method {method.method_name} does not support user-defined DIDs"
            )
        elif method.holder_defined_did() == HolderDefinedDid.REQUIRED and not did:
            raise web.HTTPBadRequest(
                reason=f"method {method.method_name} requires a user-defined DIDs"
            )

        wallet = session.inject_or(BaseWallet)
        if not wallet:
            raise web.HTTPForbidden(reason="No wallet available")
        try:
            is_did_peer_2 = method.method_name == PEER2.method_name
            is_did_peer_4 = method.method_name == PEER4.method_name
            if is_did_peer_2 or is_did_peer_4:
                logging.error("Only DID web for now")
            else:
                info = await wallet.create_local_did(
                    method=method, key_type=key_type, seed=seed, did=did
                )

                # update verkey on DID doc
                update_body = {
                    "id": f"{info.did}#key-1",
                    "type": "DIDCommMessaging",
                    "publicKeyBase58": info.verkey,
                }
                did_id = info.did.replace(":", "%3A")
                url = f"https://acapy-poc.nborbit.io/did/{did_id}"
                headers = {
                    "accept": "*/*",
                    "Content-Type": "application/json",
                }
                response = requests.put(url, json=update_body, headers=headers)

                if response.status_code != 200:
                    raise WalletError("Error updating DID doc")
                logging.info("DID doc updated successfully")
        except WalletError as err:
            raise web.HTTPBadRequest(reason=err.roll_up) from err

    return web.json_response({"result": format_did_info(info)})


@docs(tags=["DID Web Plugin"], summary="Create a new DID in server and register in wallet.")
@request_schema(DIDCreateSchema())
@response_schema(DIDResultSchema, 200, description="")
async def plugin_new_did(request: web.BaseRequest):
    """Request handler for creating a new DID in the wallet.

    Args:
        request: aiohttp request object

    Returns:
        The DID info

    """
    context: AdminRequestContext = request["context"]

    try:
        body = await request.json()
    except Exception:
        body = {}

    seed = body.get("seed") or None
    if seed and not context.settings.get("wallet.allow_insecure_seed"):
        raise web.HTTPBadRequest(reason="Seed support is not enabled")
    info = None
    async with context.session() as session:
        did_methods = session.inject(DIDMethods)

        method = did_methods.from_method(body.get("method", "web"))
        if not method:
            raise web.HTTPForbidden(
                reason=f"method {body.get('method')} is not supported by the agent."
            )
        
        if method.method_name != "web":
            raise web.HTTPForbidden(
                reason=f"method {method.method_name} is not supported by the plugin. Use 'web' method."
            )

        key_types = session.inject(KeyTypes)
        # set default method and key type for backwards compat
        key_type = (
            key_types.from_key_type(body.get("options", {}).get("key_type", ""))
            or ED25519
        )
        if not method.supports_key_type(key_type):
            raise web.HTTPForbidden(
                reason=(
                    f"method {method.method_name} does not"
                    f" support key type {key_type.key_type}"
                )
            )

        did = body.get("options", {}).get("did")
        if method.holder_defined_did() == HolderDefinedDid.NO and did:
            raise web.HTTPForbidden(
                reason=f"method {method.method_name} does not support user-defined DIDs"
            )
        elif method.holder_defined_did() == HolderDefinedDid.REQUIRED and not did:
            raise web.HTTPBadRequest(
                reason=f"method {method.method_name} requires a user-defined DIDs"
            )

        wallet = session.inject_or(BaseWallet)
        if not wallet:
            raise web.HTTPForbidden(reason="No wallet available")
        try:
            is_did_peer_2 = method.method_name == PEER2.method_name
            is_did_peer_4 = method.method_name == PEER4.method_name
            if is_did_peer_2 or is_did_peer_4:
                logging.error("Only DID web for now")
            else:
                info = await wallet.create_local_did(
                    method=method, key_type=key_type, seed=seed, did=did
                )

                # update verkey on DID doc
                create_body = {
                    "method": "web",
                    "options": {
                        "did": info.did,
                        "keyType": key_type.key_type,
                        "service": [
                            {
                                "id": f"{info.did}#did-communication",
                                "type": "DIDCommMessaging",
                                "serviceEndpoint": context.settings.get("default_endpoint"),
                                "recipientKeys": [f"{info.did}#key-1"],
                                "routingKeys": [],
                                "accept": ["didcomm/aip2;env=rfc19"],
                                "priority": 1
                            }
                        ],
                        "verificationMethod": [
                            {
                                "type": key_verification_mapping[key_type.key_type],
                                "publicKeyBase58": info.verkey,
                            }
                        ],
                    },
                    "publish": True,
                }
                url = "https://acapy-poc.nborbit.io/did"
                headers = {
                    "accept": "*/*",
                    "Content-Type": "application/json",
                }
                response = requests.post(url, json=create_body, headers=headers)

                if response.status_code != 201:
                    raise WalletError(
                        f"{response.status_code}: Error creating DID doc: {response.text}"
                    )
                logging.info("DID doc created successfully")
        except WalletError as err:
            raise web.HTTPBadRequest(reason=err.roll_up) from err

    return web.json_response({"result": format_did_info(info)})
