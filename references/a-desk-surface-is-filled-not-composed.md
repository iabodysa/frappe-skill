# A desk surface is filled, not composed

One call renders the whole surface — head, six action slots, a filter strip, a sidebar column, a
body — and every one of them already exists and is hidden before you write a line. So designing a
Desk screen is choosing which slots to fill and which shipped surface fills them for you; markup
placed anywhere else keeps none of what the slot carries. A surface is one of the eight shipped
Desk screens below, and the framework ships no collective name for them.

The framework enforces a law and only repeats a habit, so a screen departing from a habit still
runs and a screen departing from a law loses what the slot carries.

## Which surface

Pick the surface before the layout. Six of the eight already fill the head for you, and the two that
do not are the two that cost the most to build.

| The surface | You declare | What it carries | What it drops |
|---|---|---|---|
| list view | a DocType, plus a List View Settings row | sidebar, filter strip, saved views, the empty state, bulk actions on a selection | the primary action is `Add <Doctype>` and nothing else, and it is cleared the moment a row is checked |
| report view | the same DocType | the whole list machinery with a DataTable body — columns, totals, inline edit | nothing of the list; it is a rendering of the same rows, not a report |
| query report | a Report record and its `execute` | filters in the page form, a summary, a chart, a footer line | the sidebar entirely, and any primary action unless the report is prepared |
| form | the DocType's own fields | title, docname sub-title, status pill, timeline, doctype actions | the second column when `hide_toolbar` is set; buttons go through `frm.add_custom_button`, never the page |
| workspace | a Workspace record | links, shortcuts, charts, number cards and quick lists on an editor canvas | every action slot in the head — its New and Edit sit in a footer inside the body |
| dashboard | Dashboard and Dashboard Chart records | one Menu holding every action, including the jump to another dashboard | the primary action and the sidebar, and it empties `.page-content`, detaching every page handle |
| desk page | a Page record and the `.js` beside it | exactly what you fill, once you call `frappe.ui.make_app_page` | the breadcrumb, the title, the card and the sidebar — each is a call you did not make |
| dialog | a `fields` array | sections, columns, `reqd` validation, one primary and one secondary | everything needing a route; quick entry only where the DocType is flagged, has a mandatory field and no mandatory child table |

Skipping `make_app_page` and rendering into the raw wrapper is a ninth route, and the setup wizard is
the only screen that takes it. It drops the head, the sidebar toggle, the scroll-shadow, the
skip-to-main link and every keyboard shortcut group. Take it only for a full-screen takeover that
ships its own exit.

## Where a thing goes

The head is six regions in a fixed order and there is no seventh. Everything below is a choice
between a slot and the body.

| What you are placing | Where it goes | law or habit | What that decides |
|---|---|---|---|
| the one commit — Save, Submit, Create | `set_primary_action` | law | one slot per page; a second call replaces the first, so two primaries cannot coexist |
| a backward or destructive step — Cancel, Amend | `set_secondary_action` | habit | an action already taken is shown disabled with a reason, not hidden |
| an operation on checked rows | the Actions dropdown | habit | it appears with the selection and the primary is cleared, so the head reads either create or operate |
| navigation and configuration — Import, Customize, Settings | the Menu | habit | the Menu is reserved for leaving or reconfiguring, never for the task the page exists to do |
| a second, third and fourth command | `add_inner_button` | law | it mirrors itself into the Menu for narrow screens; a button you place in the body gets no mobile path |
| several commands sharing a purpose | the same `group` name on each | law | the group dropdown is created by the name, and the mobile twin is labelled `Group > Label` |
| refresh | `add_action_icon` | habit | an icon with a tooltip, never a labelled button |
| a filter or a parameter | `page.add_field` | law | the strip is prepended to the BODY and stays hidden until a field is added; values come back by fieldname |
| the state of this screen right now | `set_indicator` | law | one pill beside the title, and the label and colour are derived from the document, not chosen |
| standing context about the data | a message line in the body under the filter strip | habit | it survives; it is not the place for the outcome of an action |
| the outcome of a finished action | `frappe.show_alert` | law | it floats over a body-level container, occupies no page space and dismisses itself |
| a yes or no decision | `frappe.confirm` | law | a decision is a dialog with the affirmative primary and the dismissal secondary, never an inline banner |
| nothing to show | a hidden region inside the result area | law | the copy must separate filtered-to-nothing from nothing-exists-yet, and drop the button where the user cannot create |
| the breadcrumb | `frappe.breadcrumbs.add`, called by the surface | law | the page never sets one, so omitting the call leaves the previous screen's bar standing |
| the title | `set_title`, once the data has arrived | habit | it writes the browser tab title too, so a title set at construction flashes a placeholder |
| a sidebar | asked for at construction, then filled with your own markup | law | with `single_column` the node is never created and every later append is discarded in silence |
| a colour, a size, a radius | a semantic custom property | law | dark mode re-points the semantic names only, so a raw ramp step keeps its light value on a dark ground |
| trailing content | `page.main` | habit | the footer node is created hidden and no shipped screen ever fills it |
| anything at all | never the navbar | law | a route change removes every page-added entry from it |

Two shapes are worth copying whole. The smallest honest bespoke page is `make_app_page` with a
title, a few inner buttons, one breadcrumb call, and one rendered template appended to the body. The
largest is the query report: it creates its regions once, appends each to `page.main`, hides all but
one, and thereafter only toggles them — nothing is rebuilt per refresh and nothing is found by class
after creation.

## Settled by

| what it settles | leaf |
|---|---|
| the slots `make_app_page` hands back, and why a head rebuilt on the second visit doubles | `knowledge/desk/app-page.md` |
| the Page record, the sibling files that are the whole wiring, and the style never removed | `knowledge/desk/page.md` |
| the row that caps the columns, and the width that caps them when it is empty | `knowledge/desk/list-view.md` |
| the four branches that answer before a custom indicator runs | `knowledge/ui/list-indicator.md` |
| the order the pill's label and colour are decided in | `knowledge/job/list-indicator-precedence.md` |
| the six values `execute` is unpacked to, and the turn that makes a report prepared | `knowledge/desk/report.md` |
| the links table that is the whole content, and the empty roles table | `knowledge/desk/workspace.md` |
| the shared cache key that ignores the user and the filters | `knowledge/desk/dashboard-chart.md` |
| the field that grants the card against the method that produces the number | `knowledge/desk/number-card.md` |
| where per-DocType client code lands, and what a DocType Layout drops | `knowledge/desk/client-script.md` |
| the markup `frappe.format` returns instead of a value | `knowledge/desk/formatters.md` |
| why a `reqd` Select in a dialog is never empty | `knowledge/desk/select.md` |
| the one screen that takes the no-page route | `knowledge/desk/setup-wizard.md` |
| what the navbar reads, and which dropdown evaluates a condition | `knowledge/desk/navbar.md` |
| why a label must be a literal inside the call | `knowledge/bench/gettext.md` |
| which side of the boundary a Desk string is extracted from | `knowledge/bench/frontend-boundary.md` |
| the route to take when the surface does not belong on the Desk at all | `knowledge/web/page-files.md` |
| which of these surfaces is a record and which is code | `references/the-desk-what-is-metadata-and-what-must-be-code.md` |
