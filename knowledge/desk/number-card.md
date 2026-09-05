---
name: number-card
description: A Custom Number Card is permitted by read access to its document_type while its number comes from its method, so the field that grants the card is not the field that produces it and validate never requires it.
triggers: ["NumberCard", "has_permission", "get_permission_query_conditions", "get_result", "get_percentage_difference", "calculate_previous_result", "create_number_card", "create_report_number_card", "add_card_to_dashboard", "get_cards_for_user", "get_doctypes_with_read", "get_allowed_report_names", "get_modules_from_all_apps_for_user", "method", "type", "document_type", "parent_document_type", "function", "aggregate_function_based_on", "is_public", "is_standard", "show_percentage_stats", "stats_time_interval", "Method is required to create a number card", "Document Type and Function are required to create a number card", "number card not visible", "custom number card permission", "the card only shows up for me and nobody else can see it", "why can other users not see the dashboard card i made", "i built a card and it is invisible to the whole team this is maddening", "two people see different numbers on the same dashboard card", "why does the same tile show a different total for each user", "the card i created does not appear in the list when i add one to a dashboard", "the percentage change under the number never shows up", "no change since last week is displayed on my tile", "how do i control who is allowed to see a dashboard tile", "a user who should not have access can still read the numbers on my card", "the card saved with no complaint and then broke for everyone else"]
product: frappe
---

# Number Card

## paths

frappe/desk/doctype/number_card/number_card.py — NumberCard, validate, autoname, on_update, has_permission, get_permission_query_conditions, get_result, get_percentage_difference, calculate_previous_result, create_number_card, create_report_number_card, add_card_to_dashboard, get_cards_for_user
frappe/desk/doctype/number_card/number_card.json — type, method, document_type, parent_document_type, function, aggregate_function_based_on, report_name, report_field, is_public, is_standard, show_percentage_stats, stats_time_interval
frappe/permissions.py — get_doctypes_with_read
frappe/boot.py — get_allowed_report_names
frappe/config/__init__.py — get_modules_from_all_apps_for_user
frappe/public/js/frappe/widgets/number_card_widget.js — get_settings, render

## rules

MUST set `document_type` on a Custom Number Card even though nothing computes from it; has_permission grants a Custom card only when `document_type` is in get_doctypes_with_read, so a card left with that field empty is refused to every user who is not Administrator or System Manager.
MUST expect validate to require only `method` for a Custom card, so the card saves clean and the refusal appears later as a card that renders for the author and for nobody else.
MUST read the permission on a Custom card as a claim about a DocType and NOT as a check on the method; the widget calls the method named in `method` directly, and that call is governed by whatever the method itself checks.
MUST put the real access check inside the whitelisted method a Custom card names, because `document_type` decides who sees the card and never decides what the method returns.
MUST expect the list query to refuse a card has_permission would allow: get_permission_query_conditions ALSO requires the card's `module` to be in the user's allowed modules, to be NULL or to be empty, and has_permission never reads `module` at all.
MUST leave `module` empty, or set it to a module the user reaches, because get_cards_for_user applies the same module condition when offering cards for a dashboard.
MUST expect create_number_card to insert with ignore_permissions, so a card can be created through it by a user who cannot create a Number Card.
MUST expect get_cards_for_user to offer only cards the session owns or cards with `is_public` set, so a card shared through a dashboard still needs is_public to be selectable elsewhere.
MUST set `aggregate_function_based_on` whenever `function` is anything but Count, and `parent_document_type` whenever `document_type` is a child table; validate throws on both.
MUST expect get_result to run through frappe.get_list, so a Document Type card is filtered by the reader's own permissions and two users legitimately see two different numbers on the same card.
NEVER read a missing percentage as an error; get_percentage_difference returns nothing when `show_percentage_stats` is unset and returns None when the previous period computed to zero.
MUST set developer_mode to export a card whose `is_standard` is set; on_update calls export_to_files only under that flag.

## values

type values: Document Type, Report, Custom
Document Type card: number from get_result through frappe.get_list, permitted by read on document_type
Report card: number from frappe.desk.query_report.run, permitted by report_name in the allowed reports
Custom card: number from the method named in `method`, permitted by read on document_type
validate requires: Document Type needs document_type and function, Report needs report_name and report_field and function, Custom needs method only
module condition: in the user's allowed modules, or null, or empty
short circuit: Administrator and System Manager return True before any of it
percentage window: Daily, Weekly, Monthly, Yearly, subtracted from now

## how

Three card types share one permission function, and only two of them have a field that means what the function reads. A Document Type card counts rows of `document_type`, so read access to that DocType is the right question. A Report card names a report, so the allowed report list is the right question. A Custom card computes from a whitelisted method, and there is no field that describes what the method touches — so has_permission falls back to `document_type` anyway, a field validate does not require and the number does not use.

That produces the two failures the type is known for. Leave `document_type` empty and the card is correct, saves, renders for its author, and is invisible to everyone below System Manager with no message. Fill it in with a DocType that has nothing to do with the method, and the card is now permitted to exactly the people who can read that unrelated DocType, while the method still runs whatever it runs.

Treat the field as a declaration of audience and put the enforcement in the method. The widget calls the method by name with the card's own arguments; nothing between the click and that call consults a role. A Custom card is therefore only as safe as the check written inside the function it names.
