# C — Triage Inbox

Mail school. One record at a time, decide, next. Built for clearing a queue.

Suits a page whose job is a pile that shrinks: renewals waiting on a decision,
requests waiting on approval, exceptions waiting on a human. It suits a reader
who opens the page with a backlog and closes it with a smaller one. It suits
work where the decision is short and the reading is short. It suits a page
poorly when the reader compares records against each other, edits many fields
per record, or arrives to answer one question about the whole set.

## The layout

```
┌──────────────┬───────────────────────┬───────────────────────────────────┐
│ VISAS        │  search               │  title                            │
│              │───────────────────────│  chip  chip  chip                 │
│ o My queue   │  subject        (tag) │───────────────────────────────────│
│ o New        │  line two             │  label        label               │
│ o Legal      │───────────────────────│  value        value               │
│ o Awaiting.. │  subject        (tag) │  label        label               │
│ o Blocked    │  line two             │  value        value               │
│ o Renewed    │───────────────────────│                                   │
│ o Rejected   │  subject        (tag) │───────────────────────────────────│
│              │  line two             │  History                          │
│              │───────────────────────│  o  ──────────────────────────    │
│              │  subject        (tag) │  o  ──────────────────────────    │
│              │  line two             │───────────────────────────────────│
│              │                       │ [Approve] Schedule SADAD Reject   │
│              │                       │                      J / K  next  │
└──────────────┴───────────────────────┴───────────────────────────────────┘
  210 px          340 px                  fills the remaining width
```

Three columns, full height, no top bar. The two left columns are fixed; the
third takes whatever is left. At 1280 the third column is 730.

## The regions

**Rail (210 wide, fixed).** The app name, then the named queues, one per row.
Each row is a dot, a label, a leader line that stretches, and a count pinned to
the far end. One row is selected and carries a filled background; the rest sit
flat on the rail. The rail scrolls on its own when the queues outgrow it. Nine
queues fit the sketch's height without scrolling.

**List (340 wide, fixed).** A search field in its own header band, then the
records of the selected queue, one row each. A row is a short accent bar, two
stacked lines — a strong first line and a weaker second — and a status pill at
the far end. The selected row darkens and its accent bar darkens with it. The
list scrolls; the rail and the record do not scroll with it.

**Record (fills, min ~640).** Four stacked bands, each with the same side
padding:

- *Header.* The record's title, then a row of small chips for the facts a
  reader checks before deciding — status, owner, date.
- *Fields.* Two columns of label-over-value pairs, five rows deep. The two
  columns are equal and both stretch. This band carries only the fields that
  bear on the decision.
- *History.* A quieter background, a small heading, and one line per event with
  a dot marker. Three lines deep in the sketch.
- *Actions.* Separated by a hairline. One filled primary button, then the
  alternatives as light buttons, then a stretching gap, then the keyboard hint
  at the far end.

## What it does well

- The pile is honest. The count sits beside the queue name, so the size of the
  work is visible before the work starts.
- The decision lives in one place. The buttons never move between records, so
  the hand learns one target.
- Reading and deciding share a screen. No route change per record, so the list
  keeps its scroll position and the reader keeps their place.
- It rewards a keyboard. Next record, then a decision, without a pointer.
- Little chrome. The record's own fields carry the page, so a dense Arabic
  record still reads.

## What it costs

- It needs width. Three columns eat 550 before the record starts. Below roughly
  1100 the record pane drops under a comfortable reading width.
- One record at a time hides comparison. A question that spans two records costs
  a second trip through the list.
- The rail grows with the number of named queues, and a long rail turns the
  cheapest navigation in the page into a scroll.
- In the sketch the action bar sits under the content, not pinned to the bottom
  edge of the pane, so a short record leaves it floating mid-screen and a long
  record pushes it below the fold. Pinning it is a decision this sketch leaves
  open.
- The sketch draws placeholder bars, not text, so it decides nothing about
  truncation, wrapping, or how a long Arabic subject behaves inside a 246-wide
  row.
- Each counted queue in the rail is one aggregate query. A rail of many counts
  is a rail of many round trips.

## Right to left

What mirrors:

- The column order. The rail moves to the right edge, the list beside it, the
  record on the left.
- Inside a rail row: the dot leads on the right, the count pins to the left, the
  leader line still stretches between them.
- The list row's accent bar moves to the right edge of the row; the status pill
  moves to the left end.
- The two field columns swap, and the reading order inside the band runs
  right to left.
- The history dot leads on the right and its bar stretches leftward.
- The action bar reverses: the primary button sits at the right, the keyboard
  hint at the left.

What does not mirror:

- The vertical rhythm — band heights, row heights, gaps, and every symmetric
  padding.
- Radii, border widths, colours, and type sizes.
- The pills, chips and dots, which are symmetric already.
- The key names in the hint. `J / K` stays Latin and reads left to right inside
  its own run, and giving that line its own direction keeps it from reordering.
- A number keeps its own internal direction regardless of the paragraph around
  it, so the counts and the record identifiers stay intact.

Frappe's mechanism for the mirror, in the installed source:

- A language counts as right-to-left when it is one of `ar`, `he`, `fa`, `ps` —
  `frappe/public/js/frappe/utils/utils.js:1059`.
- The desk gets a `.frappe-rtl` class whose rules set `text-align: right` and
  force `direction: rtl` on inputs and textareas —
  `frappe/public/scss/desk/global.scss:551`, `:559`.
- The whole desk stylesheet is regenerated through `rtlcss` into a mirrored
  bundle — `frappe/esbuild/esbuild.js:11`, `:163`, `:176`, `:232`, `:234` — and
  the mirrored file is requested by an `rtl_` prefixed bundle path,
  `frappe/public/js/frappe/assets.js:129`, `:131`.
- Direction-sensitive glyphs are chosen in JavaScript rather than left to CSS:
  the form toolbar picks `es-line-right-chevron` or `es-line-left-chevron` by
  `frappe.utils.is_rtl()` — `frappe/public/js/frappe/form/toolbar.js:322`,
  `:330`. A chevron drawn in this layout's list or action bar carries the same
  obligation.

## The Frappe surface it maps onto

Read against frappe 15.109.0.

- **Rail counts** map onto the list view's group-by sidebar. The client asks
  `frappe.desk.listview.get_group_by_count` per field —
  `frappe/public/js/frappe/list/list_sidebar_group_by.js:105`, `:163`, `:177` —
  and the server aggregates there,
  `frappe/desk/listview.py:33`.
- **The desk page frame** gives one sidebar column and one main column:
  `<div class="col-lg-2 layout-side-section">` at
  `frappe/public/js/frappe/ui/page.js:101`, bound at `:125`. The rail is native
  to that frame; the middle list column is extra structure this layout adds.
- **List paging** already behaves like an inbox: 100 rows on a large screen and
  20 otherwise — `frappe/public/js/frappe/list/base_list.js:47` — with "load
  more" advancing `start` by `page_length`, `:420`, `:421`.
- **The record's two-column field band** maps onto the form layout's own
  columns, made per column break at
  `frappe/public/js/frappe/form/layout.js:186`, `:228`, `:329`.
- **History** maps onto the form timeline —
  `frappe/public/js/frappe/form/footer/form_timeline.js:10`, `:118`.
- **The action bar** maps onto the page's primary and secondary actions,
  `frappe/public/js/frappe/ui/page.js:319`, `:329`. The primary action is
  already bound to `ctrl+s` for free —
  `frappe/public/js/frappe/ui/keyboard.js:187`.
- **Next / previous record** exists as `navigate_records`,
  `frappe/public/js/frappe/form/form.js:1245`, reached by `shift+ctrl+>` and
  `shift+ctrl+<` at `frappe/public/js/frappe/form/form.js:140`, `:150`, and by
  the toolbar chevrons at `frappe/public/js/frappe/form/toolbar.js:318`. A bare
  `j` / `k` binding registers through `frappe.ui.keys.add_shortcut`,
  `frappe/public/js/frappe/ui/keyboard.js:24`, `:64`.
- **Acting on several rows at once**, if the layout ever grows a multi-select,
  maps onto `BulkOperations`,
  `frappe/public/js/frappe/list/bulk_operations.js:1`.
