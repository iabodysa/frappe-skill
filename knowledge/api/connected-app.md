---
name: connected-app
description: Connected App is the OAuth2 client side and one Token Cache row holds one user's token, whose expiry is measured from the row's modified timestamp rather than from when the token was issued.
triggers: ["ConnectedApp.validate", "get_oauth2_session", "initiate_web_application_flow", "get_user_token", "get_token_cache", "get_scopes", "get_query_params", "get_active_token", "get_backend_app_token", "get_openid_configuration", "callback", "client_id", "client_secret", "redirect_uri", "authorization_uri", "token_uri", "revocation_uri", "userinfo_uri", "introspection_uri", "openid_configuration", "scopes", "query_parameters", "TokenCache.get_auth_header", "update_data", "get_expires_in", "is_expired", "get_json", "autoname", "access_token", "refresh_token", "expires_in", "state", "success_uri", "token_type", "authorize", "get_token", "revoke_token", "openid_profile", "introspect_token", "Token Cache", "Please enter OpenID Configuration URL", "Invalid Parameters.", "Invalid token state! Check if the token has been created by the OAuth user.", "oauth2 client credentials", "connected app token expiry", "the token looks fresh but the other system keeps rejecting it", "our access token expires way earlier than it should", "why does the saved token suddenly say it is still valid when it is dead", "the stored token clock resets every time we touch the record", "the integration silently stops working and nothing is in the error log", "getting a none instead of a token and the next line blows up", "why did my refresh come back empty with no error", "the scheduled job just returns a login url instead of doing the work", "background job tries to send the user to a sign in page", "the callback url i typed keeps getting overwritten when i save", "i set the redirect address and it changed itself back", "which side do i use when another system wants to log into us", "my extra login parameters are ignored by the provider", "my database changes got committed halfway through the login flow"]
product: frappe
---

# Connected App

## paths

frappe/integrations/doctype/connected_app/connected_app.py — ConnectedApp.validate, get_oauth2_session, initiate_web_application_flow, get_user_token, get_token_cache, get_scopes, get_query_params, get_active_token, get_backend_app_token, get_openid_configuration, callback
frappe/integrations/doctype/connected_app/connected_app.json — client_id, client_secret, redirect_uri, authorization_uri, token_uri, revocation_uri, userinfo_uri, introspection_uri, openid_configuration, scopes, query_parameters
frappe/integrations/doctype/token_cache/token_cache.py — TokenCache.get_auth_header, update_data, get_expires_in, is_expired, get_json
frappe/integrations/doctype/token_cache/token_cache.json — autoname, access_token, refresh_token, expires_in, state, scopes, success_uri, token_type
frappe/integrations/oauth2.py — authorize, get_token, revoke_token, openid_profile, openid_configuration, introspect_token

## rules

MUST call `get_active_token(user)` for a user-delegated call, and MUST test the return before using it; a refresh failure logs `Token Refresh Error` and returns `None`.
MUST call `get_backend_app_token()` for a machine-to-machine call; it caches under the empty-string user, so it never picks up whoever is signed in.
MUST read `get_auth_header()` as the header builder; it returns `{"Authorization": "Bearer <token>"}` and raises `DoesNotExistError` when `access_token` is empty.
MUST accept a commit inside the flow; `initiate_web_application_flow` and `get_backend_app_token` both call `frappe.db.commit()`, so a caller inside a transaction has that transaction split under it.
NEVER call `get_user_token` from a background job; with no cached token it sets `frappe.local.response["type"] = "redirect"` and returns the URL, which no job can follow.
NEVER type a `redirect_uri`; `validate` recomputes it on every save from `frappe.utils.get_url()` and the `callback` method path.
NEVER use Connected App when the site is the OAuth2 server; that side is `OAuth Client`, `OAuth Bearer Token` and the endpoints in `frappe/integrations/oauth2.py`.
MUST read expiry as measured from the Token Cache row's `modified` timestamp plus `expires_in`, not from when the provider issued the token; any save of that row moves the expiry forward.
MUST expect one Token Cache row per `(connected app, user)` pair, named `{connected_app}-{user}` by `autoname`.
MUST expect `update_data` to reject a token whose `token_type` is neither bearer nor MAC, with `Received an invalid token type`.
MUST put every scope in the `scopes` child table and every extra authorization parameter in `query_parameters`; `get_scopes` and `get_query_params` read nothing else.

## values

client credential: `client_id` Data, `client_secret` Password
computed on validate: `redirect_uri`
callback endpoint: `/api/method/frappe.integrations.doctype.connected_app.connected_app.callback/<name>`
Token Cache name: `{connected_app}-{user}`
backend token user: the empty string
token fields: `access_token` and `refresh_token`, both Password
expiry basis: row `modified` plus `expires_in` seconds
accepted token types: bearer, MAC
server-side DocTypes: OAuth Client, OAuth Bearer Token, OAuth Authorization Code

## how

Connected App is the client half of OAuth2 and nothing else. If the question is how another system signs in to this site, none of this applies — that is `OAuth Client` and the endpoints in `frappe/integrations/oauth2.py`. Reading the wrong half is the common mistake, because both halves store a client id and a secret.

Choose between the two token getters by who the call is on behalf of. A user-delegated call needs `get_active_token`, which refreshes and can hand back `None`; a service-to-service call needs `get_backend_app_token`, which deliberately caches under an empty user so a background job and a signed-in session share one token. Neither raises on a refresh failure, so a caller that skips the `None` test turns an expired grant into an attribute error somewhere further down.

Expiry is derived, not stored. The row keeps `expires_in` as a duration and compares against its own `modified`, so anything that saves the row — including a save that changed nothing — resets the clock and makes a dead token look fresh. Treat a token that reports plenty of life but is refused by the provider as this, and refresh rather than trusting `is_expired`.
