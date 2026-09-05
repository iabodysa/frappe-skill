---
name: select
description: A Select whose options begin with a real value is filled with that value on both the client and the server, so a reqd Select is never empty and MandatoryError never fires.
triggers: ["frappe.ui.form.add_options", "parse_option", "toggle_placeholder", "get_static_default_value", "BaseDocument._validate_selects", "Please check the value of", "select field default value", "empty select field", "the dropdown already has something selected when i open a new record", "why is my required dropdown never showing an error when i leave it alone", "the required dropdown is not blocking save and i am losing my mind", "every record ended up with the same first choice in the status column", "who set all these records to the same value nobody picked it", "why do all my rows show low priority when nobody chose it", "the mandatory check does not fire on the drop down list", "how do i make the drop down start empty", "my test expects the save to be rejected but it saves fine", "records created from code get a value in the choice field i never set", "the placeholder never shows on the dropdown"]
product: frappe
---

# Select

## paths

frappe/public/js/frappe/form/controls/select.js — frappe.ui.form.add_options, parse_option, toggle_placeholder
frappe/model/create_new.py — get_static_default_value
frappe/model/base_document.py — BaseDocument._validate_selects

## rules

MUST begin a Select field's `options` with a blank line wherever the field is `reqd`, because add_options ends by setting selectedIndex to 0 and the first real option is then already chosen.
NEVER expect MandatoryError on a `reqd` Select with no blank first option; the field is never empty for the check to catch.
MUST read the auto-fill as server-side too: get_static_default_value returns `df.options.split("\n", 1)[0]` for a Select, so frappe.new_doc gets the first option with no browser involved.
NEVER rely on _validate_selects to catch it; it only checks that a non-empty value is one of the options and has no opinion on which one arrived.
MUST test the VALUE the document carries after creation, never that creation is refused, because a test asserting refusal passes for the wrong reason.
MUST read `[Select]` and `Loading...` as the two option strings get_static_default_value refuses to fill from.

## values

client fill: add_options sets selectedIndex 0 after appending every option
server fill: get_static_default_value returns the first line of options
skipped option strings: [Select], Loading...
_validate_selects: membership only, and it returns early under in_import and for naming_series
fix: a leading newline in the DocType's options

## how

Two independent places fill the field and they agree, so there is no configuration where the client and the server disagree and expose the problem. The browser sets the selected index after building the list; `frappe.new_doc` reaches the same first option through get_default_value. That is why the defect survives testing: a test that creates a document without setting the field and asserts a refusal passes, and it passes because the field held a value the whole time.

The consequence is a column of documents all carrying the first option — a severity that reads Low everywhere, an approval state nobody chose. Read a suspiciously uniform Select column as this, not as user behaviour.

The fix belongs in the DocType, not in a validation. A leading newline makes the first row blank, the unset document then holds an empty string, and the ordinary mandatory check does the work it was already there to do.
