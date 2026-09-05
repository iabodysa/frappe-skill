---
name: property-setter
description: A Property Setter row is applied over the doctype's shipped JSON on every meta load, so a property one covers can never change again from the app code, and nothing announces the override.
triggers: ["Property Setter", "PropertySetter.autoname", "PropertySetter.validate", "make_property_setter", "delete_property_setter", "bulk_delete_property_setters", "_delete_property_setters", "Meta.apply_property_setters", "Meta.process", "Meta.add_custom_fields", "Meta.add_custom_links_and_actions", "cast", "sbool", "doctype_or_field", "property_type", "row_name", "field_name", "doc_type", "is_system_generated", "reset_customization", "reset_to_defaults", "reset_layout", "CustomizeForm.make_property_setter", "set_property_setters_for_doctype", "set_property_setters_for_docfield", "set_property_setter_for_field_order", "update_order_property_setter", "preserve_naming_series_options_in_property_setter", "set_in_list_view_property", "make_default", "update_naming_series_property_setter", "setup_properties", "add_index", "search_index", "field_order", "links_order", "import_doc", "delete_old_doc", "Field type cannot be changed for", "label change not showing", "field still hidden after update", "customization overrides app", "my change to the doctype json does nothing", "customize form", "property setter", "i changed the field in the code and the screen still shows the old label", "why does my edit to the doctype file do nothing on the form", "the field is still hidden even though i set it visible in the app", "made a field required in code but it is still optional on the form", "the dropdown still shows the old choices after i updated them", "i deployed the change and ran the update and the form did not move at all", "reset to defaults did not remove my customisations", "how do i see every override someone made on one form", "i turned a checkbox setting off and it behaves as if it is on", "changing one field changed the same field on every other form too", "the extra buttons and related links i added stopped appearing after an update", "nothing warns me that a form was customised how do i tell", "the button i added does not appear on the toolbar"]
product: frappe
---

# Property Setter

## paths

frappe/custom/doctype/property_setter/property_setter.py — PropertySetter.autoname, PropertySetter.validate, PropertySetter.on_trash, PropertySetter.on_update, PropertySetter.validate_fieldtype_change, make_property_setter, delete_property_setter, bulk_delete_property_setters, _delete_property_setters, not_allowed_fieldtype_change
frappe/custom/doctype/property_setter/property_setter.json — doctype_or_field, doc_type, field_name, property, property_type, value, row_name, module, is_system_generated
frappe/model/meta.py — Meta.process, Meta.apply_property_setters, Meta.add_custom_fields, Meta.add_custom_links_and_actions, Meta.sort_fields
frappe/utils/data.py — cast, sbool, cint, cstr
frappe/__init__.py — make_property_setter
frappe/custom/doctype/customize_form/customize_form.py — CustomizeForm.make_property_setter, set_property_setters_for_doctype, set_property_setters_for_docfield, set_property_setter_for_field_order, set_property_setters_for_actions_and_links, update_order_property_setter, get_existing_property_value, reset_to_defaults, reset_layout, reset_customization, doctype_properties, docfield_properties
frappe/core/doctype/doctype/doctype.py — DocType.preserve_naming_series_options_in_property_setter
frappe/core/doctype/document_naming_settings/document_naming_settings.py — update_naming_series_property_setter
frappe/desk/doctype/list_view_settings/list_view_settings.py — set_in_list_view_property
frappe/printing/doctype/print_format/print_format.py — make_default
frappe/core/doctype/domain/domain.py — Domain.setup_properties
frappe/database/mariadb/database.py — MariaDBDatabase.add_index
frappe/custom/doctype/custom_field/custom_field.py — CustomField.on_trash
frappe/modules/utils.py — sync_customizations_for_doctype
frappe/modules/import_file.py — import_doc, delete_old_doc

## rules

MUST ask what Property Setter exists on a DocType before reading the app code, whenever a shipped label, `hidden`, `reqd`, `options`, `default` or `fieldtype` change does not appear on screen; apply_property_setters runs on every meta load and writes the stored value over the freshly synced JSON, so the app code being read is innocent.
NEVER read a migrate as restoring a property: `import_doc` deletes and re-inserts the DocType record from the JSON, and the Property Setter rows are untouched, so the JSON is overwritten again on the next `frappe.get_meta`.
NEVER expect a message, a log line or a conflict when a Property Setter masks a shipped change; apply_property_setters sets the attribute and returns.
NEVER treat a Property Setter as authored: one is written without anyone opening Customize Form by saving a DocType that has a `naming_series` field and at least one record, by dragging a column in a list view, by "Set as default print format", by saving Document Naming Settings, by enabling a Domain, and by `db.add_index` on a single field outside install and migrate.
NEVER read "Reset to defaults" as removing the overrides: reset_customization deletes only rows with `is_system_generated` false and skips every `naming_series` row and every `options` row, so exactly the machine-written overrides survive the reset.
MUST pass `property_type` on every call to make_property_setter, because `cast` returns the value unchanged for an empty or unknown fieldtype and the stored value is a string — a `Check` property saved as "0" with no property_type is applied as the truthy string "0", so turning a flag off turns it on.
NEVER call `frappe.make_property_setter` with an args dict that has no `doctype` key: it then queries every DocField with that fieldname and writes one Property Setter for every DocType that has the field.
MUST fill `field_name` on every field-level row, because PropertySetter.validate deletes by the filters that are non-empty — an insert carrying `doc_type` and `property` alone deletes every field-level row for that property on that DocType.
NEVER point `doctype_or_field` at "DocType" for a property that lives on a field; apply_property_setters then sets an attribute nothing reads and raises nothing.
MUST re-create a "DocType Link", "DocType Action" or "DocType State" Property Setter after the app changes that DocType's JSON: those rows match on `row_name`, which is the child row's hash, the shipped JSON carries no name for those rows, and delete_old_doc drops the children — so the loop matches nothing and the override disappears in silence.
MUST list `/app/property-setter` filtered by `doc_type` to see every override on one DocType; Customize Form shows the resulting values and never says which of them came from a Property Setter.
MUST delete the Property Setter row to give a property back to the app; nothing else releases it.
NEVER change `fieldtype` on a `naming_series` field through a Property Setter — validate_fieldtype_change throws `Field type cannot be changed for {0}`.

## values

row identity: `{doc_type}-{field_name or row_name or "main"}-{property}`
doctype_or_field: DocField (matches `field_name`), DocType (sets on the meta), DocType Link / DocType Action / DocType State (match `row_name`)
value column: Small Text — every value is stored as a string
property_type empty or unknown: cast returns the string unchanged
property_type Check: cint(sbool(value)) — "0" and "false" become 0
property_type Int: cint · Float, Currency, Percent: flt · Data, Text, Small Text, Select, Link: cstr
make_property_setter default is_system_generated: True
Customize Form and field_order rows: is_system_generated False
reset_customization deletes: is_system_generated False, field_name != naming_series, property != options
reset_layout deletes: field_order and insert_after only
order in Meta.process: add_custom_fields, apply_property_setters, sort_fields, set_custom_permissions, add_custom_links_and_actions
frappe.make_property_setter with no doctype_or_field: defaults to DocField and derives property_type from the DocField field of that name, else "Data"

## how

A Property Setter is a row in a table, not a patch to a file. Meta loads the DocType from the database, then apply_property_setters reads every row filtered on `doc_type` and writes each stored value over the object. The app's JSON is the input to that overwrite, so once a row exists for a property, that property is frozen at the row's value for the life of the row. A migrate makes this worse rather than better: `import_doc` deletes the old DocType record and inserts the JSON fresh, so the shipped value really does land in the database, and then the next `frappe.get_meta` covers it again.

The diagnosis follows from that, and it runs in the opposite direction to instinct. A field that stays hidden, a label that keeps the old wording, a Select whose options never gain the new value — none of these are bugs in the code that ships them. Ask which Property Setter sits on that DocType first, and only open the app code after the list comes back empty.

Almost nothing about these rows announces itself. `make_property_setter` defaults `is_system_generated` to True, and six ordinary actions call it — saving a DocType that already holds records and has a naming series, reordering list columns, setting a default print format, saving Document Naming Settings, enabling a Domain, adding a single-field index from the console. None of them says a customization was created, and the button labeled reset is precisely the one that keeps them, because reset_customization filters to `is_system_generated` false. So a site nobody customized still carries overrides, and the operator who clicks Reset to defaults and sees no change is looking at the correct behavior.

The typing is the second silent failure. `value` is Small Text, so everything comes back a string, and `cast` is a chain of `elif` that returns the input untouched when the fieldtype is empty or unrecognized. A Check written with no property_type therefore reaches the meta as `"0"`, which is truthy in Python and in the JSON the Desk receives, so the row that was meant to clear `hidden` sets it. Give every row its property_type, and read a row whose effect is the opposite of its value as a missing property_type rather than as a mystery.

Matching is by name for fields and by hash for the child tables, and only the first is stable. `field_name` survives any number of migrates. `row_name` is the `name` of a DocType Link, Action or State row, the shipped JSON carries no name for those rows, and delete_old_doc removes the children before the re-insert, so every such Property Setter is orphaned by the migrate that changes the JSON it referred to. The loop finds no match, breaks nothing and logs nothing.
