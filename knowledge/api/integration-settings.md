---
name: integration-settings
description: Five settings DocTypes in frappe hold an outbound credential and Google Calendar is the one that declares both OAuth values as Password yet writes them with frappe.db.set_value, so its refresh token sits in tabGoogle Calendar in clear text.
triggers: ["LDAPSettings.validate", "connect_to_ldap", "get_file_picker_settings", "GoogleOAuth.validate_google_settings", "authorize", "refresh_access_token", "get_google_service_object", "handle_response", "get_access_token", "authorize_access", "GoogleCalendar.get_access_token", "google_callback", "GoogleContacts.get_access_token", "get_google_contacts_object", "PushNotificationSettings.validate_relay_server_setup", "PushNotification._get_credential", "auth_webhook", "get_google_indexing_object", "Ldap Settings", "Google Settings", "Google Calendar", "Google Contacts", "Push Notification Settings", "Website Settings", "Ensure the user and group search paths are correct.", "which doctypes store an api credential", "oauth settings doctype", "the google calendar refresh token is stored in plain text in our database", "a stored cloud credential is readable straight from the table", "why is the token not encrypted like the other password fields", "we have to reauthorize the connection over and over", "the settings screen makes a network call every time i save it", "the directory login says wrong username or password but the password is right", "the sign in test fails for a reason that has nothing to do with the password", "the check says the credential is set but the connection still fails", "which screens actually hold our external keys", "the file storage keys are blank in the form but uploads still work", "enabling push notifications refuses to save", "the push notification secret read throws instead of coming back empty"]
product: frappe
---

# Integration settings

## paths

frappe/integrations/doctype/ldap_settings/ldap_settings.py — LDAPSettings.validate, connect_to_ldap
frappe/integrations/doctype/google_settings/google_settings.py — get_file_picker_settings
frappe/integrations/google_oauth.py — GoogleOAuth.validate_google_settings, authorize, refresh_access_token, get_google_service_object, handle_response
frappe/integrations/doctype/google_calendar/google_calendar.py — GoogleCalendar.get_access_token, authorize_access, google_callback
frappe/integrations/doctype/google_contacts/google_contacts.py — GoogleContacts.get_access_token, authorize_access, get_google_contacts_object
frappe/integrations/doctype/push_notification_settings/push_notification_settings.py — PushNotificationSettings.validate_relay_server_setup
frappe/push_notification.py — PushNotification._get_credential, auth_webhook
frappe/website/doctype/website_settings/google_indexing.py — get_google_indexing_object

## rules

MUST expect a clear-text refresh token in `tabGoogle Calendar`; `refresh_token` and `authorization_code` are declared `Password`, but `authorize_access` and `google_callback` write them with `frappe.db.set_value`, so the column holds the token and no `__Auth` row exists. Re-save the record through the document to move the value.
MUST pass `fieldname="refresh_token"` when calling `get_google_service_object` from an app; `get_google_contacts_object` passes `indexing_refresh_token`, which belongs to `Website Settings` and is declared on neither, so the credentials are built with `refresh_token=None` and the client can hold an access token it cannot renew.
NEVER trust `validate_google_settings` or the credential test in `_get_credential`; both test the field for truth, and the mask is truthy, so they only catch a field that was never filled.
MUST expect a live bind on every save of `LDAP Settings` while `enabled`.
NEVER read "Invalid username or password" from LDAP as a wrong password; `connect_to_ldap` raises that message for any failed bind, and a decrypt failure arrives there as `password=None`.
MUST read `Push Notification Settings` as the one record whose secret read raises rather than returns `None`; `_get_credential` calls `get_password("api_secret")` with no `raise_exception=False`, while every other read in this group passes it.
MUST expect `get_file_picker_settings` to return `app_id` and `client_id` to any signed-in session.
MUST set `push_relay_server_url` in site config before enabling the push relay; `validate_relay_server_setup` throws without it.
MUST read one empty Push Notification credential pair as triggering a fresh registration against the relay, which saves the returned pair with `ignore_permissions=True` and commits.
MUST expect `Google Calendar` and `Google Contacts` to hold one record per user rather than a single, and MUST expect a missing refresh token there to raise a `ValidationError` naming `authorize_access`.

## values

Push Notification Settings: single; api_key Data, api_secret Password
LDAP Settings: single; base_dn Data required, password Password required
Google Settings: single; client_id Data, api_key Data, app_id Data, client_secret Password
Google Calendar: one record per calendar, named `field:calendar_name`; refresh_token, authorization_code, next_sync_token all Password
Google Contacts: one record per address, named `format:GC-{email_id}`; refresh_token, authorization_code, next_sync_token all Password
site config required: push_relay_server_url
relay registration token lifetime: 600 seconds

## how

Reach for one of these before writing a settings DocType of your own; the credential half is already solved, and copying the shape copies the mistakes too. The shape that is right is Push Notification Settings: a `Password` field, written through the document on save or on `ignore_permissions=True` re-registration, read with `get_password`. The shape that is wrong is Google Calendar, which declares `Password` and then writes past it with `frappe.db.set_value` — the secret lands in a column any reader of the DocType can see, with no `__Auth` row behind it.

One of these records reaches the network from inside `validate`. Saving `LDAP Settings` while enabled is not a local write; it is a live bind that fails the save when the directory is unreachable. That is deliberate and worth copying, but it means a migration that touches the record needs the directory up.

Every credential test in this group is a truth test, and the mask is truthy. So none of them distinguishes a correct secret from a wrong one, only a filled field from an empty one. The first real check is always the provider's own refusal, and most of these read with `raise_exception=False`, which means a lost encryption key arrives as an error inside the provider's library rather than as a decrypt failure in frappe.
