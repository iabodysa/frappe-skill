---
name: role
description: Has Role is one child table shared by nine parents, so a role list is never a user list, and an empty role list on a Page or a Report permits instead of refusing.
triggers: ["istable", "get_users_with_role", "get_roles", "get_doctype_roles", "get_all_perms", "ALL_USER_ROLE", "SYSTEM_USER_ROLE", "GUEST_ROLE", "is_permitted", "get_custom_allowed_roles", "get", "getpage", "Has Role", "Page", "Report", "Custom Role", "Not in Developer Mode", "Only Administrator can edit", "Cannot edit a standard report. Please duplicate and create a new report", "has role child table", "empty role list permission", "counting who holds this role gives a number far bigger than the user list", "my query for role holders returned reports and dashboards instead of people", "why does the count of users with a role not match the users i can see?", "i left the allowed roles empty expecting nobody to see it and everyone can open it", "a page with no role set is open to anyone including logged out visitors", "is an empty roles list the same as nobody is allowed?", "an anonymous visitor can load our internal page", "portal customers pass a check i wrote for staff only", "why do website users satisfy my role condition?", "i added roles to the report but an old list still decides who sees it"]
product: frappe
---

# Role

## paths

frappe/core/doctype/has_role/has_role.json — istable, role
frappe/utils/user.py — get_users_with_role
frappe/permissions.py — get_roles, get_doctype_roles, get_all_perms, ALL_USER_ROLE, SYSTEM_USER_ROLE, GUEST_ROLE
frappe/core/doctype/page/page.py — is_permitted, get_custom_allowed_roles
frappe/core/doctype/report/report.py — is_permitted
frappe/core/doctype/custom_role/custom_role.py — get_custom_allowed_roles
frappe/desk/desk_page.py — get, getpage

## rules

MUST call frappe.utils.user.get_users_with_role to list the holders of a role; it joins Has Role to User, drops Administrator and keeps enabled = 1.
MUST name the module when citing get_users_with_role, because frappe/utils/user.py, frappe/core/page/permission_manager/permission_manager.py and frappe/social/doctype/energy_point_settings/energy_point_settings.py each define one and they differ.
NEVER count tabHas Role without a parenttype filter, because nine DocTypes write into it and the unfiltered count adds reports, pages, workspaces, dashboard charts and HTML blocks to the users.
MUST re-count the parents against the installed tree rather than trust a stored list of them, and MUST add a parenttype filter to every query over any istable child table with more than one parent.
MUST name at least one role on every Page record and every Report record, including one meant for everybody, because is_permitted returns True on an empty allowed list.
MUST read an empty roles table in a Page or Report JSON as published to everyone, never as unfinished.
NEVER put a secret, a key or a private query into a Page's script or content, because getpage carries allow_guest=True and returns the document and the assets load_assets attaches to whoever names the page.
MUST expect a Custom Role to replace the Report's own role list and to extend the Page's.
MUST read a role check against All as reachable by a website user too, since get_roles adds ALL_USER_ROLE to every non-Guest user regardless of desk access.
MUST expect get_roles to add SYSTEM_USER_ROLE only when is_system_user(user) is true, so a role rule written against Desk User already excludes every website user.
NEVER expect get_roles to return anything but [GUEST_ROLE] for a Guest or empty user.

## values

Has Role: istable 1, one field, role
parents: user, report, page, custom_role, role_profile, role_permission_for_page_and_report, workspace, dashboard_chart, custom_html_block
Page.is_permitted on an empty list: True
Report.is_permitted on an empty list: True
getpage: whitelisted with allow_guest=True
ALL_USER_ROLE: "All", added to every user who is not Guest, website users included
SYSTEM_USER_ROLE: "Desk User", added only when is_system_user(user)
GUEST_ROLE: "Guest", the only role get_roles returns for Guest or no user
what an anonymous caller receives: the Page document and its assets, not the data the page later fetches

## how

Has Role is one physical table holding several unrelated relationships, so the phrase "who holds this role" is not a query over that table — it is a query over the User parent of that table, and every count taken without parenttype measures a union nobody asked about. get_users_with_role already writes that join; call it before writing SQL.

The empty list is the second trap and it runs the other way from every other check in the framework. Elsewhere an unstated permission withholds. On Page and Report an unstated role list permits, and is_permitted says so in its own docstring. Treat the role list as the only thing standing between a desk page and an anonymous caller, and name a role even when the answer is "everyone" — an explicit All is auditable and an empty table is indistinguishable from work not finished.

Each call the page then makes carries its own check, so what leaks through an unnamed role list is the page and its JS, not the records behind it. That is a smaller hole than it first reads and still the wrong default to ship.
