# A — Dense Desk

The ERP terminal school. One table fills the whole viewport, every band above it
is a single strip of chrome, and whitespace is spent only where it separates two
different kinds of control. It suits a work queue an operator sits in all day:
thousands of records, a small fixed set of columns, and bulk action as the main
verb. It suits a browse-and-discover page much less well.

## The layout

```
┌───────────────────────────────────────────────────────────────────────┐
│ topbar  49px                                                          │
│ VISAS CONTROL ──────────────── [6628 payment][349 ops][130 new][9 leg]│
├───────────────────────────────────────────────────────────────────────┤
│ filters 46px                                                          │
│ [▭][▭][▭][▭][▭][▭][▭][▭][▭]     nine equal controls, one row, no wrap │
├───────────────────────────────────────────────────────────────────────┤
│ bulkbar 38px                                                          │
│ 12 selected [Approve][Schedule][SADAD][Confirm][Reject] ─ 11,812 rows │
├───────────────────────────────────────────────────────────────────────┤
│ thead   28px                                                          │
│ ☐  Employee   Visas exp  Status   Corporation  Department  SADAD  Fee │
├───────────────────────────────────────────────────────────────────────┤
│ rows    32px each, sixteen visible, alternating #ffffff / #fbfbfb     │
│ ☐  ▬▬▬▬▬▬▬▬  ▬▬▬▬▬  ▬▬▬▬▬▬  ▬▬▬▬▬  ▬▬▬▬  ▬▬▬▬▬  ▬▬▬       [ action ] │
│ ☐  ▬▬▬▬▬▬▬▬  ▬▬▬▬▬  ▬▬▬▬▬▬  ▬▬▬▬▬  ▬▬▬▬  ▬▬▬▬▬  ▬▬▬       [ action ] │
│ ☐  ▬▬▬▬▬▬▬▬  ▬▬▬▬▬  ▬▬▬▬▬▬  ▬▬▬▬▬  ▬▬▬▬  ▬▬▬▬▬  ▬▬▬       [ action ] │
│ …                                                                     │
├───────────────────────────────────────────────────────────────────────┤
│ paging  32px                                                          │
│ 1 2 3 … 296 ─────────────────────────────────────────────  40 / page  │
└───────────────────────────────────────────────────────────────────────┘
```

Every band is full-bleed. There is no sidebar and no card; the page edge is a
16px inline pad and nothing else. Vertical rhythm comes from the band heights
rather than from margins between them — the bands sit flush, separated by a
change of background tone.

## The regions

**topbar** — the page identity on one side, a row of counter chips on the other,
joined by a hairline rule that eats the leftover width. Each chip pairs a number
at 12px semibold with a category word at 10px regular. The chips are the only
summary the layout offers; there is no dashboard above the table. Four of them
is about the ceiling before the row stops reading as a strip and starts reading
as a panel.

**filters** — nine equal-width controls in one row, each growing to share the
width evenly. Equal width is the whole idea: the operator learns positions
rather than labels. The row sits on white with a hairline border so it separates
from the grey bar above it. Nine is the point where each control is around 130px
wide at a 1280px viewport, which holds a short label and a caret and no more.

**bulkbar** — the selection count, then the verbs that apply to the selection,
then a rule, then the total row count pinned to the far end. It holds a fixed
place in the stack rather than appearing on selection, so the table below it
keeps its position when the selection changes. The cost is a strip of chrome
that reads as inert while nothing is selected.

**thead** — a 9px semibold label per column on the darkest of the greys, so the
header reads as a rule rather than as content. Column widths are fixed here and
repeated in every row; the header is what makes the fixed widths legible.

**rows** — 32px tall, 8px block padding, 14px between columns, a 14px checkbox
leading. The zebra stripe carries the row boundary, so there are no horizontal
rules at all. The trailing action chip is fixed at 60px and sits after the last
data column rather than pinned to the far edge.

**paging** — a page-number run on one side, the page size on the other, the same
hairline rule between them that the topbar and bulkbar use. Three bands out of
six share that pattern, which is what makes the page feel like one object.

## What it does well

Sixteen rows are visible at 820px of height with six bands of chrome around
them, roughly twice what a card layout fits in the same space.

Column positions are fixed, so an operator scanning the fifth column skips the
header on every page after the first. The zebra stripe does the row separation
that rules would otherwise do, which saves a pixel of height per row and a great
deal of visual noise across sixteen of them.

Selection, action and count live in one strip, so the whole bulk workflow is one
horizontal sweep: check rows, move up, press a verb, read the count.

The greyscale is doing structural work rather than decorative work. Six surface
tones — #f7f7f7, #ffffff, #fafafa, #ededed, #fbfbfb, #f0f0f0 — separate six
bands with no borders except one hairline under the filter row. A colour accent
added later has somewhere to land precisely because the base is neutral.

## What it costs

Nine equal filters at 1280px are already tight. Below roughly 1000px they stop
holding a readable label, and the row has no wrap behaviour designed into it.

Eight columns plus an action chip consume 1020px of the 1280px. There is no room
for a ninth column, and the two widest — Employee at 170px and Status at 150px —
are the ones a long Arabic name or a long status phrase truncates first.

The bulkbar occupies 38px permanently for a control that is meaningful only
during a selection. On a short viewport that is a row of data given up.

There is no place for a record preview, a chart, or a detail pane. Opening a
record leaves the page entirely, and returning re-enters at the top of the list
unless scroll position is preserved deliberately.

The 9px column headers and the 10px meta text sit below the size most Desk
themes use, and they read as small in Arabic, where the letterforms carry more
detail per glyph than Latin ones.

## Under right-to-left

What mirrors: the order of every horizontal row. The brand moves to the right of
the topbar and the counter chips to the left. The filter row reverses, so the
first filter sits at the right edge. In the bulkbar the selection count leads
from the right and the total row count settles at the left. The column order
reverses, so the checkbox column and the Employee column lead from the right and
the action chip trails at the left. In the paging band the page-number run leads
from the right and the page size settles at the left.

What holds: every vertical relationship. Band order down the page is unchanged,
band heights are unchanged, the 32px row height and the zebra phase are
unchanged, and the 16px inline padding stays symmetric, so the flip costs
nothing at the page edge.

What needs a second look: numeric columns. A Fee column set right-aligned in a
left-to-right layout becomes left-aligned under the flip if its alignment is
written as a physical side rather than a logical one; writing it as
end-alignment keeps the digits against the column's trailing edge in both
directions. The same applies to the SADAD reference and the Visas expiry date,
where the digits stay Latin even when the surrounding text is Arabic, and the
bidirectional algorithm places them correctly only when the field is isolated
from the run around it.

Truncation flips side as well. The ellipsis lands at the left of an Arabic name
in a fixed-width cell, which is where the family name usually sits, so an
Employee column that truncates loses different information in each direction.

## The Frappe surface it maps onto

The Desk list view already produces most of these bands, and the sketch mostly
re-proportions them rather than replacing them. Line numbers are read from
frappe 15.109.0.

- The header strip is built by `get_header_html_skeleton` at
  `frappe/public/js/frappe/list/list_view.js:741`, which emits
  `<header class="level list-row-head">` holding a `.list-header-subject` group,
  a `.checkbox-actions` group carrying `.list-check-all`, and a `.level-right`
  group. The sketch's **thead** and **bulkbar** are those groups pulled apart
  into separate bands.
- The row count the bulkbar pins to its trailing edge is the Desk's
  `<span class="list-count">`, emitted at
  `frappe/public/js/frappe/list/list_view.js:730`.
- The bulk-action affordance in the Desk appears only while a selection exists —
  `toggle_actions_menu_button(toggle)` at
  `frappe/public/js/frappe/list/list_view.js:590`, driven by the checked set
  gathered at `frappe/public/js/frappe/list/list_view.js:1619`. The sketch keeps
  the band resident instead, which is a departure worth naming out loud.
- The per-row checkbox class is applied at
  `frappe/public/js/frappe/list/list_view.js:2206`.
- A data cell is `list-row-col ellipsis`, with `text-right` added for a numeric
  field, at `frappe/public/js/frappe/list/list_view.js:900`. The ellipsis class
  is what the sketch's fixed column widths rely on, and `text-right` is the
  physical alignment the right-to-left note above concerns.
- Desk columns of type Field also carry `hidden-xs`, assigned in the class map
  at `frappe/public/js/frappe/list/list_view.js:897`, and that class resolves to
  `display: none` between the xs and sm breakpoints at
  `frappe/public/scss/desk/global.scss:140`. That is the mechanism the sketch's
  narrow-screen column dropping reuses without new CSS.
- Page size in the Desk is one of `[20, 100, 500, 2500]`, built at
  `frappe/public/js/frappe/list/base_list.js:375`, and the default is chosen at
  `frappe/public/js/frappe/list/base_list.js:47` as 100 on a large screen and 20
  otherwise, using `frappe.is_large_screen` from
  `frappe/public/js/frappe/utils/common.js:277`. The sketch's `40 / page` is not
  one of those values.
- The Desk pages with a single `Load More` button rather than numbered pages —
  `frappe/public/js/frappe/list/base_list.js:393`. The sketch's `1 2 3 … 296`
  run is a new control rather than a restyled existing one.
- A standard list page also builds a sidebar, at
  `frappe/public/js/frappe/list/base_list.js:277`. The sketch drops it, which is
  where most of its extra table width comes from.
- Standard filters are rendered by the `FilterArea` class at
  `frappe/public/js/frappe/list/base_list.js:595` through
  `make_standard_filters` at `frappe/public/js/frappe/list/base_list.js:619`.
  The sketch's nine equal controls are that area given a fixed count and an even
  distribution.
- Right-to-left in Frappe is a served-asset decision rather than a runtime one:
  `is_rtl()` at `frappe/utils/jinja_globals.py:141` returns true when the
  request language is one of `ar`, `he`, `fa`, `ps`, and `bundled_asset` at
  `frappe/utils/jinja_globals.py:128` prefixes the stylesheet path with `rtl_`
  when it does. A layout that expresses its mirroring in logical properties gets
  the flip from that stylesheet without a second set of rules.
