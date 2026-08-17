# Known Wix Failure Routes

## Connector requests reauthentication

Browser login does not prove the Wix connector is authorized. Retry the connector once after its reauthorization surface is completed. Do not replace the connector token with an account ID or ask the user to paste secrets into chat.

## CLI cannot reach `manage.wix.com`

Treat `ENOTFOUND` as an execution-network limitation, not a code or login failure. Preserve local evidence, report the full build incomplete, and resume in a network-enabled approved environment.

## `UnsupportedPackageManager`

The Wix CLI detector may reject a newer npm user-agent before compilation. Confirm the layer. A temporary compatible user-agent can distinguish detector failure from project failure, but is diagnostic—not a durable release fix. Record tested Node/npm/CLI versions.

## Astro/Wix imports appear frozen in the workspace

First test `import("astro/config")` and inspect the exact open file without printing Wix debug logs. In this PXPress workspace, Node 22 and Node 24 both stalled while reading many small dependency files under `Documents`, and eventually returned `ECANCELED`; the application source was not the cause. Prove the distinction with a temporary build directory, a clean dependency install using `--ignore-scripts`, and the same source/config files. Use an official, checksum-verified Node release when testing another runtime. Do not replace the project lockfile from the temporary install. The 2026-08-16 isolated run completed both Astro and `wix build`, so treat the original dependency tree/filesystem as the repair target.

## Development override has no app collections

`wix dev` can synchronize the app manifest and preview links without creating data-collection extensions. Wix documents that those collections materialize when the app is installed or updated with a released app version. Do not create same-ID manual collections as a shortcut because they can conflict with future app-owned collections. Keep the staging site isolated, preserve all effect flags as false, and require explicit release approval before creating a new app version.

## Direct localhost preview returns OAuth `unknown_error`

A raw request to the Astro dev port does not carry the authenticated Wix preview context. If the log shows token fetch `400` with `unknown_error`, open the CLI-generated Wix preview redirect in an authenticated browser before judging the application route. This failure is distinct from the automation-trigger `403` and from CMS collection absence.

## App namespace precondition (`428`)

An app override can fail when the Wix app lacks a namespace. Inspect first. Setting it is a Wix configuration mutation: capture prior state, choose a stable namespace, and retain rollback/approval evidence.

## Automation trigger returns `403`

When hook and automation validation are correct, inspect installed-app permission acceptance and deployed runtime identity. If permissions were added after installation, refresh authorization without uninstalling. Add only redacted token-type/request-ID diagnostics. One allowlisted test may prove acceptance/queueing; it does not prove inbox delivery.

## Safe log inspection

Never print or attach complete `.wix` debug logs. They can contain authorization headers, cookies, request bodies, site IDs, or customer data. Search only for the exact error/status, extract a narrow excerpt, and redact header/body values before storing evidence.
