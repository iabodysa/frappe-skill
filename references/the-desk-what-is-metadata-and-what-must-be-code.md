# The desk — what a record declares and what only code can do

Every one of these is configured by a RECORD the deployment ships, and code is only ever the
value that has to be COMPUTED. The form is the exception: its connections arrive from a python
module a Custom DocType never loads at all. Every one of them accepts a key it does not read and
drops it without raising, so what you ship is a declaration nothing consumes.

| What you are building | Configured by | The only code it runs | What it drops in silence |
|---|---|---|---|
| list view | `in_list_view` on the DocField, plus one List View Settings row | `<doctype>_list.js` — indicator, extra fields, filters | every `in_list_view` field past the column cap |
| form | the DocType JSON field properties | `<doctype>.js`, and `<doctype>_dashboard.py` for connections | the whole dashboard module on a Custom DocType |
| workspace | the Workspace record and its child tables | none — there is no workspace controller | a DocType or Report no `links` row names |
| dashboard chart | the Dashboard Chart record | a Dashboard Chart Source module, for `chart_type` Custom | nothing declared — the validation is what it drops |
| number card | the Number Card record | a whitelisted method, for `type` Custom | nothing declared — the permission is derived |
| Desk Page | the Page record | the `.js` and `.css` beside its module file | nothing — but the style is never removed from head |
| report | the Report record | `execute`, for a Script Report | four rendered parts, when `execute` returns two values |

A Workspace whose roles table is empty is shown to every logged-in user, and a Workspace shows only
what its own `links` child table names — nothing is discovered.

## Settled by

| what it settles | leaf |
|---|---|
| the links table, and the empty roles table | `knowledge/desk/workspace.md` |
| the sibling files served with no wiring, and the style left in head | `knowledge/desk/page.md` |
| the six values `execute` is unpacked to, and the fifteen-second turn | `knowledge/desk/report.md` |
| why a `reqd` Select never raises MandatoryError | `knowledge/desk/select.md` |
| the markup `frappe.format` returns | `knowledge/desk/formatters.md` |
| no root hidden key, and what `read_only` costs the search | `knowledge/desk/hiding-a-doctype.md` |
| which DocField properties the server enforces | `knowledge/document/validation.md` |
| what `in_create` and `read_only` change and what they do not | `knowledge/permission/docperm.md` |
| the row that sets the column cap, and the width that sets it when empty | `knowledge/desk/list-view.md` |
| the shared cache key that ignores the user and the filters | `knowledge/desk/dashboard-chart.md` |
| the field that grants the card against the method that produces the number | `knowledge/desk/number-card.md` |
| the four branches that answer before a custom indicator runs | `knowledge/ui/list-indicator.md` |
