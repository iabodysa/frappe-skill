# D — Command Console

A single centred column of work, grouped by the state each item is waiting in,
with no sidebar, no filter bar and no toolbar. Every action arrives through a
command palette floating over the list.

It suits a page whose reader already knows what the work is and only needs to
move it: a renewals queue, an approval queue, a payment queue. It suits a
reader who works the same page all day and learns the keys. It suits a page
where the row count per state matters more than any single row's detail.

It suits a page poorly when the reader arrives cold, needs to discover what
filters exist, or visits once a month.

## The layout

```
┌────────────────────────────────────────────────────────────────────────┐
│  Visas / Renewals                            [   search   ]  [ ]       │ 60
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│      ● Awaiting operations approval ─────────────────────────  6       │
│      ┌──────────────────────────────────────────────────────────┐      │
│      │ ☐  ▬▬▬▬▬▬▬▬  ▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭  ▬▬▬▬   ( pill )    │      │
│      │ ☐  ▬▬▬▬▬▬▬▬  ▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭  ▬▬▬▬   ( pill )    │      │
│      │ ☐  ▬▬▬▬▬▬▬▬  ▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭  ▬▬▬▬   ( pill )    │      │
│      └──────────────────────────────────────────────────────────┘      │
│                                                                        │
│      ● Waiting for legal approval ───────────────────────────  3       │
│      ┌──────────────────────────────────────────────────────────┐      │
│      │ ☐  ▬▬▬▬▬▬▬▬  ▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭  ▬▬▬▬   ( pill )    │      │
│      └──────────────────────────────────────────────────────────┘      │
│                                                                        │
│      ● Awaiting payment ─────────────────────────────────────  5       │
│      ┌──────────────────────────────────────────────────────────┐      │
│      │ ☐  ▬▬▬▬▬▬▬▬  ▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭  ▬▬▬▬   ( pill )    │      │
│      └──────────────────────────────────────────────────────────┘      │
│  220 │                       840                            │   220    │
└────────────────────────────────────────────────────────────────────────┘

                    the palette, centred, floating over the list
              ┌────────────────────────────────────────────────┐
              │  Type a command…                               │ 48
              ├────────────────────────────────────────────────┤
              │  ▫  Approve selected  ───────────────  [ ⏎ ]    │ selected
              │  ▫  Schedule renewal  ───────────────  [   ]    │
              │  ▫  Enter SADAD number  ─────────────  [   ]    │
              │  ▫  Confirm payment  ────────────────  [   ]    │
              │  ▫  Reject with reason  ─────────────  [   ]    │
              │  ▫  Export selection  ───────────────  [   ]    │
              └────────────────────────────────────────────────┘
                                520 wide, 300 tall
```

## The regions

**header** — one row, 60 tall, 32 of side padding. The page's name on the
leading edge as a two-level breadcrumb, a rule that eats the free width, then
a search field and one square icon button on the trailing edge. Nothing else
lives here: no filter chips, no view switcher, no primary button.

**stream** — the whole rest of the page, one column, growing to fill. It carries
220 of padding on each side, which leaves an 840 measure in a 1280 frame. That
gutter is the layout's main decision: it is what makes a list feel like a
document rather than a table.

**group header** — a small dot, a 10px label naming the state being waited on,
a hairline that eats the free width, and a count on the trailing edge. It takes
18 of space above and 8 below, which is the only vertical rhythm in the page.

**row** — a checkbox, a fixed-width primary field, a detail field that eats the
free width, a fixed-width meta field, and a status pill on the trailing edge.
Rows carry a 1px border on all sides rather than a shared divider, so a row is a
unit that can be selected, not a stripe in a table.

**palette** — an overlay, 520 by 300, horizontally centred and floating over the
stream at a fixed offset from the top. A text input at the head, then command
rows: an icon, a label, a rule, and a keycap on the trailing edge. One row
carries a filled background as the active row.

## What it does well

The reader sees the shape of the backlog in one glance, because the group
headers and their counts are the only strong elements on the page.

Nothing competes with the work. There is no chrome to skip past, so the eye
lands on the first row of the first group immediately.

The 840 measure keeps a row scannable. A row that runs the full 1280 forces the
eye to travel between the primary field and the status pill.

Actions do not consume permanent space. A page whose action set grows over time
grows only its palette, never its header.

The row is deliberately reduced to five slots. That constraint is what keeps
twenty rows readable without a header row explaining the columns.

## What it costs, and where it breaks

Everything is discoverable only by typing. A reader who does not know the
palette exists sees a page with no verbs on it. A visible hint near the search
field earns its space here.

The gutter throws away 440 of 1280. On a 1280 screen that is a real loss; on a
1920 screen it is the point. A layout that fixes the measure rather than the
padding survives both.

The row has no header, so the meaning of the fixed-width meta field and the
status pill is learned rather than read. Two fields is near the ceiling for
that.

Group order is a decision the page makes, not the reader. There is no sort
control anywhere in the sketch, so a reader who wants the oldest item first has
nowhere to ask for it.

The palette floats over the rows it acts on. When it opens, the selection it is
about to change is partly hidden behind it. Anchoring it lower, or showing the
selected count in its input line, closes that gap.

A group whose count is zero has no representation. Deciding whether an empty
state disappears or holds its place is part of adopting this layout.

## Right to left

The page direction flips, and with it the header's contents: the breadcrumb
moves to the right edge, the search field and icon button to the left. The
breadcrumb separator between the two levels reverses along with them.

Every row's slot order flips: the checkbox to the right, then the primary field,
the growing detail, the meta field, and the status pill on the left. The same
flip applies to the group header — dot and label right, count left — and to
every palette command row, whose keycap ends on the left.

What does not change: the 220 gutter is symmetric, so the stream does not
visibly move. The palette is horizontally centred, so it stays put. Its shadow
has no horizontal offset, so it needs no mirroring. Vertical rhythm, row height,
and the type scale are unaffected.

What deserves care: the counts and any Latin identifier inside a row sit inside
Arabic text, so their own direction is decided per run of characters, not by the
page. A keycap glyph is a symbol, not text, and reads the same either way.

Arabic at 9px and 10px, which the group header and count use, is thinner than
Latin at the same size. Raising the two smallest steps one notch for an Arabic
build is worth testing before shipping.

## The Frappe surface it maps onto

All paths are relative to the `frappe` app.

**The sidebar this layout removes is a toggle, not a deletion.** The list view
registers Toggle Sidebar as a menu item on Ctrl+K
(`frappe/public/js/frappe/list/list_view.js:1757-1763`), and the state persists
in localStorage and is applied by a `no-list-sidebar` class on the body
(`frappe/public/js/frappe/list/base_list.js:292-301`). A page that wants D's
chrome-free stream can start from the existing list view with the sidebar
hidden rather than from a new page type.

**The palette has a near-twin in the Desk.** Global search opens on Ctrl+G,
which focuses `#navbar-search`
(`frappe/public/js/frappe/ui/keyboard.js:198-206`). It searches rather than
acts, so a command palette is an addition, not a replacement.

**Shortcuts are registered, not hand-bound.** `frappe.ui.keys.add_shortcut`
takes `{shortcut, action, description, page, condition}` and keeps the entry in
a list (`frappe/public/js/frappe/ui/keyboard.js:24-73`); Shift+/ opens a dialog
rendering that list (`frappe/public/js/frappe/ui/keyboard.js:226-232`). A
palette built on the same registry gets its own help screen for free.

**Selection already swaps the page's verbs.** Checking rows calls
`toggle_actions_menu_button`, which shows the Actions menu and clears the
primary action (`frappe/public/js/frappe/list/list_view.js:590-598`); the
checked set comes from `get_checked_items`
(`frappe/public/js/frappe/list/list_view.js:1643`). That menu is the palette's
existing content.

**Bulk verbs exist.** `BulkOperations`
(`frappe/public/js/frappe/list/bulk_operations.js:1`) carries delete, edit,
print, assign and submit-or-cancel, the last routed through
`frappe.desk.doctype.bulk_update.bulk_update.submit_cancel_or_update_docs`
(`frappe/public/js/frappe/list/bulk_operations.js:275-281`). "Approve selected"
maps onto submit; "Reject with reason" does not map onto anything and needs its
own whitelisted method.

**The grouped stream is the gap.** Group-by in the list view is a sidebar filter
over `assigned_to`, `owner` and user-chosen fields
(`frappe/public/js/frappe/list/list_sidebar_group_by.js:9-13`) — it narrows the
result, it does not section it. Grouping that actually sections rows lives in
the report view's GroupBy control
(`frappe/public/js/frappe/views/reports/report_view.js:125-130`). Rendering D's
group headers inside a list result is custom work either way.

**Right to left is decided by the language, and the stylesheet is a separate
build.** On the client, `frappe.utils.is_rtl` tests the boot language against
`ar`, `he`, `fa`, `ps` (`frappe/public/js/frappe/utils/utils.js:1059-1060`);
the server twin is `is_rtl` in `frappe/utils/jinja_globals.py:141-146`. The
build runs `rtlcss` over the stylesheets and emits them under `/css-rtl/`
(`esbuild/esbuild.js:11`, `esbuild/esbuild.js:163`,
`esbuild/esbuild.js:176-181`, `esbuild/esbuild.js:232-235`); `bundled_asset`
prefixes a css path with `rtl_` when the language is right-to-left
(`frappe/utils/jinja_globals.py:128-136`), and the RTL manifest is merged over
the main one (`frappe/utils/__init__.py:1019-1025`). Logical properties in
custom css survive this pipeline unchanged; physical left/right values are what
rtlcss rewrites.
