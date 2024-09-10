# DID Sov plugin
This plugin is used to interact with the Key DID method. It allows you to create, resolve DIDs.

## Installation
To install the plugin, run the following command in the terminal:
```bash
pip install did_key_plugin.v1_0
```
Then add this plugin to the `plugins` list in the `aries` section of your configuration file.

Example:
```yaml
plugins:
  - did_key_plugin.v1_0
```

## Usage
This plugin adds did:key method support to the following existing routes:
- `/wallet/did/create`
- `/resolver/resolve/{did}`

Additionally, any other APIs/protocols that uses did:key method will run properly once the plugin is loaded.