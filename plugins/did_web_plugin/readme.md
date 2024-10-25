# DID Web plugin
This plugin is used to interact with the DID Web protocol. It allows you to create, resolve, and update DIDs on a DID Web compatible server.

## Installation
To install the plugin, run the following command in the terminal:
```bash
pip install did_web_plugin.v1_0
```
Then add this plugin to the `plugins` list in the `aries` section of your configuration file.
Example:
```yaml
plugins:
  - did_web_plugin.v1_0
```

## Usage
This plugin provides the following routes:

### Create a DID
To create a DID, send a POST request to `/wallet/did/create-new` with the following body:
```json
{
  "method": "web",
  "options": {
    "did": "did:web:aritrocoder.github.io:alice",
    "key_type": "ed25519"
  }
}
```
It adds the DID to the wallet and also stores it on the DID Web compatible server, registered with the plugin.

### Register a DID
To register a DID on the DID Web compatible server, send a POST request to `/wallet/did/create-from-external` with the following body:
```json
{
  "method": "web",
  "options": {
    "did": "did:web:aritrocoder.github.io:alice",
    "key_type": "ed25519"
  }
}
```
This will register the DID on the wallet and update it's verification method on the DID Web compatible server. To not update the verification method, use the default `wallet/did/create` API route.

### Resolve a DID
Resolution can be done by using the default `/wallet/did/resolve` API route.

### Changing the DID server
Changing the DID server requires altering few lines of the code, depending on the security and access levels in the server. In general, these lines should be changed:
- Line 354-359 in `did_web_plugin/did_web_plugin/v1_0/create.py`
- Line 246-251 in `did_web_plugin/did_web_plugin/v1_0/create.py`