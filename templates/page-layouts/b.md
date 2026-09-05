# B — Status Board

Kanban school. The pipeline is the screen, and a row moves by dragging it from one
column to the next.

It suits a page whose single job is to show where every record sits in a workflow
and to move records between stages. It fits a doctype with one Select field that
carries the stage, a small fixed set of stages, and a reader who asks "what is
stuck" more often than "what does this record say".

It fits poorly where the population is large, where the reader needs to compare
values across many fields, or where a record belongs to several stages at once.

## Layout

```
┌─ page frame ── radius 10, 1px border ──────────────────────────────────────┐
│                                                                            │
│  header  16/600 title ── hairline rule grows ──  ▭  ▭  ▭  ▭   4 x 110x28   │
│                                                                            │
├────────────────────────────────────────────────────────────────────────────┤
│  filters  ▭  ▭  ▭  ▭  ▭    5 chips, height 24, one row, no wrap            │
├────────────────────────────────────────────────────────────────────────────┤
│  board — grey ground, the only region that scrolls                         │
│                                                                            │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐     │
│  │New    130 │ │Ops    349 │ │Legal    9 │ │Pay   6628 │ │Done  3947 │     │
│  │ ┌───────┐ │ │ ┌───────┐ │ │ ┌───────┐ │ │ ┌───────┐ │ │ ┌───────┐ │     │
│  │ │▬▬▬▬▬▬▬│ │ │ │▬▬▬▬▬▬▬│ │ │ │▬▬▬▬▬▬▬│ │ │ │▬▬▬▬▬▬▬│ │ │ │▬▬▬▬▬▬▬│ │     │
│  │ │▭▭▭ ▭▭ │ │ │ │▭▭▭ ▭▭ │ │ │ │▭▭▭ ▭▭ │ │ │ │▭▭▭ ▭▭ │ │ │ │▭▭▭ ▭▭ │ │     │
│  │ └───────┘ │ │ └───────┘ │ │ └───────┘ │ │ └───────┘ │ │ └───────┘ │     │
│  │ ┌───────┐ │ │ ┌───────┐ │ │ ┌───────┐ │ │ ┌───────┐ │ │ ┌───────┐ │     │
│  │ │  ...  │ │ │ │  ...  │ │ │ │  ...  │ │ │ │  ...  │ │ │ │  ...  │ │     │
│  │ └───────┘ │ │ └───────┘ │ │ └───────┘ │ │ └───────┘ │ │ └───────┘ │     │
│  │ ┌───────┐ │ │ ┌───────┐ │ │           │ │ ┌───────┐ │ │ ┌───────┐ │     │
│  │ │  ...  │ │ │ │  ...  │ │ │           │ │ │  ...  │ │ │ │  ...  │ │     │
│  │ └───────┘ │ │ └───────┘ │ │  short     │ │ └───────┘ │ │ └───────┘ │     │
│  │           │ │ ┌───────┐ │ │  column    │ │ ┌───────┐ │ │           │     │
│  │  column   │ │ │  ...  │ │ │  keeps     │ │ │  ...  │ │ │  column   │     │
│  │  keeps    │ │ └───────┘ │ │  full      │ │ └───────┘ │ │  keeps    │     │
│  │  full     │ │           │ │  height    │ │ ┌───────┐ │ │  full     │     │
│  │  height   │ │           │ │            │ │ │  ...  │ │ │  height   │     │
│  │           │ │           │ │            │ │ └───────┘ │ │           │     │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘     │
│    gap 12        gap 12        gap 12        gap 12                        │
└────────────────────────────────────────────────────────────────────────────┘

card, 10 padding, gap 6            column header, 13 tall
┌───────────────────────┐          New ──── hairline grows ──── 130
│ ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ │  title   11/600 label            10/400 count
│ ▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭ │  meta
│ ▭▭▭▭▭  ▭▭▭            │  two tag pills, height 14, gap 6
└───────────────────────┘
```

## Regions

**frame** — the whole page, white, one hairline border, radius 10, clipped. It
holds three stacked bands and gives the page one visible edge.

**header** — padding 20 across and 16 down, items centred, gap 8. Reading order:
the page title at 16/600, a hairline rule that takes all the slack, then four
equal 110x28 pill controls pushed to the far end. The rule is the mechanism that
parks the controls at the edge, so a longer title costs the rule and never the
controls. The four controls suit a saved-view switch, a sort control, a filter
opener and one primary action.

**filters** — padding 20 across, 14 down, gap 8, one row of five chips of unequal
width, each 24 tall with a fully rounded end. They read as applied filters, and
their width follows their label. Five chips of this width fill roughly a third of
the row, which leaves room for two or three more before the row runs out.

**board** — the grey ground under the columns, padding 20 across, 16 above and 20
below, gap 12, and the one region that carries the page's scroll. It holds five
equal columns, each growing to fill its share.

**column** — white, hairline border, radius 8, padding 10, gap 8, and full height
of the board whatever its card count. It holds a header row and then its cards.

**column header** — 13 tall, gap 6, items centred: the stage label at 11/600, a
hairline rule that takes the slack, and the card count at 10/400 in grey. The
count reads as the answer to "how big is this pile", so it earns the far edge
where the eye lands after the label.

**card** — the grey-white body, hairline border, radius 6, padding 10, gap 6, and
62 tall in the sketch. It stacks a strong title line, a weaker meta line, and a
row of two tag pills. Nothing else fits in 62, so the card carries a name, one
line of context, and two facts.

## What it does well

The pipeline shape is the answer to the question, so the reader learns the shape
of the backlog before reading a single record. The count beside each stage turns
five numbers into a diagnosis: in the sketch, 6628 waiting on payment against 9
in legal says where the work actually sits.

Moving a record is one gesture in the same view that showed the problem. There is
no list, no form, no save, and no return trip.

The column is a fixed frame with a variable fill, so the eye compares heights
without reading numbers. A column that keeps its full height when it holds two
cards preserves that comparison; a column that shrinks to its content destroys it.

Every card carries the same three shapes in the same order, so scanning a column
costs one glance per card rather than one read.

## What it costs

The board holds every record it shows. A column on this frame has 645 pixels of
card space, which is nine cards, and the sketch's own counts run to four figures.
Anything past the first screenful lives behind a scroll the reader has no reason
to trust, so the layout shows a pipeline honestly and a population dishonestly.

A card 62 tall and a column 238 wide give roughly 198 usable pixels for a title.
An Arabic name plus an visa number does not fit on one line at a readable size,
so the title truncates and the reader loses the identifier that distinguishes two
records with similar names.

Five columns is the ceiling for a full-width desk. A sixth stage either shrinks
every column below a readable card width or pushes the board into sideways
scrolling, and a stage the reader cannot see is a stage the reader forgets.

Drag is the only affordance the layout offers for the thing it exists to do. It
does not survive a touch screen well, it has no keyboard equivalent, and it
cannot express a move that needs a reason, an attachment or a confirmation. A
stage change that requires a document or an approval breaks the gesture, and the
layout has nowhere to put what the gesture cannot carry.

Nothing on the board says why a record sits where it sits. Two tag pills carry
two facts, so age, owner, amount and blocker compete for the same two slots.

## Right to left

The whole thing mirrors. The band stack keeps its order top to bottom, and every
row inside it reverses.

The title moves to the right edge and the four header controls move to the left,
in reversed order among themselves. The filter chips start at the right. The
column order reverses, so the first stage sits at the right edge and the pipeline
runs right to left — which is the correct reading for an Arabic user, because the
pipeline is a sentence and it reads with the language.

Inside a card, the title and meta lines start at the right. The two tag pills
reverse their order, and the wider pill sits on the right.

Inside a column header, the label takes the right and the count takes the left,
with the rule between them as before.

Padding and gaps are symmetric everywhere in this sketch, so no spacing value
changes. Radii are uniform per shape, so no corner changes. The scroll direction
of the board reverses with the writing direction.

What does not mirror: the digits. A count of 6628 and an visa number keep their
left-to-right digit order inside a right-to-left line, and a mixed line of Arabic
words and Latin digits needs an explicit direction on the element that holds it
or the terminal and the browser disagree about where the number ends.

## The Frappe surface

The sketch maps onto the Desk Kanban view. The pieces that already exist:

- The board is a saved document. `frappe/desk/doctype/kanban_board/kanban_board.json:29-42`
  gives it `reference_doctype` and a required `field_name`, and
  `kanban_board.json:47-52` gives it a `columns` child table, so the five columns
  are rows in `Kanban Board Column` and the stage of a card is one Select field.
- The columns render from `frappe/public/js/frappe/views/kanban/kanban_column.html:1-27`.
  Line 1 puts the stage value on `data-column-value` and paints the column from
  `--bg-{{indicator}}`; lines 2-6 give the header its indicator pill and title;
  lines 18-22 add the inline "+ Add" affordance the sketch leaves out.
- The card renders from `frappe/public/js/frappe/views/kanban/kanban_card.html:1-24`:
  a title line at 9-14, a muted `doc_content` line at 16-18, and an empty
  `.kanban-card-meta` at 20-21 — which is exactly the three-shape stack the
  sketch draws, with the meta row as the home for the two tag pills.
- Drag between columns is Sortable on `.kanban-cards`,
  `frappe/public/js/frappe/views/kanban/kanban_board.bundle.js:583-607`. Its
  `onEnd` reads `from_colname` and `to_colname` off the parent column and
  dispatches `update_order_for_single_card`.
- Reordering the columns themselves is a second Sortable on the board,
  `kanban_board.bundle.js:364-370`, with the drag handle bound to
  `.kanban-column-title` — so the column header doubles as the grip.
- The server writes the stage on drop. `frappe/desk/doctype/kanban_board/kanban_board.py:131-137`
  defines `update_order_for_single_card` and asserts write permission on the
  reference doctype before touching anything; `kanban_board.py:117-122` shows the
  bulk path setting the stage field for each moved card.
- The column geometry lives in `frappe/public/scss/desk/kanban.scss:16-35`: the
  board is a flex row with `gap: 0.5em` and hidden overflow, each column is
  `flex: 1 0 260px` with `max-width: 300px`, and `min-height: calc(100vh - 150px)`
  is what keeps a two-card column at full height. The sketch's 238-wide column sits
  just under that 260 basis, so five columns on a 1280 frame land slightly tighter
  than the shipped default.
- The header band and the chip row come free from the list-view chrome the Kanban
  view inherits. `frappe/public/js/frappe/ui/page.js:319` sets the primary action,
  `page.js:134-140` owns the `.menu-btn-group` and `.standard-actions` groups that
  the four header controls land in, and
  `frappe/public/js/frappe/list/base_list.js:879-898` builds the
  `.filter-selector` with its filter button and clear-all button that the chip row
  extends.
- Right to left is a build-time stylesheet swap, not a runtime class.
  `frappe/utils/jinja_globals.py:141-146` treats `ar`, `he`, `fa` and `ps` as
  right-to-left, and `jinja_globals.py:128-136` serves the `rtl_`-prefixed bundle
  for those languages. The mirrored bundle is produced by rtlcss in
  `esbuild/esbuild.js:176-181`, which flips physical directions in the compiled
  CSS. A layout built on `flex` with symmetric padding, as this one is, mirrors
  without any hand-written rule.

Two things the sketch draws that the shipped surface does not provide:

- The per-column card count. `kanban_column.html` has no count element, and
  nothing in `kanban_board.bundle.js` renders one — the only count in that file is
  `comment_count` on a card at lines 760-763. The number beside each stage label
  is new work.
- A bounded column. `frappe/public/js/frappe/views/kanban/kanban_view.js:80` sets
  `this.page_length = 0`, so the Kanban view asks for the whole result set rather
  than a page of it. On the sketch's own counts that is over ten thousand cards in
  one request. Capping each column and offering a "see the rest" path is the change
  that makes this layout safe at that size.
