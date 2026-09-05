---
name: custom-json
description: A module's custom JSON carries four keys with four different write semantics, it is applied on every migrate only when sync_on_migrate is truthy, and the exporter writes no file for a doctype customized by links alone.
triggers: ["sync_customizations", "sync_customizations_for_doctype", "export_customizations", "create_custom_fields", "create_custom_field", "get_existing_custom_fields", "PropertySetter.autoname", "PropertySetter.validate", "delete_property_setter", "db_insert", "db_update", "add_custom_links_and_actions", "set_custom_permissions", "Custom Field", "Property Setter", "Only allowed to export customizations in developer mode", "Label is mandatory", "Fieldname not set for Custom Field", "module customize json", "property setter and custom field file", "i edited the customization file and nothing changed on the site after an update", "why does my customization only apply on a fresh install and never again", "my saved customizations are not applied when the site is updated", "the connections tab is empty even though the file lists them", "the related documents section shows nothing although i added them", "why do my links never show up on the form", "i exported the customizations and no file was written and no error appeared", "the export said it worked but there is nothing on disk", "importing the customization wiped a setting another team had made", "a change someone else made on the same field was overwritten by my file", "how do i ship a field change without losing what others changed on that field"]
product: frappe
---

# Custom JSON

## paths

frappe/modules/utils.py — sync_customizations, sync_customizations_for_doctype, export_customizations
frappe/custom/doctype/custom_field/custom_field.py — create_custom_fields, create_custom_field, get_existing_custom_fields
frappe/custom/doctype/property_setter/property_setter.py — PropertySetter.autoname, PropertySetter.validate, delete_property_setter
frappe/model/base_document.py — db_insert, db_update
frappe/model/meta.py — add_custom_links_and_actions, set_custom_permissions

## rules

MUST set sync_on_migrate to 1 for a customization that has to stay live. sync_customizations applies the file when that key is truthy or when the run is an install, and there is no third branch — absent or 0 means the file is applied once at install-app and never again, with no error and no log line, so editing it later reaches no existing site.
MUST read the four keys as four different write semantics. Custom Field and DocType Link look up an existing row and update it in place with validation disabled; Property Setter inserts through the ORM and its controller replaces only the property it names; Custom DocPerm runs an unfiltered delete of every row for the doctype and reinserts the file's rows.
MUST give every links row a parent key naming the DocType it hangs off. Without it the sync's doctype list becomes [None], the lookup filter compiles to parent IS NULL and matches nothing, and db_insert writes the row with parent, parentfield and parenttype all NULL — add_custom_links_and_actions filters on parent and custom, so the link never renders, nothing is logged, and the orphan is rewritten on every run.
MUST set custom to 1 on every links row a custom JSON ships. add_custom_links_and_actions filters on parent and custom together, so a row written without it is stored and never appended to the meta.
MUST read an empty Connections tab on a doctype whose custom JSON plainly declares links as that missing key; adding it makes them all appear at once.
MUST hand-check a links-only export. export_customizations builds custom_fields, property_setters, custom_perms and links and then writes the file only when one of the FIRST THREE is non-empty, so a doctype customized only by links falls through to an implicit return and the operator sees success with nothing on disk.
MUST use create_custom_fields where a delivery has to preserve properties the app does not care about. It is the only property-level merge in the framework: it loads the existing Custom Field, applies only the keys the caller passed, and saves only when the result differs, so an unmentioned property keeps the operator's value and an unchanged field costs no write.
NEVER expect that of the JSON route; it writes every key in the file over the current value with validation disabled and a direct database update, comparing no hash and no timestamp.
MUST read a Property Setter's delete as scoped and intended. Its name is computed from the doctype, the field or row it targets and the property, so validate deletes the predecessor for that exact key when the document is new and the operator loses one property's value, never a block.
MUST expect sync_customizations to skip a file whose doctype does not exist, printing `DocType {0} does not exist.` and continuing.
MUST expect a child table's rows to be synced from the parent's file only when no separate JSON exists for that child in the same folder.

## values

four keys: custom_fields, property_setters, custom_perms, links
condition: sync_on_migrate truthy, or frappe.flags.in_install with an app named
Custom Field lookup: dt plus fieldname
DocType Link lookup: parent plus link_doctype plus link_fieldname
Property Setter name: <doc_type>-<field_name or row_name or main>-<property>
export condition: custom_fields or property_setters or custom_perms non-empty
export requires: developer_mode

## how

Read one file as four mechanisms, one per key. Three of them are additive and one wipes a whole
table, and a diff of the file shows no difference between them — so a single customization can carry a
harmless change and a destructive one in the same commit. Decide per key, not per file.

sync_on_migrate is a checkbox pressed months ago that decides whether the file is live or frozen, and
nothing in the file's diff tells you which. Read the key before assuming an edit will land anywhere.

The exporter's write condition is where hand-written files come from, and hand-written files are where the missing
parent key comes from: the two defects are one chain. When a customization must be written by hand,
compare it against a file the exporter did produce, because the keys the exporter always emits are
exactly the ones the sync silently needs.
