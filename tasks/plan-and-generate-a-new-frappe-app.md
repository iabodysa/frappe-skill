# Task — plan a new Frappe app and generate it

## The app and its modules

Which command already writes the package, and what is left for the plan to write?
MUST let the scaffold command write the package and MUST author only the DocType JSON, the extra modules, the controllers and the filled hooks.
`references/the-commands-that-create-an-app-a-site-and-an-install.md`

Which file decides what the app declares, and where does each declaration live?
MUST name the file that carries each declaration before writing a line into it.
`references/the-files-an-app-is-made-of-and-what-each-one-declares.md`

Which module directories will the sync walk open?
MUST list every module in `modules.txt` and MUST give every module package its `__init__.py`, because a directory the file does not name is never opened and no error is raised.
`knowledge/bench/tree.md`

## Each DocType's shape

Is this DocType ordinary, a single, or a child table?
MUST settle it before the first migration, because the table sync is skipped for a single and a child table's permissions are reset, and neither carries data across afterwards.
`knowledge/bench/standard-json.md`

Is it submittable, and does it post ledger entries?
MUST make it submittable from the first day when it posts ledger entries, because a submitted document never returns to draft.
`knowledge/document/submit.md`

What does the cancel write, and which checks does it skip?
MUST NOT put a rule the cancel has to obey in `validate`, because the cancel save skips that path.
`knowledge/document/cancel.md`

## The name

Which naming route does this DocType take?
MUST declare exactly one route, because the first route that produces a name ends the sequence and every later route is skipped in silence.
`knowledge/document/autoname.md`

Is the prefix free, and what does taking a number cost a concurrent insert?
MUST pick a prefix no shipped app already claims, because one counter row is shared by every writer of that prefix.
`knowledge/document/naming-series.md`

Where must the module and the controller sit for the name to resolve to a class?
MUST place the module and the controller on the derived path before naming anything.
`references/choosing-a-naming-rule-and-keeping-the-tests-off-its-counter.md`

Does the name have to be derived from other fields?
MUST choose the derived form deliberately, because the derivation runs on the insert and not on a later edit.
`knowledge/document/derived-names.md`

## The fields

What is the fieldname of every field?
MUST fix each fieldname in the plan, because a rename in the JSON alone adds an empty column and orphans the old one while the migration exits clean.
`knowledge/document/rename-field.md`

What is the fieldtype of every field?
MUST fix each fieldtype in the plan, because a later change is permitted only inside a small group and editing the JSON bypasses that guard.
`knowledge/document/rename-doc.md`

Which field property does the server actually enforce?
MUST express a rule with a property the server checks rather than one the browser reads.
`knowledge/document/validation.md`

Does a unique index refuse a duplicate on an optional column?
MUST make the column mandatory when uniqueness has to hold.
`knowledge/document/unique-index.md`

Will a default decide what the first insert stores?
MUST set the value in code when the insert-time default is not the wanted value.
`knowledge/document/defaults.md`

## Who may read and change it

Where do the permission rows ship?
MUST ship the rows in the DocType JSON `permissions` array and MUST NOT seed a Custom DocPerm, because one Custom DocPerm row replaces the shipped block whole.
`knowledge/bench/custom-docperm.md`

Which rows does the framework read when it answers a permission question?
MUST design the rows against the reader that consumes them.
`knowledge/permission/docperm.md`

What happens to a role name the site does not have?
MUST declare every role the plan uses, because a missing role is created with desk access and nobody asked for it.
`knowledge/document/role-auto-created.md`

Does a field need to be hidden from a role rather than the whole record?
MUST put the field on a permlevel and give the role a row at that level.
`knowledge/permission/permlevel.md`

Which route is the whole permission decision?
MUST read the route end to end before writing a condition of your own.
`references/permissions.md`

## What the app declares to the framework

Which hook keys does the framework actually read?
MUST spell every key exactly as its reader spells it and MUST write its value as a dotted string, because an unread key is stored and never fires.
`knowledge/bench/hooks.md`

Which records carry code, and what does each one run?
MUST know what a record executes before shipping it with the app.
`references/the-records-that-carry-code-and-what-each-one-runs.md`

## The records that ship with the app

Which records are imported from a module directory, and which are not?
MUST ship a Workflow, a Dashboard Chart, a Number Card and a Kanban Board as a fixture or a patch, because the sync walk never picks them up from a module directory.
`knowledge/bench/fixtures.md`

Why does a shipped record sometimes not land on a site that already ran?
MUST stamp `modified` fresh on every non-DocType record the app ships, because an import skips a record whose stamp is not newer than the row.
`knowledge/bench/standard-json.md`

Which of fixtures, a seed and a migration is the right carrier here?
MUST choose the carrier from what the record has to survive.
`references/fixtures-seed-migrate.md`

What does the plan's post-install record set run through?
MUST create the records through the document API so their own validation runs.
`knowledge/bench/seeds.md`

Which patch runs, and in what order?
MUST order a patch against the schema pass it depends on.
`knowledge/bench/patches.md`

## The first run the app puts in front of a user

Where is an onboarding's progress kept?
MUST expect the first user who finishes a step to retire that onboarding for the whole site, because the progress is written onto the shipped record itself.
`knowledge/desk/module-onboarding.md`

What decides that a step is done?
MUST NOT read a completed step as proof the work happened, because the browser announces the completion and the endpoint that records it carries no role check and no field allowlist.
`knowledge/desk/onboarding-step.md`

Which of the two products in the Form Tour DocType is being written?
MUST set `page_route` for a tour that has to fire on a route, and MUST expect a plain form tour to store no progress at all.
`knowledge/desk/form-tour.md`

Which stylesheet does a shipped Print Style reach?
MUST scope every selector, because the same blob is appended after the standard print sheet for the whole site and injected into the Desk head at boot, and the disabled flag stops neither.
`knowledge/desk/print-style.md`

## Installing and migrating it

What does the install actually do on a site?
MUST know what the install runs before pointing it at a site that already holds data.
`knowledge/bench/install-app.md`

What does the migration delete without raising?
MUST emit `<name>.py` beside every DocType JSON, because a DocType whose controller cannot be imported is removed and the run continues.
`knowledge/bench/migrate.md`

What is the safe order on a site that is already running?
MUST follow the delivery order rather than installing and hoping.
`references/delivering-to-a-site-that-is-already-running.md`

## What the desk shows afterwards

Will the new DocType appear where users look?
MUST add the link to the Workspace child table, because nothing is listed automatically.
`knowledge/desk/workspace.md`

Which parts of the desk are metadata and which must be code?
MUST take the metadata form wherever the desk offers one.
`references/the-desk-what-is-metadata-and-what-must-be-code.md`

Does a browser that already visited run the Desk Page script that was just deployed?
MUST bump the Page record so the eviction walk fires, because with_page serves the page out of `localStorage` and editing the sibling file alone leaves the record's stamp unchanged.
`knowledge/desk/page-cache.md`

## Proving it

How is a test for the generated DocType written and run?
MUST write the test against the framework's own case class and runner.
`references/writing-tests-the-frappe-way.md`

What does the test case give the DocType for free?
MUST use the shipped case rather than building a harness.
`knowledge/bench/case.md`
