# Task — ship a customisation, a record or a schema change to another site

## Which mechanism carries this row

Which of the delivery mechanisms is this row's?
MUST place the row on the graph before writing anything.
`references/fixtures-seed-migrate.md`

Does the value differ per site?
MUST write a seeder for a per-site value, and MUST look for a hook that already declares the record class first.
`knowledge/bench/seeds.md`

Does the delivery have to reach a site that already exists, or one being created?
MUST cover both clocks, because the migrate sequence never reaches a site being installed.
`knowledge/bench/migrate.md`

What has already been recorded when the install hook runs?
MUST make the hook re-runnable, because the app is in the installed list before a single hook has run and nothing wraps the sequence.
`knowledge/bench/install-app.md`

## The change is a field or a property on another app's DocType

Which key of the custom JSON carries the change?
MUST choose among the four keys by their write semantics, and MUST set the sync flag when the customisation has to keep following the file.
`knowledge/bench/custom-json.md`

Why did the exporter write no file?
MUST ship a DocType customised by links alone through another mechanism.
`knowledge/bench/custom-json.md`

What is already declarable rather than written?
MUST name the metadata that carries the change before adding code to it.
`references/the-desk-what-is-metadata-and-what-must-be-code.md`

Why does the app's own JSON stop deciding a property after the site was customised once?
MUST delete the Property Setter row to hand the property back to the app code, because the row is applied over the shipped JSON on every meta load and nothing announces the override.
`knowledge/bench/property-setter.md`

## Permissions are part of what ships

What does one custom permission row do to the shipped block?
MUST ship every role's row together, because one row replaces the whole block and a single Reset click deletes them all.
`knowledge/bench/custom-docperm.md`

Where does a role your app needs come from?
MUST declare the role in a fixture, because the one created on the fly carries desk access.
`knowledge/document/role-auto-created.md`

Can uninstall take the permission rows back?
MUST plan the removal, because the only automatic cleanup is the doctypes carrying a link to the module.
`knowledge/bench/install-app.md`

## The delivery is a fixture

Is this row a constant the app owns?
MUST ship a constant as a fixture and MUST NOT ship anything a site may edit, because the import forces on every migrate.
`knowledge/bench/fixtures.md`

What does the import skip, and what does a mid-list failure leave?
MUST resolve every Link value against what the same install creates, and MUST expect no field default and no advancing series.
`knowledge/bench/fixtures.md`

Which runs first when a fixture and a customisation touch one DocType?
MUST read the fixed sync order of the migrate rather than assume one.
`knowledge/bench/migrate.md`

## The delivery is a one-time data change

Is the patch re-runnable, and what stamps it?
MUST raise out of the patch on a row failure, because a normal return stamps it done forever.
`knowledge/bench/patches.md`

How are rows removed and how is the mutation tried by hand first?
MUST read the force flag as skipping the link check rather than narrowing it, and MUST commit in the console before trusting a manual mutation.
`knowledge/bench/patches.md`, `knowledge/bench/site-commands.md`

## The delivery is standard JSON in a module folder

Which module folders are imported at all?
MUST check the record's folder against the importable list, and MUST ship a dashboard through its own folder rather than that list.
`knowledge/bench/standard-json.md`

What happens on a site that has already touched the record?
MUST expect the skip gate to keep the file out forever, and MUST NOT trust the dashboard sync to overwrite what its own docstring claims.
`knowledge/bench/standard-json.md`

A record written from code at install fails — what then?
MUST verify each record landed, because the writer abandons a failing record and never retries.
`knowledge/bench/standard-json.md`

Is the document already held by another job?
MUST expect a queued-action lock and MUST NOT read a stale one as a live job.
`knowledge/job/lock.md`

## The delivery claims a route or renames a field

Does the shipped DocType take a route a template already answers?
MUST settle the route ownership before shipping either.
`knowledge/web/routing.md`

Is the rename one change or two?
MUST ship the JSON edit and the rename patch together, in that order.
`knowledge/document/rename-doc.md`
