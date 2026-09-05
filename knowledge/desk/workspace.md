---
name: workspace
description: A Workspace shows only what its own links child table names, and a Workspace whose roles table is empty is shown to every logged-in user.
triggers: ["Workspace.is_permitted", "Workspace.is_item_allowed", "Workspace.get_links", "Workspace._prepare_item", "Workspace.get_number_cards", "get_workspace_sidebar_items", "get_custom_reports_and_doctypes", "get_custom_doctype_list", "get_custom_report_list", "Workspace.get_module_wise_workspaces", "last_sequence_id", "roles", "links", "public", "for_user", "hide_custom", "sequence_id", "build_domain_restriced_doctype_cache", "build_domain_restriced_page_cache", "get_active_domains", "DatabaseQuery.prepare_filter_condition", "set_workspace", "Domain Settings", "You need to be Workspace Manager to edit this document", "Content data shoud be a list", "You need to be Workspace Manager to delete a public workspace.", "workspace not showing for a role", "workspace links", "my new screen does not appear anywhere in the side menu", "why is there no link to my list even though the user can open it by url", "the report is missing from the sidebar but it opens if i type the address", "a user with one role can see every section in the menu including payroll", "why does everyone see all the menu sections regardless of their role", "i restricted the section by role and it is still visible to everybody", "after the upgrade all the menu links vanished for normal users", "everything works for the admin account but staff see an empty menu", "why do the links only disappear for some accounts and not for me", "one menu entry is greyed out and i cannot click it", "the trail at the top of the page points to the wrong section", "i changed the order number but the top breadcrumb still shows the old section"]
product: frappe
---

# Workspace

## paths

frappe/desk/desktop.py — Workspace.is_permitted, Workspace.is_item_allowed, Workspace.get_links, Workspace._prepare_item, Workspace.get_number_cards, get_workspace_sidebar_items, get_custom_reports_and_doctypes, get_custom_doctype_list, get_custom_report_list
frappe/desk/doctype/workspace/workspace.py — Workspace.get_module_wise_workspaces, last_sequence_id
frappe/desk/doctype/workspace/workspace.json — roles, links, public, for_user, hide_custom, sequence_id
frappe/cache_manager.py — build_domain_restriced_doctype_cache, build_domain_restriced_page_cache
frappe/core/doctype/domain_settings/domain_settings.py — get_active_domains
frappe/model/db_query.py — DatabaseQuery.prepare_filter_condition
frappe/public/js/frappe/views/breadcrumbs.js — set_workspace

## rules

MUST add a row to the Workspace links child table for every DocType and Report an app ships, because get_custom_doctype_list filters on `custom: 1` and get_custom_report_list on `is_standard: "No"`, so a shipped DocType and a standard Report are in neither list.
MUST read an empty roles child table as public: is_permitted returns True when both the roles table and get_custom_allowed_roles are empty.
MUST put a role row on every Workspace the deployment does not intend every logged-in user to reach, or disable the stock Workspaces it does not use.
NEVER read is_permitted returning True as proof a Workspace is restricted; it returns True for a Workspace nobody restricted.
MUST read `domain_restricted_doctypes` as the list a link must BE IN — is_item_allowed renders a DocType link only when the name is in `can_read` AND in `restricted_doctypes`.
MUST read every Workspace DocType link disappearing at once for every non-Administrator user as the domain cache, and a single link disappearing as a DocPerm.
NEVER test a domain regression as Administrator; is_item_allowed returns True for Administrator before it reads the cache.
MUST rebuild the domain cache after a migrate, because build_domain_restriced_doctype_cache returns early under in_patch, in_install, in_migrate, in_import and in_setup_wizard and leaves whatever preceded it.
NEVER set sequence_id to move a module breadcrumb; get_module_wise_workspaces orders by `creation` and set_workspace takes index 0 of that list.
MUST set hide_custom when the links child table is to be the only source of entries.
MUST read a greyed link as `incomplete_dependencies`, which _prepare_item sets when a DocType named in `item.dependencies` holds no record.

## values

link sources: the links child table, plus the Custom Documents and Custom Reports groups unless hide_custom
Custom Documents filter: custom 1, istable 0, module
Custom Reports filter: is_standard No, disabled 0, module
roles empty: shown to every logged-in user
breadcrumb target: earliest creation among Workspaces with public 1 and for_user ""
sequence_id: orders the sidebar, never the breadcrumb
domain match: get_active_domains appends "", and prepare_filter_condition wraps a nullable column in ifnull(col, '') for every operator but = and like

## how

A Workspace is a declared list, not a discovery. get_links reads the links child table and adds exactly two groups on top of it, and both of those are filtered to what the UI drew rather than what an app shipped. So a DocType exported to an app folder leaves the sidebar the moment `custom` flips to 0, and a Report leaves it the moment `is_standard` becomes Yes. Nothing raises: the route still resolves and the DocPerm still permits, so the only symptom is a screen with no way in. Ship the links row in the Workspace JSON and the question does not arise.

Read a missing link by how many are missing. One link is a permission question — `can_read`. Every DocType link on every Workspace for every non-Administrator user is the domain cache, and the cache holds only because two independent halves agree: the empty domain is an active domain, and a NULL `restrict_to_domain` is compared as `''`. Break either half and no permission has changed while nothing renders.

Permission on the Workspace itself is the opposite default to permission on data. An empty roles table means public, and the stock Workspaces ship with it empty, so a user with one role reads a sidebar full of Payroll and Accounting entries whose data is then refused. The refusal is correct and the sidebar is the defect: it teaches the operator that links do not work.

Two orderings exist and only one can be set. The sidebar reads sequence_id and the module breadcrumb reads `creation`. An app that needs a guaranteed module root has to control that timestamp order, and nothing in the DocType declares the guarantee, so assert it on the rendered anchor rather than assume it.
