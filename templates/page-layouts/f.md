# F — Guided Batch

Wizard school. The screen asks one question about a batch and moves it on.

## What it suits

One queue of documents that all sit in the same state and all want the same
decision. The page carries a single question at the top, the batch under it,
and one committing button at the bottom. It suits an approval step in a
workflow, a payment run, a renewal sweep — anything where the operator is not
browsing but answering.

It fits poorly where the operator arrives without knowing what they came for.
A person who wants to look something up has no question to answer here.

## The layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│ STEPPER                                                                  │
│  ○ New ──── ● Ops approval ──── ○ Legal ──── ○ Payment ──── ○ Done       │
├──────────────────────────────────────────┬───────────────────────────────┤
│ BATCH CARD                               │ RAIL                          │
│ ┌──────────────────────────────────────┐ │ ┌───────────────────────────┐ │
│ │ ASK                                  │ │ │ WHAT HAPPENS NEXT         │ │
│ │  Approve these 349 renewals?         │ │ │  · ─────────────────      │ │
│ │  Uncheck anything that should not    │ │ │  · ─────────────────      │ │
│ │  go through.                         │ │ │  · ─────────────────      │ │
│ ├──────────────────────────────────────┤ │ │  · ─────────────────      │ │
│ │ NARROW                               │ │ └───────────────────────────┘ │
│ │  (chip)(chip)(chip)  347 of 349 ✓    │ │ ┌───────────────────────────┐ │
│ ├──────────────────────────────────────┤ │ │ FLAGGED (2)               │ │
│ │ BATCH                                │ │ │ ┌───────────────────────┐ │ │
│ │  ☑ ◉ ────── ─────────── ▭  ▭         │ │ │ │ ───────────────────   │ │ │
│ │  ☑ ◉ ────── ─────────── ▭  ▭         │ │ │ │ ──────────            │ │ │
│ │  ☑ ◉ ────── ─────────── ▭  ▭         │ │ │ └───────────────────────┘ │ │
│ │  ☑ ◉ ────── ─────────── ▭  ▭         │ │ │ ┌───────────────────────┐ │ │
│ │  ☐ ◉ ────── ─────────── ▭  ▭  <flag  │ │ │ │ ───────────────────   │ │ │
│ │  ☑ ◉ ────── ─────────── ▭  ▭         │ │ │ │ ──────────            │ │ │
│ │  ☑ ◉ ────── ─────────── ▭  ▭         │ │ │ └───────────────────────┘ │ │
│ │  ☑ ◉ ────── ─────────── ▭  ▭         │ │ └───────────────────────────┘ │
│ │  ☑ ◉ ────── ─────────── ▭  ▭         │ │ ┌───────────────────────────┐ │
│ │  ☑ ◉ ────── ─────────── ▭  ▭         │ │ │ QUEUE AFTER THIS STEP     │ │
│ │  ☑ ◉ ────── ─────────── ▭  ▭         │ │ │  Legal   ············   9 │ │
│ │  (scrolls)                           │ │ │  Payment ·········  6,628 │ │
│ ├──────────────────────────────────────┤ │ │  Renewal ············   7 │ │
│ │ COMMIT                               │ │ └───────────────────────────┘ │
│ │  [Back]        [Reject 2] [Approve   │ │                               │
│ │                 347 and continue]    │ │                               │
│ └──────────────────────────────────────┘ │                               │
└──────────────────────────────────────────┴───────────────────────────────┘
```

## The regions

**STEPPER** — a full-width band across the top, outside the cards. Six dots
joined by rules that stretch to fill. One dot is filled and its label is dark;
the rest are hollow and grey. It names the pipeline the batch is travelling and
marks the station the operator is standing at. It carries no controls.

**BATCH CARD** — the growing column. It holds four stacked bands:

- **ASK** — the question in the largest type on the page, and one line under it
  telling the operator what their hands are for. The count lives inside the
  question sentence, not in a separate badge.
- **NARROW** — three pill filters and, pushed to the far end by a spacer, a live
  count of how many of the batch are still checked.
- **BATCH** — the rows. Each row is a checkbox, an avatar, a primary label, a
  filler field that takes the slack, a status pill and a trailing chip. Rows
  alternate two near-identical surface tints. An unchecked row shows a darker
  trailing chip, which is how the flagged pair is spotted in place.
- **COMMIT** — a bar tinted apart from the rows, holding a quiet back button at
  the near edge, a spacer, and at the far edge a quiet reject button beside the
  one dark filled button. The filled button restates the count it is about to
  act on.

**RAIL** — a fixed 300-wide column of three separate cards that never grows.
*What happens next* previews the consequence in four short lines. *Flagged* pulls
the exceptions out of the batch so the operator does not have to hunt for them.
*Queue after this step* shows the sizes of the stations still downstream.

## What it does well

The page has one job and says it in one sentence. An operator who reads only
the ASK band and the filled button knows the whole transaction.

Every number on the screen is the same number seen from a different angle —
349 asked, 347 checked, 2 flagged, 347 approved, 2 rejected. The rail's
*Flagged* card and the batch's unchecked rows are the same two documents. That
redundancy is what lets a person commit 347 records without reading 347 rows.

The commit bar states its count. A button reading *Approve 347 and continue*
cannot be pressed by accident against the wrong batch.

The rail is advisory in full. Nothing in it takes a click that changes data, so
it can be dropped on a narrow screen without removing a capability.

## What it costs

It handles one question at a time. An operator holding two unrelated decisions
pays a full page transition between them.

The batch column scrolls while the commit bar stays. A very long batch means the
ASK band scrolls away, and with it the sentence the button depends on. Keeping
the ASK band pinned, or repeating the count in the button as this sketch does,
is what saves it.

The stepper is decoration until the operator can click it. If the stations are
not navigable the band spends 56 pixels of height on a label.

The trailing chip is the only thing separating a flagged row from an approved
one at a glance, and the difference between its two tints is small. A colour or
an icon carries that difference further than a tint step does.

The page assumes the batch is homogeneous. Where the rows want different
decisions the checkbox is too blunt an instrument and the layout stops helping.

## Right to left

Frappe stamps the direction on the root element and swaps the whole stylesheet
bundle, so the mirroring is a build concern rather than a per-component one —
`frappe/www/app.py:62` computes `layout_direction`, `frappe/www/app.html:2`
writes it into `dir`, and `frappe/utils/jinja_globals.py:134` swaps a
`rtl_`-prefixed CSS bundle in its place.

Mirrors:

- The stepper reverses. *New* takes the right edge and *Done* the left, and the
  connecting rules run right to left.
- The batch card and the rail swap sides — rail on the left, batch on the right.
- Every row's internal order reverses: checkbox at the right edge, trailing chip
  at the left.
- The commit bar reverses. *Back* sits at the right edge; the filled button lands
  at the far left.
- Each rail row's label-dots-value pattern reverses, so the value sits at the
  left.

Does not mirror:

- The digits themselves. 349 stays 349 whichever way the line runs, and Arabic
  reads a number left to right inside a right-to-left sentence. A count set on
  the same line as Arabic words is the one place the terminal and the browser
  disagree about order.
- Vertical order. The stepper stays above, the commit bar stays below.
- The rail's card order, top to bottom.
- Icon glyphs that are not directional. A chevron pointing forward wants
  flipping; a person glyph does not.

## The Frappe surface it maps onto

**The two-column split is the Desk page's own grid.** `Page` builds a row
holding a `col-lg-2 layout-side-section` and a `layout-main-section` beside it
(`frappe/public/js/frappe/ui/page.js:100-106`), and hands the sidebar back as
`this.sidebar` (`frappe/public/js/frappe/ui/page.js:125`). The rail lands there;
the batch card lands in the main section. The sketch's rail is wider than
`col-lg-2` allows, so the split is the one place the sketch asks for a custom
page rather than the stock list.

**The checkbox column and the count are stock list behaviour.** The list view
draws a `.list-row-checkbox` per row and wires the header checkbox to toggle all
of them (`frappe/public/js/frappe/list/list_view.js:1375-1398`), and reads the
selection back with `get_checked_items`
(`frappe/public/js/frappe/list/list_view.js:1643`). Whenever the selection is
non-empty the page swaps its primary action for the actions menu
(`frappe/public/js/frappe/list/list_view.js:590-598`) — the sketch's commit bar
takes the opposite position, keeping the primary button visible and letting its
label carry the count.

**The commit button is a workflow transition applied in bulk.** Where the
doctype has a workflow, the list view builds one menu entry per available
transition (`frappe/public/js/frappe/model/workflow.js:91`,
`frappe/public/js/frappe/list/list_view.js:1802-1828`) and calls
`frappe.model.workflow.bulk_workflow_approval` with the checked names
(`frappe/public/js/frappe/list/list_view.js:1815`).

**The batch size decides whether the click blocks.** `bulk_workflow_approval`
runs the loop inline below 20 documents, enqueues it on the `short` queue
between 20 and 500, and throws above 500
(`frappe/model/workflow.py:238-253`). A batch of 349 lands in the middle band,
so the sketch's *Approve 347 and continue* returns before the work finishes and
the operator watches a progress bar rather than a result.

**That progress bar is real.** `_bulk_workflow_action` calls `show_progress` per
document (`frappe/model/workflow.py:265`), which publishes a percentage once the
batch reaches five (`frappe/model/workflow.py:356-359`) through
`frappe.publish_progress` (`frappe/realtime.py:12`). The rail's *What happens
next* card is the natural home for it.

**The stepper is the workflow's own state list.** A Workflow document carries a
`states` table and a `transitions` table
(`frappe/workflow/doctype/workflow/workflow.json:16-19`), which is enough to
draw the six dots and to know which one is filled.

**A non-workflow batch has a different door.** For plain field edits across a
selection, `BulkOperations` exposes `edit`, `submit_or_cancel`, `delete`,
`assign` and `add_tags` (`frappe/public/js/frappe/list/bulk_operations.js:310`,
`:275`, `:195`, `:225`, `:425`). The commit bar maps onto whichever of those the
step actually is.
