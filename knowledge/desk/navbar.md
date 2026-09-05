---
name: navbar
description: Navbar Settings refuses to save when the count of standard rows drops, and only the settings dropdown evaluates a row's condition while the help dropdown reads hidden alone.
triggers: ["NavbarSettings", "validate_standard_navbar_items", "get_app_logo", "get_navbar_settings", "NavbarItem", "help_dropdown", "settings_dropdown", "announcement_widget", "app_logo", "is_standard", "hidden", "item_label", "item_type", "route", "action", "condition", "navbar.html", "toolbar.js", "dismissed_announcement_widget", "Please hide the standard navbar items instead of deleting them", "hide navbar item frappe", "remove help menu item desk", "it refuses to save when i delete a menu entry from the top bar", "why can i not remove an item from the top menu", "how do i take an entry out of the help menu", "i changed the top menu and nothing changed on screen", "the menu change only appears after i reload everything", "my rule to show a menu entry only to managers is ignored in the help menu", "the entry shows for everyone even though i wrote a condition for it", "my menu entry renders as a plain line instead of a clickable item", "clicking my custom top bar item does nothing", "the wrong logo appears at the top left after installing another app", "we installed a third app and the logo went back to the old one", "the banner at the top is gone for me but colleagues still see it"]
product: frappe
---

# Navbar Settings

## paths

frappe/core/doctype/navbar_settings/navbar_settings.py — NavbarSettings, validate, validate_standard_navbar_items, get_app_logo, get_navbar_settings
frappe/core/doctype/navbar_settings/navbar_settings.json — app_logo, settings_dropdown, help_dropdown, announcement_widget
frappe/core/doctype/navbar_item/navbar_item.json — item_label, item_type, hidden, is_standard, route, action, condition
frappe/boot.py — get_navbar_settings, get_app_logo
frappe/public/js/frappe/ui/toolbar/toolbar.js — navbar_settings, announcement_widget
frappe/public/js/frappe/ui/toolbar/navbar.html — help_dropdown, settings_dropdown, announcement_widget, dismissed_announcement_widget

## rules

MUST set `hidden` on a standard navbar row instead of deleting it; validate_standard_navbar_items counts the rows carrying `is_standard` before and after the save and throws "Please hide the standard navbar items instead of deleting them" when the count fell.
MUST expect that check to compare COUNTS and not identities, so deleting one standard row while adding another standard row passes it.
MUST expect the check to be skipped under a patch, because it runs only when `frappe.flags.in_patch` is false.
MUST put a row whose visibility depends on the session in `settings_dropdown`; the template evaluates `condition` for that dropdown only, and renders a `help_dropdown` row on `hidden` alone.
MUST write `condition` as a JavaScript expression that is safe to eval on every navbar render, because the template evaluates it inline for every settings row.
MUST expect a row with neither `route` nor `action` to render as a divider, whatever `item_type` says.
MUST expect `action` to be inlined into an onclick attribute after a `return`, so the value must be a JavaScript expression and not a statement block.
MUST expect the whole navbar to come from `frappe.boot`; get_navbar_settings loads the Single into bootinfo, so a navbar change is visible only after the boot is rebuilt.
MUST read the desk logo as a four-step fallback: Website Settings `app_logo`, then Navbar Settings `app_logo`, then the LAST `app_logo_url` hook when exactly two apps declare one, otherwise the first.
NEVER expect a third app's `app_logo_url` to win; get_app_logo takes index 0 and replaces it with index 1 only when the hook list has exactly two entries.
MUST expect the announcement banner to be dismissed per browser; the template hides it once `dismissed_announcement_widget` is in localStorage, and stripping the HTML to an empty string is the only way to remove it for everyone.

## values

dropdowns: help_dropdown and settings_dropdown, both child tables of Navbar Item
row fields: item_label, item_type, hidden, is_standard, route, action, condition
item_type options: Route, Action, Separator
condition evaluated: settings_dropdown only
hidden honoured: both dropdowns
render branch: route gives an anchor, else action gives a button, else a divider
standard row count: may rise, may not fall, unless in_patch
logo order: Website Settings app_logo, Navbar Settings app_logo, app_logo_url hook
hook pick: index 1 when the list has two entries, else index 0
announcement dismissal: localStorage key dismissed_announcement_widget

## how

The navbar is one Single document read into the boot, so every change costs a boot rebuild before anyone sees it, and nothing about it is per-user except what `condition` decides at render time.

Removal is deliberately blocked. The validator counts standard rows and refuses a save that lowers the number, which makes `hidden` the supported way to take a stock entry out of the menu. The count is the whole test, so it neither notices which row went nor protects a specific entry — and it is bypassed entirely inside a patch, which is how the framework moves its own rows.

The two dropdowns are not symmetric and the asymmetry is the thing to remember. A settings row can carry a `condition` that is evaluated for the viewer; a help row cannot, so the only field there is `hidden`, which is global. A rule such as "show this only to a manager" therefore has to be expressed as a settings-dropdown row, or the entry has to be hidden for everyone.

The logo fallback ends in a hook list whose pick is positional. Two apps declaring `app_logo_url` gives the second one the logo; three gives it back to the first. An app that must own the branding sets it on Website Settings or Navbar Settings instead, where the answer does not depend on how many other apps are installed.
