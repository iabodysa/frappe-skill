# E — Dashboard First

Analytics school. Numbers on top, the table is the drill-down.

The page opens with the answer already on screen: five counts, two pictures of the same
data, and only then a short list of the rows a person can act on today. It suits a page
whose reader arrives to ask "how big is the problem" before asking "which one do I open" —
a renewal overview, a collections summary, a monthly close.

It reads poorly as a working queue. A person who arrives to process fifty rows pays for
376px of chrome before the first row appears.

## The layout

Sizes below come from the sketch's own frame, 1280 x 820. LEAD is the side a
right-to-left reader starts from; TRAIL is the side they end on.

```
LEAD                                                                        TRAIL
+---------------------------------------------------------------------------+
| Renewal overview  ------------------------------  [ chip ] [ chip ] [chip] |  64
+===========================================================================+
| +----------+ +----------+ +----------+ +----------+ +----------+          |
| | label    | | label    | | label    | | label    | | label    |          |
| | 6,628    | | 349      | | 3,947    | | 737      | | 12       |          | 120
| | ________ | | ________ | | ________ | | ________ | | ________ |          |
| +----------+ +----------+ +----------+ +----------+ +----------+          |
+---------------------------------------------------------------------------+
| +---------------------------------------------+ +---------------------+   |
| | Expiries by month                           | | Share by status     |   |
| |          #        #                         | |   .-.   [] ------   |   | 192
| |    #  #  #  #  #  #  #     #  #   #  #  #   | |  ( o )  [] ------   |   |
| |  # #  #  #  #  #  #  #  #  #  #   #  #  #   | |   '-'   [] ------   |   |
| +---------------------------------------------+ +---------------------+   |
+---------------------------------------------------------------------------+
| +-----------------------------------------------------------------------+ |
| | Needs action today  ---------------------------------------  see all  | |
| +-----------------------------------------------------------------------+ |
| | (o)  name______   ______________________________  [meta]   [ do it ]  | |
| | (o)  name______   ______________________________  [meta]   [ do it ]  | | 299
| | (o)  name______   ______________________________  [meta]   [ do it ]  | |
| | (o)  name______   ______________________________  [meta]   [ do it ]  | |
| | (o)  name______   ______________________________  [meta]   [ do it ]  | |
| | (o)  name______   ______________________________  [meta]   [ do it ]  | |
| +-----------------------------------------------------------------------+ |
+---------------------------------------------------------------------------+
|                          (empty — the page ends here)                     | 145
+---------------------------------------------------------------------------+
```

## The regions

**Page header (64 tall, white).** The page title at 16px semibold on the lead side, a
hairline that eats the slack, and three controls pinned to the trail side — two wide
(110) and one narrow (90). The narrow one carries the primary verb; the wide two carry the
filters that change what every band below counts.

**KPI strip (120 tall).** Five equal cards, each one growing to fill a fifth of the row.
A card holds a 9px muted label, a 26px semibold number, and a 4px rule beneath it. The
rule is a share-of-total meter, not decoration — the sketch draws it full-width in every
card, so it carries no value yet. Five is the count the sketch decides; a sixth card
would push each below the width its number needs.

**Analytics band (192 tall).** Two cards side by side that answer the same question two
ways: a twelve-bar column chart that grows to take the slack, and a fixed 300-wide card
holding a donut and a four-row legend. Twelve bars reads as twelve months. Four legend
rows reads as the four states the KPI strip counts, minus the derived one.

**Action list (299 tall).** One card. A 12/16-padded header strip in #fafafa carrying the
section title and a `see all` escape to the full list, then six rows at 38 tall each. A
row is: a 20px round avatar, a 150-wide primary field, a field that grows to eat the rest,
an 80-wide meta pill, and a 64-wide action chip on the trail side. Six rows is a sample,
not the list.

**Tail (145 tall).** Nothing. The sketch leaves the bottom eighth empty rather than
stretching the list to fill it — the list is a preview with a fixed appetite.

## What it does well

- The reader gets the number before the noun. A manager who only wants "how many are
  waiting on payment" never scrolls.
- Every region is one row of equal-weight children, so the whole page is four flex rows.
  There is no grid to fight and no column that has to know about another column.
- The action list is short and capped. It never becomes the page's scroll surface, so the
  page keeps a stable height and the numbers stay pinned in view.
- Only one card carries a fixed width (the 300-wide donut card). Everything else grows,
  so the layout survives a wide monitor without a max-width guard.

## What it costs

- 376px of the viewport goes to summary before the first actionable row. On a 768-tall
  laptop that leaves room for about five rows.
- The five KPI cards and the four donut slices restate the same partition twice, and the
  bar chart restates the fifth card. A reader can spend attention reconciling three
  pictures of one dataset.
- Six rows is a preview, so any real work moves through `see all` to another page. The
  page is a lobby, and a person who works the queue daily pays the lobby toll every visit.
- The 4px meter under each number carries no data in the sketch. Shipping it drawn full in
  every card teaches the reader to ignore it, which costs the affordance later.
- The 300-wide donut card is the one thing that cannot shrink. It sets the narrowest
  width at which the analytics band still reads as two columns.

## Right-to-left

**Mirrors on its own.** Every region here is a flex row whose children sit in source
order, and the sketch uses `justify-content: flex-start` / `flex-end` semantics rather
than physical margins. Frappe's `.level-left` / `.level-right` pair is written exactly
that way (`apps/frappe/frappe/public/scss/common/flex.scss:68-74`), so header controls,
row action chips and the `see all` link all land on the trail side without a rule being
written for Arabic. The build also runs every stylesheet through `rtlcss` into a parallel
`rtl_` bundle (`apps/frappe/esbuild/esbuild.js:11`, `:232-235`), which flips whatever
physical padding survives.

**Does not mirror.** Two things:

1. The number card's own body is pinned physically —
   `.widget.number-widget-box .widget-body { text-align: left; }`
   (`apps/frappe/frappe/public/scss/desk/desktop.scss:629,656`). Under Arabic the label and
   the 26px figure sit on the wrong side of the card unless the page overrides it. The
   `rtl_` bundle does flip a `text-align: left` it can see, so the question worth checking
   on the real bench is whether this rule survives into the RTL build or is re-applied by
   a later selector.
2. The bar chart and the donut are SVG drawn by `frappe-charts`
   (`apps/frappe/package.json:49`, options assembled at
   `apps/frappe/frappe/public/js/frappe/widgets/chart_widget.js:576-586`). `rtlcss`
   rewrites CSS, not geometry a library computes in JavaScript, so the twelve months read
   left-to-right whatever the page direction is. Reversing the series before handing it to
   the chart is the lever, and it costs the axis labels their natural order in return.

Numerals are a separate decision from direction. The sketch shows Latin digits with a
thousands comma; Arabic-Indic digits are a formatting choice the layout does not force.

## The Frappe surface it maps onto

This is a Workspace, not a List View. The correspondence is close enough to build on:

- **The page itself** — Workspace, whose body is a JSON block list in the hidden `content`
  field (`apps/frappe/frappe/desk/doctype/workspace/workspace.json:151-155`), with child
  tables for the cards and charts it embeds (`:196` number_cards, `:56` charts,
  `:179` quick_lists).
- **KPI strip** — five Number Card widgets. The renderer is
  `apps/frappe/frappe/public/js/frappe/widgets/number_card_widget.js:5`, the box style is
  `apps/frappe/frappe/public/scss/desk/desktop.scss:629`, and its `min-height: 84px` is
  close to the sketch's 94.
- **The strip's arithmetic** — Frappe lays widget groups on a CSS grid keyed by column
  count (`apps/frappe/frappe/public/js/frappe/widgets/widget_group.js:58`). `grid-col-3`
  is `repeat(auto-fill, minmax(300px, 1fr))`
  (`apps/frappe/frappe/public/scss/desk/desktop.scss:60-66`). At 1232px of usable width
  that fills four cards per row, not five. Five equal cards is the sketch's decision and
  the stock grid does not produce it.
- **Both charts** — Dashboard Chart, rendered through
  `apps/frappe/frappe/public/js/frappe/widgets/chart_widget.js`. The donut type maps at
  `:571` and caps at six slices for Pie and Donut (`:575`); the sketch's four legend rows
  sit inside that cap.
- **The action list** — a Quick List widget
  (`apps/frappe/frappe/public/js/frappe/widgets/quick_list_widget.js`) or a link out to
  the List View, whose row is a left block and a right block
  (`apps/frappe/frappe/public/js/frappe/list/list_view.js:761-770`, skeleton at `:777-780`).
  The sketch's five-part row is wider than that two-part skeleton, so the middle three
  parts live inside the left block.
- **The header band** — the standard page head, 60px tall by
  `--page-head-height` (`apps/frappe/frappe/public/scss/desk/css_variables.scss:23`) against
  the sketch's 64. Its trail-side controls are `set_primary_action` plus menu items
  (`apps/frappe/frappe/public/js/frappe/ui/page.js:319`, container at `:129`).
- **Card chrome** — `.frappe-card` is a 1px `--gray-300` border with the shadow removed
  (`apps/frappe/frappe/public/scss/common/global.scss:31-35`), which is the sketch's
  #e6e6e6 hairline. `.layout-main-section.frappe-card` also carries an RTL-specific
  `overflow: visible` escape (`apps/frappe/frappe/public/scss/desk/page.scss:91-99`) worth
  copying if a card here ever clips a dropdown.
- **Direction itself** — a session in `ar` is RTL by
  `apps/frappe/frappe/utils/jinja_globals.py:141-147`, and the same predicate exists in JS at
  `apps/frappe/frappe/public/js/frappe/utils/utils.js:1059`.
