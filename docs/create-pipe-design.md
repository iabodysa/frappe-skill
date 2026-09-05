# The `create` pipe — the design three source readings settled

`create` generates a Frappe app from a PLAN the operator fills in first. It refuses to generate
until every irreversible decision in that plan is answered, because those decisions cannot be
changed once the app holds data.

## What already exists, and what `create` must not rebuild

`bench new-app` writes the package scaffold: module directory, `templates`, `www`, `config`,
`public`, `patches`, `__init__.py`, `pyproject.toml`, `license.txt`, `modules.txt` with ONE line,
`hooks.py` with `doc_events`, `scheduler_events`, `required_apps` and `add_to_apps_screen` all
commented out, `patches.txt`, and the editor and lint files. It reaches this through
`bench/commands/make.py` `new_app`, `frappe/commands/utils.py` `make_app` and
`frappe/utils/boilerplate.py` `_create_app_boilerplate`, which takes a hooks dict and can be called
without prompting.

The Desk writes a DocType's own files only on a live site with `developer_mode` on:
`frappe/core/doctype/doctype/doctype.py` `on_update` calls `export_doc`, which reaches
`frappe/modules/export_file.py` `write_document_file` for the JSON, and `make_controller_template`
reaches `frappe/modules/utils.py` `make_boilerplate` for `<name>.py`, `test_<name>.py` and
`<name>.js`. `make_module_and_roles` inserts the `Module Def` and any missing `Role` as database
records, never as files.

`create` therefore calls `_create_app_boilerplate` for the scaffold and writes only what nothing
else writes: DocType JSON authored from a plan, extra modules, controllers and tests beside offline
JSON, a filled `hooks.py`, the `fixtures` hook and its JSON, and workspace and card metadata.

It calls rather than duplicates: `ctlkit.config` `discover_config` for the root, `schema_peek` for
validating a plan's links and selects, `seed_kit` for post-install records with its dry run,
`stamp` for the `modified` field, and `benchx` for anything that touches a site.

## The eight failures the generator must design out

`frappe/model/sync.py` `sync_for` walks `modules.txt` alone, so a module directory missing from that
file is never opened and no error is raised. The module package needs its `__init__.py` or the walk
raises an import error instead.

`frappe/model/sync.py` `remove_orphan_doctypes` deletes a DocType whose controller cannot be
imported, printing and continuing. A DocType JSON shipped without its `<name>.py` beside it is
therefore removed on the next migration.

`frappe/database/schema.py` `get_column_definitions` skips a field whose fieldname is one of the
framework's own columns, and the import path sets `ignore_validate`, so
`frappe/core/doctype/doctype/doctype.py` `scrub_field_names` and `check_invalid_fieldnames` never
run over a generated file. The generator must refuse those names itself.

`frappe/core/doctype/doctype/doctype.py` `validate_series` is a Desk path, skipped during sync, so a
`naming_series` prefix already carrying a `tabSeries` row silently shares that counter.

Custom DocPerm replaces the shipped permission block whole once any row exists, so a generated app
carries its permissions in the DocType JSON `permissions` array and never seeds Custom DocPerm. A
role name that does not exist is auto-created with desk access, so role names are validated against
the plan and the site.

`check_link_table_options` returns early under patch mode and links are ignored during import, so a
link to a DocType that does not exist yet passes sync in silence and fails on the next Desk save.
Ordering still has to be right because seeded records do validate their links.

`frappe/modules/import_file.py` `import_file_by_path` skips a non-DocType record whose `modified`
stamp is not newer than the row in the database, so every non-DocType record the pipe writes carries
a fresh UTC stamp.

`_load_app_hooks` stores whatever it is given and `insert_single_event` skips a scheduler entry it
cannot import with a coloured message only, so hook keys are spelled exactly as their reader spells
them and their values are dotted strings.

Workflow, Dashboard Chart, Number Card and Kanban are not in `IMPORTABLE_DOCTYPES`, so
`frappe/model/sync.py` `get_doc_files` never picks them up from a module directory; they ship as a
patch or a fixture.

## The order the pipe writes in

`modules.txt` and the module packages, then the DocType directories with child tables and linked
masters before whatever depends on them, then `hooks.py`, then workspace and report JSON, then the
seed records as patches.

A DocType directory carries `<name>_list.js` beside the JSON, the controller and the test, because
`frappe/desk/form/meta.py` `add_code` loads that file into `__list_js` and
`frappe/core/doctype/doctype/doctype.py` leaves its `make_boilerplate("controller_list.js")` call
commented out, so nothing else writes it. The workspace, the onboarding steps, the module
onboarding and the form tours follow `hooks.py`, in the order `IMPORTABLE_DOCTYPES` walks them.

## The irreversible half of the plan

These are asked first and the pipe refuses to generate while any is unanswered.

- The app name and the module list. `frappe/model/base_document.py` `import_controller` loads a
  controller from the module value, and `patches.txt` carries import paths forever.
- Single, child table, or ordinary, per DocType. `updatedb` skips the table sync for a single and
  `set_defaults_for_single_and_table` wipes the permissions of a child table, and neither change
  migrates data across afterwards.
- Submittable, and whether it posts ledger entries. `check_docstatus_transition` never allows a
  submitted document back to draft, and `make_reverse_gl_entries` cancels by writing reversal rows
  rather than deleting, so a ledger posting forces submittable from the first day.
- The naming route, and inside it the autoincrement decision.
  `validate_autoincrement_autoname` refuses the change once the table holds a row, and
  `set_defaults_for_autoincremented` forces `allow_rename` off.
- The fieldname of every field. `frappe/model/utils/rename_field.py` `rename_field` is the only
  route that carries data across, and a rename in the JSON alone adds an empty column and leaves the
  old one orphaned while the migration exits clean.
- The fieldtype of every field. `validate_fieldtype_change` permits a change only inside the small
  groups in `ALLOWED_FIELDTYPE_CHANGE`, and editing the JSON bypasses that guard.
- The name of every first-run record, and whether there is a `Module Onboarding` at all.
  `frappe/desk/desktop.py` reads `onboarding_name` out of the `Workspace` `content` blob and
  `Module Onboarding.steps` cites each `Onboarding Step` by name, while `Form Tour` autonames from
  `field:title`. `remove_orphan_doctypes` covers DocTypes alone, so a renamed record imports as a
  second row and the first one stays live and reachable.

## The reversible half

Labels, list-view flags, title and search fields, permission rows, the unique flag, `track_changes`,
`allow_rename` outside autoincrement, and the `naming_series` option list, which affects new
documents only. `is_tree` sits between the two: `add_nestedset_fields` and `rebuild_tree` can
backfill the tree columns, but only through a patch.

## Surfaces

`create plan` writes the plan template. `create ask` prints the questions in the order above, the
hardest to reverse first, and it asks the first-run path — the workspace, the onboarding or an
explicit `none`, the steps, and which DocTypes name a form tour — rather than leaving an author to
already know the shape. `create check` grades a filled plan and names every unanswered
irreversible decision, every reserved fieldname, every link with no target and every misspelled hook
key. `create app` generates, and it refuses while `check` is red.
