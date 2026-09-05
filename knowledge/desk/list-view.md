---
name: list-view
description: The list slices its columns to the total_fields on the List View Settings row for the DocType, and with that field empty it slices to 4, 6 or 10 by the browser window width.
triggers: ["ListViewSettings", "total_fields", "fields", "disable_count", "disable_comment_count", "disable_sidebar_stats", "disable_auto_refresh", "disable_automatic_recency_filters", "allow_edit", "save_listview_settings", "set_listview_fields", "set_in_list_view_property", "get_default_listview_fields", "get_list_settings", "set_list_settings", "get_list_view_settings", "setup_columns", "reorder_listview_fields", "in_list_view", "Property Setter", "title_field", "hide_name_column", "status_field", "list view columns missing", "too few columns in list", "the list shows fewer columns on my laptop than on the office screen", "why do two people see a different number of columns in the same list", "i ticked a field to show in the list and it never appears", "my new column shows up for me but not for a colleague", "how do i force the list to always show the same columns everywhere", "the fourth column i added is simply not there on a small screen", "the list keeps reloading by itself every few seconds", "how do i turn off the record count above the list", "the list is slow because it counts everything on every open", "i changed the column order and it snapped back for the first two", "why can i not bulk edit these records from the list", "the list only shows recent records and hides the older ones"]
product: frappe
---

# List view columns

## paths

frappe/desk/doctype/list_view_settings/list_view_settings.py — ListViewSettings, save_listview_settings, set_listview_fields, set_in_list_view_property, get_default_listview_fields
frappe/desk/doctype/list_view_settings/list_view_settings.json — total_fields, fields, disable_count, disable_comment_count, disable_sidebar_stats, disable_auto_refresh, disable_automatic_recency_filters, allow_edit
frappe/desk/listview.py — get_list_settings, set_list_settings
frappe/public/js/frappe/list/base_list.js — get_list_view_settings
frappe/public/js/frappe/list/list_view.js — setup_columns, reorder_listview_fields, refresh_columns, hide_name_column

## rules

MUST set `total_fields` on the DocType's List View Settings row to fix the column count; setup_columns slices the column list to `this.list_view_settings.total_fields` and falls back to a width-derived number only when that value is empty.
MUST expect the fallback to be 4 below a 1366px window, 10 at 1920px and wider, and 6 in between, so the same DocType shows a different number of columns on two machines with no setting changed.
NEVER count the subject and the status indicator out of the cap; they are pushed onto the column list before the in_list_view fields, so raising in_list_view on a fourth field shows nothing on a narrow window.
MUST expect the ID column to be appended AFTER the slice when `title_field` is set and is not `name`, so a list can render one column more than `total_fields` names.
MUST name the List View Settings row after the DocType; both get_list_settings and save_listview_settings address the row by the DocType name, and get_list_settings returns nothing at all when no row exists.
MUST expect an empty settings object on a DocType nobody configured, so every Check on List View Settings reads as unset and the count, the comment count and the sidebar stats all run.
MUST expect save_listview_settings to write a Property Setter on `in_list_view` for every field it adds and every field it removes; the change is a customization of the DocType schema, not a per-view preference.
NEVER expect the status field to be moved out of the list view that way; set_in_list_view_property returns without writing when the fieldname is `status_field`.
MUST expect column ORDER to come from the `fields` Code field and column MEMBERSHIP from `in_list_view`; reorder_listview_fields keeps the first two columns fixed and reorders only what follows.
MUST set `allow_edit` on the List View Settings row to bulk-edit a DocType that has a workflow; without it the workflow blocks the bulk edit and the setting does nothing where no workflow exists.
MUST read a list that will not stop refreshing or counting as this row: disable_auto_refresh, disable_count, disable_comment_count and disable_sidebar_stats each turn off one request, and disable_automatic_recency_filters removes the creation filter the list adds to a large table.

## values

total_fields options: empty, 4, 5, 6, 7, 8, 9, 10
fallback when empty: window width <= 1366 gives 4, >= 1920 gives 10, otherwise 6
columns before the slice: subject, status indicator, then every in_list_view field that is not virtual and not the title field
column appended after the slice: ID, when title_field is set and is not name
settings row name: the DocType name
missing row: get_list_settings returns None and the client uses an empty object
fields Code field: order only
in_list_view: membership, stored as a Property Setter
excluded from the Property Setter write: status_field

## how

Two different things decide what a list shows and they live in two different places. Membership is a DocType customization — `in_list_view` on the DocField, written as a Property Setter by save_listview_settings — so a field added through the list settings dialog changes the DocType for every user. Order is the `fields` Code value on the List View Settings row, applied by reorder_listview_fields, which pins the first two columns and shuffles the rest.

The count is the third thing, and it is the one that surprises. With `total_fields` empty the slice is taken from the window width at render time, so a field that is correctly marked in_list_view and correctly ordered still vanishes on a laptop and appears on a desktop. Nothing is logged, and the DocType is identical on both. Setting `total_fields` is the only way to make the column count a property of the deployment rather than of the screen.

Read the settings row as absent rather than as default. get_list_settings catches DoesNotExistError and returns nothing, so the client's object is empty and every Check on it is falsy — which means the stock behaviour is everything enabled and the width fallback in force. A DocType only becomes deterministic once the row exists.
