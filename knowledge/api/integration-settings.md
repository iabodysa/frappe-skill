---
name: integration-settings
description: Eight settings DocTypes in frappe hold an outbound credential and Google Drive is the one that keeps both OAuth values as Data, so its refresh token sits in tabSingles in clear text.
triggers: ["DropboxSettings.onload", "get_dropbox_settings", "set_dropbox_token", "S3BackupSettings.validate", "take_backup", "LDAPSettings.validate", "connect_to_ldap", "get_file_picker_settings", "GoogleOAuth.validate_google_settings", "authorize", "refresh_access_token", "get_google_service_object", "handle_response", "get_access_token", "authorize_access", "get_google_drive_object", "GoogleCalendar.get_access_token", "google_callback", "GoogleContacts.get_access_token", "get_google_contacts_object", "PushNotificationSettings.validate_relay_server_setup", "PushNotification._get_credential", "auth_webhook", "get_google_indexing_object", "Dropbox Settings", "S3 Backup Settings", "Ldap Settings", "Google Settings", "Google Drive", "Google Calendar", "Google Contacts", "Push Notification Settings", "Website Settings", "Number of DB backups cannot be less than 1", "Queued for backup. It may take a few minutes to an hour.", "Ensure the user and group search paths are correct.", "which doctypes store an api credential", "oauth settings doctype", "the google refresh token is stored in plain text in our database", "a stored cloud credential is readable straight from the table", "why is the token not encrypted like the other password fields", "the drive upload works for an hour then stops until we reconnect", "backups to the cloud fail every day with an expired credential", "we have to reauthorize the connection over and over", "saving the settings page hangs and then throws a bucket error", "the settings screen makes a network call every time i save it", "the directory login says wrong username or password but the password is right", "the sign in test fails for a reason that has nothing to do with the password", "the check says the credential is set but the connection still fails", "which screens actually hold our external keys", "the file storage keys are blank in the form but uploads still work", "enabling push notifications refuses to save"]
product: frappe
---

# Integration settings

## paths

frappe/integrations/doctype/dropbox_settings/dropbox_settings.py — DropboxSettings.onload, get_dropbox_settings, set_dropbox_token
frappe/integrations/doctype/s3_backup_settings/s3_backup_settings.py — S3BackupSettings.validate, take_backup
frappe/integrations/doctype/ldap_settings/ldap_settings.py — LDAPSettings.validate, connect_to_ldap
frappe/integrations/doctype/google_settings/google_settings.py — get_file_picker_settings
frappe/integrations/google_oauth.py — GoogleOAuth.validate_google_settings, authorize, refresh_access_token, get_google_service_object, handle_response
frappe/integrations/doctype/google_drive/google_drive.py — get_access_token, authorize_access, get_google_drive_object
frappe/integrations/doctype/google_calendar/google_calendar.py — GoogleCalendar.get_access_token, authorize_access, google_callback
frappe/integrations/doctype/google_contacts/google_contacts.py — GoogleContacts.get_access_token, authorize_access, get_google_contacts_object
frappe/integrations/doctype/push_notification_settings/push_notification_settings.py — PushNotificationSettings.validate_relay_server_setup
frappe/push_notification.py — PushNotification._get_credential, auth_webhook
frappe/website/doctype/website_settings/google_indexing.py — get_google_indexing_object

## rules

MUST expect a clear-text refresh token in `tabSingles` on any site where Google Drive's `authorize_access` has run; `refresh_token` and `authorization_code` are declared `Data`, and `authorize_access` writes them with `frappe.db.set_single_value`.
MUST expect the same on `tabGoogle Calendar`; its fields are `Password`, but `authorize_access` and `google_callback` write them with `frappe.db.set_value`, so the column holds the token and no `__Auth` row exists. Re-save the record through the document to move the value.
MUST pass `fieldname="refresh_token"` when calling `get_google_service_object` from an app; `get_google_drive_object` and `get_google_contacts_object` both pass `indexing_refresh_token`, which belongs to `Website Settings` and is declared on neither, so the credentials are built with `refresh_token=None` and the client can hold an access token it cannot renew.
NEVER trust `validate_google_settings` or the credential test in `_get_credential`; both test the field for truth, and the mask is truthy, so they only catch a field that was never filled.
MUST expect the site config to stand in for the Dropbox app credential; an empty `app_access_key` falls back to `frappe.conf.dropbox_access_key` and an empty `app_secret_key` to `frappe.conf.dropbox_secret_key`, and `onload` flags that state to the form.
MUST expect a network call on every save of `S3 Backup Settings` while `enabled`; `validate` builds a boto3 client and calls `head_bucket`, turning a 403 into "Do not have permission" and a 404 into "Bucket not found".
MUST expect a live bind on every save of `LDAP Settings` while `enabled`.
NEVER read "Invalid username or password" from LDAP as a wrong password; `connect_to_ldap` raises that message for any failed bind, and a decrypt failure arrives there as `password=None`.
MUST read `S3 Backup Settings` as the one record whose secret read raises rather than returns `None`; every other read in frappe passes `raise_exception=False`.
MUST expect `get_file_picker_settings` to return `app_id` and `client_id` to any signed-in session.
MUST set `push_relay_server_url` in site config before enabling the push relay; `validate_relay_server_setup` throws without it.
MUST read one empty Push Notification credential pair as triggering a fresh registration against the relay, which saves the returned pair with `ignore_permissions=True` and commits.
MUST expect `Google Calendar` and `Google Contacts` to hold one record per user rather than a single, and MUST expect a missing refresh token there to raise a `ValidationError` naming `authorize_access`.

## values

Push Notification Settings: single; api_key Data, api_secret Password
Dropbox Settings: single; app_access_key Data, app_secret_key Password, dropbox_access_token Password, dropbox_refresh_token Password
S3 Backup Settings: single; access_key_id Data required, secret_access_key Password required
LDAP Settings: single; base_dn Data required, password Password required
Google Settings: single; client_id Data, api_key Data, app_id Data, client_secret Password
Google Drive: single; refresh_token Data, authorization_code Data
Google Calendar: one record per calendar, named `field:calendar_name`; refresh_token, authorization_code, next_sync_token all Password
Google Contacts: one record per address, named `format:GC-{email_id}`; refresh_token, authorization_code, next_sync_token all Password
site config fallbacks: dropbox_access_key, dropbox_secret_key
site config required: push_relay_server_url
S3 endpoint default: https://s3.amazonaws.com
relay registration token lifetime: 600 seconds

## how

Reach for one of these before writing a settings DocType of your own; the credential half is already solved, and copying the shape copies the mistakes too. The shape that is right is Dropbox: a `Password` field, written through the document, read with `get_password`. The shape that is wrong is Google Drive, which declares `Data` and writes with `set_single_value`, and Google Calendar, which declares `Password` and then writes past it — both leave the secret in a column any reader of the DocType can see.

Two of these records reach the network from inside `validate`. Saving `S3 Backup Settings` or `LDAP Settings` while enabled is not a local write; it is a live check that fails the save when the outside service is unreachable. That is deliberate and worth copying, but it means a migration that touches either record needs the service up.

Every credential test in this group is a truth test, and the mask is truthy. So none of them distinguishes a correct secret from a wrong one, only a filled field from an empty one. The first real check is always the provider's own refusal, and most of these read with `raise_exception=False`, which means a lost encryption key arrives as an error inside the provider's library rather than as a decrypt failure in frappe.
