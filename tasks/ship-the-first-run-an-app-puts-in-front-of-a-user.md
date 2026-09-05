# Task — ship the first run an app puts in front of a user

## The checklist the user meets first

Where does the progress of an onboarding live?
MUST expect the first user who finishes a step to retire that onboarding for the whole site, because the progress is written onto the shipped record itself and not per user.
`knowledge/desk/module-onboarding.md`

What actually marks a step done?
MUST NOT read a completed step as proof the work happened, because the browser announces the completion through a whitelisted call that carries no role check and no field allowlist.
`knowledge/desk/onboarding-step.md`

Which of the two products in the Form Tour DocType is being shipped?
MUST set `page_route` for a tour that has to fire on a route, and MUST expect a plain form tour to store no progress at all.
`knowledge/desk/form-tour.md`

## The screen the first run sends them to

What does the page object hand back before any button is added?
MUST read every action element as already present and hidden rather than absent, because nothing on the page head is created on demand and nothing is cleared by a route change.
`knowledge/desk/app-page.md`

Does the toolbar survive a second visit to the same route?
MUST clear the toolbar the code owns before rebuilding it, because the duplicate-label check on menu items never matches and a rebuild adds one more copy on every visit.
`knowledge/desk/app-page.md`

## The records the first run relies on

Is a shipped Server Script switched on at all, and what may it do?
MUST set `server_script_enabled` in `common_site_config.json` for the script to run, and MUST write it as restricted Python running as the calling session rather than as elevated Python.
`knowledge/desk/server-script.md`

Is a customisation the first run depends on shipped as a Property Setter?
MUST expect a property a Property Setter row covers never to change from the app code again, because the row is applied over the shipped JSON on every meta load and nothing announces the override.
`knowledge/bench/property-setter.md`

## The first document and the first public page

What does a shipped Print Style reach?
MUST scope every selector, because the blob is appended after the standard print sheet for the whole site and injected into the Desk head at boot, and the disabled flag stops neither.
`knowledge/desk/print-style.md`

Which file does a standard Web Template render?
MUST ship the `.html` file beside the exported JSON and MUST keep the standard check set, because the database `template` field is never rendered and clearing the check deletes the folder from the app.
`knowledge/web/web-template.md`
