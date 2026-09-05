# What carries the credential, the retry and the log

An outbound integration needs three things and the framework ships something different for each:
the credential belongs in a `Password` field on a Settings DocType or in a Connected App, the retry
belongs to the request session, and the log is an Integration Request row that only
`create_request_log` writes. Name the one you are NOT using and why, because every one of the three
is silently absent by default rather than loudly missing.

| What the integration needs | What the framework ships | What it does not do |
|---|---|---|
| a static key or secret | a `Password` field on a Single Settings DocType | keep the value out of `__Auth` if written with `frappe.db.set_value` |
| an OAuth2 client and a per-user token | Connected App, with one Token Cache row per user | measure expiry from when the token was issued |
| the outbound call itself | `make_request` and its `make_*_request` siblings | back off, or retry anything but a 500 |
| a record of the call | Integration Request, opened by `create_request_log` | appear at all unless the caller opens it |
| an inbound call from the service | `verify_request` for a signed GET link | verify a body — nothing shipped does |
| an event pushed out on a document change | Webhook, queued per request and flushed after commit | raise on the third failed attempt |
| the route the service calls back on | `/api/method` for a whitelisted function | check any DocType permission |

The eight shipped Settings DocTypes differ in where each one puts its secret, and one of them keeps
both OAuth values as `Data`.

## Settled by

| what it settles | leaf |
|---|---|
| the `__Auth` move, the mask, and the clear-text write | `knowledge/api/credential-storage.md` |
| the eight DocTypes and the one storing Data | `knowledge/api/integration-settings.md` |
| the client side and the Token Cache expiry | `knowledge/api/connected-app.md` |
| the shared session, the `[500]` retry list, and no backoff | `knowledge/api/outbound-http.md` |
| the only writer of the log | `knowledge/api/integration-request.md` |
| the request-local queue, the three attempts, and the log row | `knowledge/api/webhook.md` |
| what `verify_request` covers and what it refuses | `knowledge/api/inbound-verification.md` |
| where v1 and v2 answer, and the noun each spells | `knowledge/api/rest-routes.md` |
| the whitelist, the verb, and the Server Script above them | `knowledge/api/whitelisted-method.md` |
| two Data fields, and no channel to send on | `knowledge/api/whatsapp.md` |
