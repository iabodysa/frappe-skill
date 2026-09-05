---
name: hooks
description: Every non-underscore value in an installed app's hooks.py is collected into one merged dict whatever its name, so a key no reader function asks for is stored and never read and the misspelling raises nothing.
triggers: ["_load_app_hooks", "get_hooks", "append_hook", "_is_valid_hook", "app_hooks", "get_installed_apps", "hooks.py", "hook key list", "which hook keys exist", "hook not firing", "hook key ignored", "list of frappe hooks", "custom hook key", "developer_mode hooks cache", "the code i registered never runs and nothing is logged", "why is my handler never called even though it is declared", "livid that a declared handler is silently ignored with no error", "i misspelled the setting name and nothing warned me at all", "how do i find the exact list of names i am allowed to declare", "which entries in that config file actually do something", "my setting is accepted but seems to have no effect anywhere", "changes to the app configuration are not picked up until a restart", "the old configuration keeps being used after i edited it", "how do i check what all the installed apps together declare for one setting"]
product: frappe
---

# Hook Keys

## paths

frappe/__init__.py — _load_app_hooks, get_hooks, append_hook, get_installed_apps, clear_cache, get_doc_hooks, get_domain_data, has_website_permission, override_whitelisted_method
frappe/app.py — init_request, run_after_request_hooks
frappe/apps.py — get_apps, get_incomplete_setup_route
frappe/auth.py — validate_auth_via_hooks
frappe/boot.py — add_home_page, get_additional_filters_from_hooks, get_bootinfo, remove_apps_with_incomplete_dependencies
frappe/core/api/user_invitation.py — get_allowed_invite_params
frappe/core/doctype/doctype/doctype.py — DocType.export_types_to_controller
frappe/core/doctype/domain/domain.py — Domain.get_domain_data
frappe/core/doctype/domain_settings/domain_settings.py — DomainSettings.restrict_roles_and_modules
frappe/core/doctype/installed_applications/installed_applications.py — get_apps_with_incomplete_dependencies
frappe/core/doctype/log_settings/log_settings.py — LogSettings.add_default_logtypes
frappe/core/doctype/navbar_settings/navbar_settings.py — get_app_logo
frappe/core/doctype/scheduled_job_type/scheduled_job_type.py — sync_jobs
frappe/core/doctype/user/user.py — User.send_welcome_mail_to_user
frappe/core/doctype/user_invitation/user_invitation.py — UserInvitation._get_allowed_roles, UserInvitation._get_email_title, UserInvitation._run_after_accept_hooks, UserInvitation.validate_role, get_allowed_apps
frappe/desk/doctype/changelog_feed/changelog_feed.py — _app_title, fetch_changelog_feed
frappe/desk/doctype/global_search_settings/global_search_settings.py — update_global_search_doctypes
frappe/desk/form/linked_with.py — get_exempted_doctypes
frappe/desk/page/leaderboard/leaderboard.py — get_leaderboard_config
frappe/desk/page/setup_wizard/setup_wizard.py — get_setup_complete_hooks, handle_setup_exception, run_setup_success
frappe/email/__init__.py — get_communication_doctype
frappe/email/email_body.py — EMail.make, get_footer, get_header, inline_style_in_html
frappe/gettext/translate.py — _get_ignored_strings
frappe/installer.py — install_app, remove_app
frappe/migrate.py — SiteMigration.post_schema_updates, SiteMigration.pre_schema_updates
frappe/model/base_document.py — import_controller
frappe/model/db_query.py — DatabaseQuery.get_permission_query_conditions
frappe/model/delete_doc.py — get_dynamic_linked_docs, get_linked_docs
frappe/model/meta.py — Meta.get_dashboard_data
frappe/model/naming.py — has_custom_parser
frappe/model/sync.py — remove_orphan_doctypes
frappe/modules/utils.py — get_app_publisher
frappe/parallel_test_runner.py — ParallelTestRunner.before_test_setup
frappe/patches/v13_0/jinja_hook.py — execute
frappe/permissions.py — has_controller_permissions
frappe/search/sqlite_search.py — get_search_classes
frappe/sessions.py — get
frappe/test_runner.py — main
frappe/translate.py — get_messages_from_custom_fields, get_messages_from_include_files, get_messages_from_workflow
frappe/utils/__init__.py — get_site_info
frappe/utils/background_jobs.py — execute_job
frappe/utils/fixtures.py — export_fixtures
frappe/utils/install.py — add_standard_navbar_items
frappe/utils/jinja.py — get_jinja_hooks, get_jloader
frappe/utils/print_utils.py — get_print
frappe/website/doctype/personal_data_deletion_request/personal_data_deletion_request.py — PersonalDataDeletionRequest.__init__
frappe/website/doctype/personal_data_download_request/personal_data_download_request.py — get_user_data
frappe/website/doctype/portal_settings/portal_settings.py — PortalSettings.sync_menu
frappe/website/doctype/web_page/web_page.py — get_dynamic_web_pages
frappe/website/page_renderers/base_template_page.py — BaseTemplatePage.set_base_template_if_missing, BaseTemplatePage.update_website_context
frappe/website/path_resolver.py — PathResolver.get_custom_page_renderers, PathResolver.resolve, get_website_rules, resolve_redirect
frappe/website/router.py — get_base_template, get_doctypes_with_web_view
frappe/website/utils.py — clear_cache, get_home_page_via_hooks, get_portal_sidebar_items, get_sidebar_items
frappe/www/list.py — get_list_context
frappe/www/login.py — get_context
frappe/www/printview.py — get_rendered_template

## rules

MUST spell a hook key exactly as the reader function asks for it, because `_load_app_hooks` collects every module attribute it finds and no code compares that name against a list of known keys.
NEVER read a silent hook as unregistered; a misspelled key is merged and stored under `app_hooks` like any other, and `get_hooks` returns an empty list to the reader that asked for the correct spelling.
MUST place a hook value as a plain module-level assignment; `_is_valid_hook` rejects a module, a function and a class, so `import frappe` at the top of hooks.py contributes nothing and a callable defined in hooks.py is dropped without a message.
NEVER begin a hook key with an underscore; `_load_app_hooks` skips every name that does.
MUST install an app on the site before expecting its hooks.py to be read; `_load_app_hooks` walks `get_installed_apps(_ensure_on_bench=True)`, so an app present on the bench and absent from the site contributes no key.
MUST expect a scalar hook value to reach its reader as a list, because `append_hook` wraps anything that is not a list and extends the existing list for that key across apps.
MUST expect a dict hook value to merge per inner key rather than replace, because `append_hook` recurses into the dict and lists the values under each inner key.
MUST set `developer_mode` on a site where a hooks.py edit has to take effect on the next request; without it `get_hooks` reads the merged dict from the cache value `app_hooks` and the edit is invisible until that value is gone.
MUST pass `app_name` to `get_hooks` to read one app's hooks.py alone; that branch calls `_load_app_hooks` directly and skips the cache in every mode.
NEVER pass a `default` to `get_hooks` expecting it to apply to a key some app declared; the default is returned only when the merged dict has no such key at all.
MUST name a new hook key in the app that reads it, and MUST read it with `frappe.get_hooks` from a function of that app, because a key frappe does not read is inert on its own.

## values

add_to_apps_screen: get_apps, get_incomplete_setup_route
after_app_install: install_app
after_app_uninstall: remove_app
after_job: execute_job
after_migrate: SiteMigration.post_schema_updates
after_request: run_after_request_hooks
app_include_js: get_messages_from_include_files
app_logo_url: get_app_logo
app_publisher: get_app_publisher
app_title: UserInvitation._get_email_title, _app_title, get_header
auth_hooks: validate_auth_via_hooks
auto_cancel_exempted_doctypes: get_exempted_doctypes
base_template: BaseTemplatePage.set_base_template_if_missing
base_template_map: get_base_template
before_app_install: install_app
before_app_uninstall: remove_app
before_job: execute_job
before_migrate: SiteMigration.pre_schema_updates
before_request: init_request
before_tests: ParallelTestRunner.before_test_setup, main
calendars: get_bootinfo
clear_cache: clear_cache
communication_doctypes: get_communication_doctype
default_log_clearing_doctypes: LogSettings.add_default_logtypes
default_mail_footer: get_footer
doc_events: get_doc_hooks
domains: Domain.get_domain_data, DomainSettings.restrict_roles_and_modules, get_domain_data
email_css: inline_style_in_html
export_python_type_annotations: DocType.export_types_to_controller
extend_bootinfo: get
filters_config: get_additional_filters_from_hooks
fixtures: export_fixtures, get_messages_from_custom_fields, get_messages_from_workflow
get_changelog_feed: fetch_changelog_feed
get_print_format_template: get_rendered_template
get_site_info: get_site_info
get_web_pages_with_dynamic_routes: get_dynamic_web_pages
get_website_user_home_page: get_home_page_via_hooks
global_search_doctypes: update_global_search_doctypes
has_permission: has_controller_permissions
has_website_permission: has_website_permission
home_page: get_home_page_via_hooks
ignore_links_on_delete: get_dynamic_linked_docs, get_linked_docs
ignore_translatable_strings_from: _get_ignored_strings
jenv: execute
jinja: get_jinja_hooks
leaderboards: get_leaderboard_config
look_for_sidebar_json: get_sidebar_items
make_email_body_message: EMail.make
naming_series_variables: has_custom_parser
on_print_pdf: get_print
override_doctype_class: import_controller, remove_orphan_doctypes
override_doctype_dashboards: Meta.get_dashboard_data
override_whitelisted_methods: override_whitelisted_method
page_renderer: PathResolver.get_custom_page_renderers
pdf_body_html: get_rendered_template
pdf_generator: get_print
permission_query_conditions: DatabaseQuery.get_permission_query_conditions
persistent_cache_keys: clear_cache
portal_menu_items: get_portal_sidebar_items
required_apps: get_apps_with_incomplete_dependencies, remove_apps_with_incomplete_dependencies
role_home_page: get_home_page_via_hooks
scheduler_events: sync_jobs
setup_wizard_complete: get_setup_complete_hooks
setup_wizard_exception: handle_setup_exception
setup_wizard_requires: add_home_page
setup_wizard_success: run_setup_success
signup_form_template: get_context
sqlite_search: get_search_classes
standard_help_items: add_standard_navbar_items
standard_navbar_items: add_standard_navbar_items
standard_portal_menu_items: PortalSettings.sync_menu
template_apps: get_jloader
treeviews: get_bootinfo
update_website_context: BaseTemplatePage.update_website_context
user_data_fields: PersonalDataDeletionRequest.__init__, get_user_data
user_invitation: UserInvitation._get_allowed_roles, UserInvitation._run_after_accept_hooks, UserInvitation.validate_role, get_allowed_apps, get_allowed_invite_params
web_include_js: get_messages_from_include_files
webform_list_context: get_list_context
website_clear_cache: clear_cache
website_generators: get_doctypes_with_web_view
website_path_resolver: PathResolver.resolve
website_redirects: resolve_redirect
website_route_rules: get_website_rules
website_user_home_page: get_home_page_via_hooks
welcome_email: User.send_welcome_mail_to_user

## how

hooks.py is not a schema. It is a Python module whose attributes are harvested, so the set of keys
that mean anything is exactly the set of names some function passes to `get_hooks`, and that set is
the table above. Anything else in the file is collected, merged and stored, and then waited on by
nobody. This is why a hook that does not fire almost never raises: the framework has no idea the key
was meant to be one it knows.

So debug a dead hook by finding its reader, not by re-reading the app. The key names the function
that consumes it; if the table has no row for the key, the key is invented and the work is to write
the reader too.

Two mechanical traps sit before the reader is even reached. A value that is a function, a class or an
imported module is dropped by the type test, so hooks.py holds data and never definitions — a handler
is named as a dotted string, not as an object. And outside developer_mode the merged dict is cached
under `app_hooks`, so an edit to hooks.py changes nothing on the next request until that value goes.
