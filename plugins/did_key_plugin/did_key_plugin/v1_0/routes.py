import logging

from aiohttp import web
from aiohttp_apispec import docs
from acapy_agent.wallet.base import WalletError
from did_key_plugin.v1_0.key import KeyDIDResolver
from acapy_agent.admin.request_context import AdminRequestContext

LOGGER = logging.getLogger(__name__)


@docs(
    tags=["DID Key Plugin"],
    summary="API endpoint to resolve a DID using the plugin. The default /resolver/resolve/{did} endpoint also works.",
)
async def plugin_resolve(request: web.Request):
    """Resolve a DID using the plugin."""
    body = await request.json()
    context: AdminRequestContext = request["context"]
    did = body.get("did")
    if not did:
        return web.json_response({"error": "Missing 'did' parameter"}, status=400)
    try:
        resolver = None
        if did.startswith("did:key:"):
            resolver = KeyDIDResolver()
        else:
            return web.json_response(
                {"error": "Only did:key DIDs are supported"}, status=400
            )
        did_info = await resolver._resolve(profile=context.profile, did=did)
    except WalletError as e:
        return web.json_response({"error": str(e)}, status=400)
    return web.json_response(did_info)


# async def register(app: web.Application):
#     """Register routes for this plugin."""
#     app.add_routes(
#         [
#             web.post("/wallet/did/key/resolve-did", plugin_resolve)
#         ]
#     )


# def post_process_routes(app: web.Application):
#     """Amend swagger API."""

#     # Add top-level tags description
#     if "tags" not in app._state["swagger_dict"]:
#         app._state["swagger_dict"]["tags"] = []
#     app._state["swagger_dict"]["tags"].append(
#         {"name": "DID Key Plugin", "description": "DID and tag policy management"}
#     )
