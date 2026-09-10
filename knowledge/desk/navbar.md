---
name: navbar
description: Navbar Settings takes no save-time check on standard rows any more; migrate's sync_standard_items resyncs them from hooks instead, and the help dropdown now evaluates a row's condition while the settings dropdown checks neither condition nor hidden.
triggers: ["NavbarSettings", "sync_standard_items", "get_app_logo", "get_navbar_settings", "NavbarItem", "help_dropdown", "settings_dropdown", "announcement_widget", "app_logo", "is_standard", "hidden", "item_label", "item_type", "route", "action", "condition", "sidebar_header.js", "toolbar.js", "dismissed_announcement_widget", "a deleted standard navbar item came back after migrate", "hide navbar item frappe", "remove help menu item desk", "i deleted a menu entry and it saved but came back later", "why does a removed item from the top menu reappear", "how do i take an entry out of the help menu", "i changed the top menu and nothing changed on screen", "the menu change only appears after i reload everything", "my rule to show a menu entry only to managers is ignored in the settings menu", "the entry shows for everyone even though i wrote a condition for it on a settings row", "my menu entry renders as a plain line instead of a clickable item", "clicking my custom top bar item does nothing", "the wrong logo appears at the top left after installing another app", "we installed a third app and the logo went back to the old one", "the banner at the top is gone for me but colleagues still see it"]
product: frappe
---

# Navbar Settings

## paths

frappe/core/doctype/navbar_settings/navbar_settings.py — NavbarSettings, get_app_logo, get_navbar_settings, sync_standard_items, sync_table
frappe/core/doctype/navbar_settings/navbar_settings.json — app_logo, settings_dropdown, help_dropdown, announcement_widget
frappe/core/doctype/navbar_item/navbar_item.json — item_label, item_type, hidden, is_standard, route, action, condition
frappe/boot.py — get_navbar_settings, get_app_logo
frappe/public/js/frappe/ui/toolbar/toolbar.js — announcement_widget
frappe/public/js/frappe/ui/toolbar/navbar.html — announcement_widget, dismissed_announcement_widget
frappe/public/js/frappe/ui/sidebar/sidebar_header.js — add_navbar_items, get_help_siblings, populate_dropdown_menu

## rules

NEVER expect a save-time check to block deleting a standard navbar row; NavbarSettings carries no `validate` and no `validate_standard_navbar_items` any more, so the Desk form lets a user delete a standard row outright.
MUST run `sync_standard_items` (called from migrate) to reconcile the two child tables against hooks instead: `sync_table` adds any `standard_navbar_items` or `standard_help_items` hook entry missing from the matching table by `item_label`, and then drops every existing row that `is_standard` but whose `item_label` is no longer in that hook list — so a standard row deleted by hand comes back on the next migrate only while its app still declares it, and disappears again once the app stops.
MUST put a row whose visibility depends on the session in `help_dropdown`, not `settings_dropdown`; the desk sidebar's get_help_siblings evaluates `condition` (and `hidden`) for help rows, while add_navbar_items pushes every settings_dropdown row through with NEITHER `hidden` NOR `condition` checked — a hidden or conditional row in settings_dropdown renders unconditionally.
MUST write `condition` as a JavaScript expression that is safe to eval on every sidebar render, because get_help_siblings calls `frappe.utils.eval(element.condition)` inline for every help row.
MUST expect a settings_dropdown row to render regardless of `route` or `action`; add_app_item always renders an anchor and reads `item.icon` or `item.icon_url` for its glyph, so a row naming neither shows as a broken icon rather than as a divider.
MUST expect a help_dropdown row's `action` to run through `frappe.utils.eval(element.action)` on click, so the value must be a JavaScript expression, not a statement block.
MUST expect the whole navbar to come from `frappe.boot`; get_navbar_settings loads the Single into bootinfo, so a navbar change is visible only after the boot is rebuilt.
MUST read the desk logo as a four-step fallback: Website Settings `app_logo`, then Navbar Settings `app_logo`, then the LAST `app_logo_url` hook when exactly two apps declare one, otherwise the first.
NEVER expect a third app's `app_logo_url` to win; get_app_logo takes index 0 and replaces it with index 1 only when the hook list has exactly two entries.
MUST expect the announcement banner to be dismissed per browser; the template hides it once `dismissed_announcement_widget` is in localStorage, and stripping the HTML to an empty string is the only way to remove it for everyone.

## values

dropdowns: help_dropdown and settings_dropdown, both child tables of Navbar Item
row fields: item_label, item_type, hidden, is_standard, route, action, condition
item_type options: Route, Action, Separator
condition evaluated: help_dropdown only, via get_help_siblings
hidden honoured: help_dropdown only, via get_help_siblings; add_navbar_items never reads it for settings_dropdown
render branch: every settings_dropdown row renders as the same anchor row through add_app_item, regardless of item_type, route or action
standard row sync: sync_standard_items, run at migrate, adds a missing hook item and drops a stale is_standard row from each table
logo order: Website Settings app_logo, Navbar Settings app_logo, app_logo_url hook
hook pick: index 1 when the list has two entries, else index 0
announcement dismissal: localStorage key dismissed_announcement_widget

## how

The navbar is one Single document read into the boot, so every change costs a boot rebuild before anyone sees it, and nothing about it is per-user except what `condition` decides at render time in get_help_siblings.

Removal is no longer blocked at save. Deleting a standard row through the Desk form now saves cleanly; what brings a stock row back is the next `bench migrate`, through `sync_standard_items`, which re-adds any `standard_navbar_items` or `standard_help_items` hook entry missing from its table and drops any `is_standard` row whose label an app no longer declares. An app that must remove its own standard row does so by dropping the hook entry, not by editing the table.

The two dropdowns are not symmetric and the asymmetry has flipped from what it was. A help row can carry a `condition` that get_help_siblings evaluates for the viewer, and `hidden` also hides a help row; a settings row's `hidden` and `condition` are both read straight off the boot into add_navbar_items and never checked, so a settings-dropdown row always renders once it exists. A rule such as "show this only to a manager" now has to be expressed as a help-dropdown row, or the settings row has to be removed at the source (hooks or the Navbar Settings table) rather than hidden.

The logo fallback ends in a hook list whose pick is positional. Two apps declaring `app_logo_url` gives the second one the logo; three gives it back to the first. An app that must own the branding sets it on Website Settings or Navbar Settings instead, where the answer does not depend on how many other apps are installed.
