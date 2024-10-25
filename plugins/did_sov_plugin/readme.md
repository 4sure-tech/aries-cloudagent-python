# DID Sov plugin
This plugin is used to interact with the Sovrin DID method. It allows you to create, resolve DIDs on a Indy ledger.

## Installation
To install the plugin, run the following command in the terminal:
```bash
pip install did_sov_plugin.v1_0
```
Then add this plugin to the `plugins` list in the `aries` section of your configuration file.

Example:
```yaml
plugins:
  - did_sov_plugin.v1_0
```

## Usage
This plugin adds did:sov method support to the following existing routes:
- `/wallet/did/create`
- `/resolver/resolve/{did}`

Additionally, any other APIs/protocols that uses did:sov method will run properly once the plugin is loaded.

Note: Without this plugin, ACA-py won't be able to start if you add a seed in the configuration.