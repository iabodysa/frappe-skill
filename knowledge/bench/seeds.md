---
name: seeds
description: A seeder is the only correct mechanism for a value that differs per site, and the framework already declares a hook for some of the record classes apps most often hand-roll one for.
triggers: ["before_install", "add_standard_navbar_items", "standard_navbar_items", "standard_help_items", "sync_standard_items", "sync_table", "execute", "after_install", "setup_demo_data", "clear_demo_data", "Navbar Settings", "an app deleted a standard navbar item and it stayed deleted", "seed data per site", "site specific default record", "i cannot delete the extra menu entry it keeps telling me to hide it instead", "why does it refuse to let me remove an item from the top right menu", "the menu entries came back after i deleted them", "my new site is missing the default rows the other site has", "the record i created in code has empty columns that should have had values", "fields are blank even though the doctype says they have a default", "why is a dropdown field saved as nothing when i never set it", "the sample data reappears every time i run the update", "i wiped the demo records and they came back on their own", "how do i create starting records that are different on each site", "the same value has to be different per customer where do i put it"]
product: frappe
---

# Seeds

## paths

frappe/utils/install.py — before_install, add_standard_navbar_items
frappe/hooks.py — standard_help_items
frappe/core/doctype/navbar_settings/navbar_settings.py — NavbarSettings, sync_standard_items, sync_table
frappe/patches/v13_0/add_standard_navbar_items.py — execute
erpnext/setup/install.py — after_install
erpnext/setup/demo.py — setup_demo_data, clear_demo_data

## rules

MUST look for a hook that already declares the record class before writing a seeder for it. `standard_navbar_items` and `standard_help_items` are declarative hook keys whose entries carry `is_standard` 1, and `add_standard_navbar_items` reads them and writes the rows; frappe itself now declares only `standard_help_items` in its own `hooks.py`, but the `standard_navbar_items` key is still read and still open to any app that declares it.
NEVER expect `is_standard` to protect a row from deletion. `NavbarSettings` carries no `validate` method and no `validate_standard_navbar_items`; an operator who removes a standard item from Navbar Settings and saves simply deletes it, with no error and no message telling them to hide it instead.
MUST expect add_standard_navbar_items to return without changing anything when both settings_dropdown and help_dropdown are already populated, and otherwise to CLEAR both and rebuild them from the hooks of every installed app.
MUST write a seeder for any value that differs per site. frappe, erpnext and hrms declare no fixtures key at all and create their Roles and Single defaults imperatively behind a frappe.db.exists check, so a seeder is not a workaround for a missing feature — it is the mechanism the flagship apps use exclusively.
MUST ship demo data as a generator plus a matching deletion routine, never as fixtures; a fixture re-imports on the next run, so the removal button refills its own screen.
MUST build a seeder with ordinary frappe.get_doc(...).insert(), which reaches _set_defaults and applies the DocType's declared defaults. NEVER set frappe.flags.in_import in a seeder to save import-time overhead; that flag makes _set_defaults return immediately for the whole process, and every field the dict omits is stored NULL with nothing raised unless it is also reqd.
MUST name every field the seeder relies on wherever in_import is deliberately set, because setting it is a decision to take responsibility for every default.
MUST read a Select field carrying a default as the field that flag most often empties; NULL there is not an error, only a value no branch of the interface expects.

## values

declarative record classes: standard_navbar_items (open hook, not declared by frappe itself), standard_help_items (declared in frappe/hooks.py)
is_standard buys: nothing now enforced; NavbarSettings has no validate and a standard item can be deleted like any other
existence check: frappe.db.exists before insert
defaults: applied by _set_defaults on insert, skipped entirely under frappe.flags.in_import

## how

Ask the framework what it calls the concept before writing the record by hand. Some record classes
already have a declarative hook, and using one still saves writing the same rows by hand — `add_standard_navbar_items`
clears and rebuilds both dropdowns from whatever every installed app declares under `standard_navbar_items`
and `standard_help_items`. What it no longer buys is protection: `NavbarSettings` carries no `validate`
override, so nothing stops an operator from deleting a row an app declared as standard. The hooks are
easy to miss, which is why the same seeders keep being reimplemented.

Where no hook exists, a seeder behind a frappe.db.exists check is the right mechanism and not a compromise:
it is what the framework's own apps do for every per-site value. The fixture question and the seeder
question are the same question asked twice — is this a constant the app owns, or a value the site may
set — and the answer picks the mechanism.

The one trap inside a seeder is the import flag. It is set to skip import-time work and it silently
takes the DocType's declared defaults with it, so a document built from a dict stores NULL wherever the
dict was silent. An ordinary insert is the correct shape; set the flag only where the overhead has been
measured and the fields are all stated.
