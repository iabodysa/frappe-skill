# Task — call an outside service, or let one call this site

## Inbound — which endpoint the caller reaches

Which route does the caller ask for?
MUST publish the version the client is written against, because one version answers under two prefixes and the other spells the noun differently.
`knowledge/api/rest-routes.md`

What has the framework already checked when the method body starts?
MUST check the DocType permission inside the method, and MUST search the site for a Server Script that answers the same path above it.
`knowledge/api/whitelisted-method.md`

Is a Server Script answering this path, and what may it do?
MUST read `server_script_enabled` in `common_site_config.json` as the only switch, and MUST read the script as running with the caller's own permissions rather than elevated.
`knowledge/desk/server-script.md`

## Inbound — the caller is unauthenticated

What protects a Guest POST?
MUST authenticate the payload itself, because the session carries no CSRF token.
`knowledge/permission/csrf.md`

Which identity does an outside human hold on this site?
MUST set the user type and read the session as the portal rail.
`knowledge/permission/portal_identity.md`

## Inbound — proving the request came from who it claims

Does the framework verify an inbound body?
MUST write the signature check in the app, because the shipped primitive authenticates a signed GET link and refuses any request carrying a body.
`knowledge/api/inbound-verification.md`

How is the entry point limited?
MUST accept that the limiter reads and writes the counter separately, so a burst passes.
`knowledge/job/rate-limiter.md`

## Outbound — a webhook on a doc event

Which doc event and which queue carry the call?
MUST create one Webhook record per event, MUST name the background queue, and MUST NOT expect a delivery after a rollback, during an import, a patch, an install or a migrate.
`knowledge/api/webhook.md`

How is a delivery proven, and what does a failure leave?
MUST read the request log row as the only evidence, because the third attempt's failure raises nothing and no status field exists.
`knowledge/api/webhook.md`

Why did the disabled webhook keep firing?
MUST clear the site cache after editing the record, because the key is global and a direct SQL write runs no handler.
`knowledge/api/webhook.md`

## Outbound — calling the service from code

Which rules bind an outbound call?
MUST settle the timeout, the retry and the log before the first request.
`references/talking-to-an-outside-service.md`

What does the shipped request helper retry?
MUST write the backoff in the app, because the shared session repeats one status class five times with no wait and raises on the rest.
`knowledge/api/outbound-http.md`

What records the call?
MUST open the log row from the caller, because nothing else writes one.
`knowledge/api/integration-request.md`

## Where the credential lives

Where does a secret on a DocType actually sit?
MUST declare the field as Password and MUST NOT write it with a direct set, which stores it in clear text.
`knowledge/api/credential-storage.md`

Which shipped settings record holds this integration's secret, and in what?
MUST read each settings DocType's own field type, because one keeps both OAuth values as plain Data.
`knowledge/api/integration-settings.md`

## The service speaks OAuth2

Which record holds the client and which holds one user's token?
MUST measure the token's expiry from the row's own timestamp rather than from the issue time.
`knowledge/api/connected-app.md`

## The channel is one ERPNext ships a field for

Is WhatsApp a channel on this bench?
MUST build the outbound integration, because the shipped fields are two Data fields and the notification channel list has no arm for it.
`knowledge/api/whatsapp.md`
