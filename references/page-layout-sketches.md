# Six page layouts and what each one costs

Six shapes for one screen that manages a queue of records through a pipeline. They differ in one
choice: how much of the screen is given to seeing many records at once, and how much to acting on
one. Every shape below fits the same 1280-wide desk area, and every one of them is a way of
filling the regions a desk page already hands you — the head, the filter strip, the optional side
column, and the body.

Pick one, adapt it, and read its cost line before you commit; the cost is what the shape takes away,
and it is always something.

## Choosing between them

| If the day's work is | The shape that fits | Because |
|---|---|---|
| scanning many rows and comparing them | **A · Dense Desk** | rows per screen is the only thing it optimises |
| moving records between named stages | **B · Status Board** | the stages are the layout, so the count per stage is free |
| clearing a queue, one record at a time | **C · Triage Inbox** | the decision and the evidence sit on one screen |
| repeating a small set of commands fast | **D · Command Console** | the commands are typed, so the chrome can go |
| answering how many and how bad first | **E · Dashboard First** | the numbers lead and the table is the drill-down |
| one decision over a whole batch | **F · Guided Batch** | the screen asks a question instead of offering a menu |

Two questions settle it faster than the table. First: does the user arrive knowing which record they
want, or does the screen have to tell them? A, B and E answer the second; C, D and F assume the
first. Second: how many records does one action touch? One record points at C, a handful points at
A or D, and the whole filtered set points at F.

Mixing is allowed and often right. Three of these are the same data at three depths, so a tab strip
that swaps the body between C, E and F over one shared head is a real option, and cheaper than three
pages.

---

## A · Dense Desk

An ERP or terminal screen. Maximum rows per screen, no whitespace, everything on one plane.

```
┌──────────────────────────────────────────────────────────────────────────┐
│ VISAS CONTROL  ------  [6628 payment] [349 ops] [130 new] [9]         49 │
├──────────────────────────────────────────────────────────────────────────┤
│ [ filter v ]  [ filter v ]  [ filter v ]  [ filter v ]                46 │
├──────────────────────────────────────────────────────────────────────────┤
│ 12 selected [Approve][Schedule][SADAD][Confirm][Reject] 11,812        38 │
├──────────────────────────────────────────────────────────────────────────┤
│ [ ] Employee   Visas exp  Status   Corp    Dept   SADAD   Fee         28 │
├──────────────────────────────────────────────────────────────────────────┤
│ [ ] .........  ........  .......  ......  .....  ......  ...             │
│ [ ] .........  ........  .......  ......  .....  ......  ...         512 │
│ [ ] ... 16 rows at 32px ...                                              │
├──────────────────────────────────────────────────────────────────────────┤
│ 1 2 3 ... 296 --------------------------------- 40 / page             32 │
└──────────────────────────────────────────────────────────────────────────┘
```

**Regions.** A topbar carrying the page name and a strip of stage counts that double as filters. A
filter row of typed controls. A bulk bar that appears with a selection, holds every action that
operates on checked rows, and shows the total on the right. A column header row. The rows. A pager.

**Good for.** Sixteen rows at a glance in 512px, and a comparison across eight columns without
scrolling sideways. The counts in the topbar answer "how much is left" without a second screen. The
bulk bar puts five verbs one click from a selection.

**Costs.** Nothing on this screen explains a record; a row is an identifier, not a story, so any
question beyond the eight columns is a second navigation. Density is unforgiving of long values — an
Arabic full name and a corporation name both want more than the 170px and 120px drawn here, and
truncation destroys the scan the layout exists for. Eight columns is near the practical ceiling
before the row stops reading as one thing.

**The Frappe surface.** This is the report view — the list machinery with a DataTable body — and the
shipped one already gives columns, inline edit, totals and the checkbox column. Filling the head:
the stage counts go in `add_inner_button` calls or an indicator, the filter row is `page.add_field`
per control, and the bulk verbs belong in the Actions dropdown that appears with the selection. Two
behaviours to plan around. The framework clears the primary action the moment a row is checked, so a
create button and a bulk bar can not share the head. And the shipped list pages by show-more from a
page length of 100 on a large screen and 20 otherwise, not by numbered pages — the numbered pager
drawn above is code you write.

**Under RTL.** Columns mirror, so the checkbox column and the identifier land on the right and the
numeric tail on the left. The two things that break: a column whose width was tuned for a Latin
label, and any digit-plus-unit cell, which reads in its own direction inside a mirrored row. Sizing
columns in `ch` rather than `px`, and wrapping a mixed-script cell so its direction is set on the
cell rather than inherited, both survive the flip.

---

## B · Status Board

A kanban. The pipeline is the screen, and a record moves by being dragged.

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Renewal pipeline ----------------------------- [ action ]             60 │
├──────────────────────────────────────────────────────────────────────────┤
│ [chip] [chip] [chip] [chip] [chip]                                    38 │
├──────────────────────────────────────────────────────────────────────────┤
│  New 130    Ops 349    Legal 9    Payment    Renewed                     │
│  +--------+ +--------+ +--------+ +--------+ +--------+                  │
│  | card62 | | ...... | | ...... | |  6628  | |  3947  |                  │
│  | ...... | | ...... | | ...... | | ...... | | ...... |   722            │
│  | ...... | |        | |        | | ...... | | ...... |                  │
│  |   :    | |   :    | |   :    | |   :    | |   :    |                  │
│  +--------+ +--------+ +--------+ +--------+ +--------+                  │
│    238 each                                                              │
└──────────────────────────────────────────────────────────────────────────┘
```

**Regions.** A head with the board name and one action. A chip row of saved filters. Five columns,
each a stage, each headed by its own name and count, each holding cards of roughly 62px.

**Good for.** The distribution is the layout — a stage that is backing up is visible before anyone
reads a number. Moving a record is one gesture and needs no form. It is the best of the six for a
standing meeting, because the shape of the work is legible from across a room.

**Costs.** It stops working the moment one column is large. A stage holding 6,628 records is a column
you can not scroll to the end of, and the card count in its header becomes the only honest thing in
it — which means the board is describing a pipeline it can not actually show. Five columns at 238px
each is already tight for an Arabic name plus a date, and a sixth stage would push a column under
200px. Drag is also the only affordance, so a keyboard-only or screen-reader path wants a parallel
route you build yourself.

**The Frappe surface.** The kanban board is a shipped list view type, driven by a Kanban Board record
that names the DocType and the Select field whose options become the columns. The consequence worth
knowing before sketching: the stages have to be the options of one Select field on the DocType, so a
pipeline computed from several fields is not this surface without your own board. Card contents come
from the board's own field list, not from the list view's columns.

**Under RTL.** The column order mirrors, and that is the whole point of checking it — a pipeline
reads as progress, so the first stage belongs where reading starts. A board left in source order
shows the pipeline running backwards. Drag itself is direction-agnostic, but any arrow, chevron or
"move forward" icon between columns is a physical direction that wants flipping with the layout.

---

## C · Triage Inbox

A mail client. Rail, list, detail. One record at a time, decide, next.

```
┌────────────┬─────────────────┬───────────────────────────────────────────┐
│ VISAS      │ [ search      ] │ ..........................             84 │
│            │                 │ .....................................     │
│ My queue   │ > ...... [##]   │                                           │
│      349   │ > ...... [##]   │ .....................................     │
│ New   130  │   ...... [##]   │ ..................................... 250 │
│ Legal   9  │   ...... [##]   │                                           │
│ Awaiting   │   ...... [##]   │ History                                   │
│ pay  6628  │   ...... [##]   │ .....................................  94 │
│ Blocked 3  │   ...... [##]   │                                           │
│ Renewed    │   ...... [##]   │ [Approve][Schedule][SADAD][Rej]  J/K   63 │
│     3947   │   50px each     │                                           │
│ < 210 >    │ < 340 >         │ < 730 >                                   │
└────────────┴─────────────────┴───────────────────────────────────────────┘
```

**Regions.** A rail of saved queues, each with a live count. A search box over a list of 50px rows,
the current one marked by a bar on its leading edge. A detail pane in four bands: identity header,
the fields that carry the decision, a history band, and a fixed action bar with the verbs and the
keyboard hint.

**Good for.** Deciding without navigating. The evidence and the verb are on one screen, so the cost
per record is one keystroke, and a queue of 349 is genuinely clearable. The rail counts make
progress visible while the work is happening. It degrades well: on a narrow screen the three panes
collapse to a stack in an order that still makes sense.

**Costs.** It shows one record at a time, so any question that compares records is answered
elsewhere. Three panes over 1280px leaves 730px for the detail, which is one column of fields, not
two — a record needing a wide form outgrows this shape. The action bar at the bottom of the detail is
a commitment: every verb lives there, so a fifth and sixth verb start crowding the keyboard hint off
the row. And the counts in the rail are queries that run on every arrival, so they want to be cheap
or cached.

**The Frappe surface.** A desk page constructed with the sidebar left on — asked for at construction,
not added later — gives you the rail as a real column, and it comes out around one sixth of the
width, which is close to the 210px drawn. The middle list and the detail pane are your own markup in
the page body; no shipped surface splits the body in two. Keyboard next and previous are shortcut
registrations, and registering them through the framework's shortcut helper rather than a raw key
listener is what puts them in the help overlay. Building the rail counts as one grouped query rather
than one query per queue is the difference between a page that opens and one that hangs.

**Under RTL.** The rail moves to the right and the detail to the left, and the selection bar on a
list row moves to the row's leading edge with it. The band that needs attention is the action bar:
verbs mirror, so a destructive action drawn last on the left lands first on the right unless the
order is expressed logically. The keyboard hint is Latin text inside a mirrored row and wants its
own direction set, or it renders with the slash in the wrong place.

---

## D · Command Console

Almost no chrome. A grouped list, and everything reachable by typing.

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Visas / Renewals --------------------  [ search ]   [ cmd ]           60 │
├──────────────────────────────────────────────────────────────────────────┤
│    o Awaiting operations approval ------------------  6               38 │
│    [ ] ........  ......................  ......  [###]                32 │
│    [ ] ........  ......................  ......  [###]                   │
│    o Waiting for legal approval --------------------  3                  │
│    [ ] +----------------------------------------+                        │
│    o   | Type a command...                      | 48                     │
│    [ ] +----------------------------------------+                        │
│        |  Approve selected               [Enter]| 36                     │
│        |  Schedule renewal                      |                        │
│        |  Enter SADAD number                    | 520                    │
│        |  Confirm payment                       |  x                     │
│        |  Reject with reason                    | 300                    │
│        |  Export selection                      |                        │
│        +----------------------------------------+                        │
│    <-- 220 gutter -->        <-- 840 content -->                         │
└──────────────────────────────────────────────────────────────────────────┘
```

**Regions.** A thin head with the route as a breadcrumb and a search. One content column, inset by a
220px gutter on each side, holding alternating group headers and item rows. A palette that floats
over the middle of the screen and holds every command with its shortcut.

**Good for.** Speed for someone who already knows the verbs. Grouping by state means the list is
self-sorting and needs no status column. The 840px measure keeps rows readable rather than sprawling,
and the palette means the number of available commands is not limited by the width of a toolbar —
twenty commands cost the same screen space as five.

**Costs.** It is hostile to a first-time user; nothing on the screen names what can be done until the
palette is opened, so discoverability is entirely carried by one keystroke that has to be taught. The
gutters throw away a third of the width, which is a real loss on a laptop and the reason this shape
looks luxurious and reads as sparse. A grouped list also has no fixed row position, so a record moves
when its state changes, which is disorienting during bulk work.

**The Frappe surface.** The navbar already ships a search that resolves typed text into routes,
DocTypes and reports, so a second palette on the page competes with it — reusing the shipped one for
navigation and keeping a page-owned palette strictly for the page's own verbs avoids two overlapping
answers to the same keystroke. The grouped rows are your own body markup. Registering each command
through the shortcut helper is what makes the palette and the keyboard agree, since both then read
one list.

**Under RTL.** The gutters are symmetric, so the content column does not move. The group header's
count moves to the left end and its dot to the right. The palette is centred and stays centred, but
its rows mirror, so a shortcut badge drawn on the right lands on the left. Command labels are the
place this shape hurts most: a typed palette matches on text, so an Arabic label and a Latin command
name both have to be searchable, or half the commands become unreachable by typing.

---

## E · Dashboard First

Numbers on top. The table underneath is the drill-down, not the subject.

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Renewal overview -------------------  [ period ]  [ new ]             64 │
├──────────────────────────────────────────────────────────────────────────┤
│ +---------+ +--------+ +--------+ +--------+ +----------+                │
│ | Awaiting| | Ops    | | Renewed| |Rejected| |Expiring7d| 120            │
│ |  6,628  | |   349  | |  3,947 | |   737  | |    12    |                │
│ | ....... | | ...... | | ...... | | ...... | | ........ |                │
│ +---------+ +--------+ +--------+ +--------+ +----------+                │
├──────────────────────────────────────────────────────────────────────────┤
│ +-- Expiries by month ------------------+ +- Share ----+                 │
│ |  _  #  =  #  -  #  .  #  ,  =  -  #   | |    (o)     | 192             │
│ |  918 wide, 12 bars                    | |  120  .... |                 │
│ +---------------------------------------+ +------------+                 │
├──────────────────────────────────────────────────────────────────────────┤
│ Needs action today --------------------------- see all                37 │
│ [ ] ........  ..........................  .....  [ act ]              38 │
│ [ ] ... 6 rows ...                                                       │
└──────────────────────────────────────────────────────────────────────────┘
```

**Regions.** A head with a period selector and one action. A row of five tiles, each a label, a large
number and a thin bar. A charts band split 918 / 300 between a time series and a share. A short table
under a titled header with a "see all" escape to the full list.

**Good for.** Answering how many and how bad before anyone touches a record. The tiles are a summary
someone repeats out loud, which makes this the shape to open a page on if the page has an audience
beyond the person doing the work. The short table keeps it from being a dead end: the first six rows
that need action are actionable in place.

**Costs.** By the time you reach the table there are 376px left, which is six rows — this is a
starting screen, not a working one, and anyone who spends the day here pays a scroll for every row.
Five tiles is where the row stops reading: a sixth makes each tile under 200px, at which point a
label and a formatted number stop fitting side by side. Every tile and chart is a separate
aggregate query, so the opening cost of this page is the sum of eight queries, and a slow one holds
the whole screen.

**The Frappe surface.** The tiles map onto Number Card records and the two charts onto Dashboard
Chart records, which means the numbers become configuration rather than code — and also that their
refresh and caching follow the record rather than your page. The one behaviour to check before
sketching a per-user tile: a chart's cached result is keyed in a way that does not always separate
one viewer from another, so a number that is supposed to differ per user is worth proving on two
logins. The drill-down table is a list or report view, and "see all" is a route into it with the
same filters applied.

**Under RTL.** Tiles mirror, so the leading tile is on the right, and the tile order is a ranking
that wants to survive the flip. The two things that do not mirror on their own: a bar chart's time
axis, which reads left-to-right by convention in most chart libraries even under `dir=rtl` and has to
be reversed deliberately if the earliest month belongs on the right; and the thin progress bar in a
tile, which fills from its physical start unless it is written with a logical property. Numbers stay
Latin-numeral and left-to-right inside a mirrored tile, which is correct, and only looks wrong if the
label and the number were centred together.

---

## F · Guided Batch

A wizard. The screen asks one question about a whole batch and moves it on.

```
┌──────────────────────────────────────────────────────────────────────────┐
│ (1)New --(2)Ops --(3)Legal --(4)Pay --(5)Renew --(6)Done              56 │
├───────────────────────────────────────────────┬──────────────────────────┤
│ Approve these 349 renewals?                   │ What happens next        │
│ Uncheck anything that should not              │ ................     116 │
│ go through.                   87              │ ................         │
├───────────────────────────────────────────────┼──────────────────────────┤
│ [filt][filt]  347 of 349 checked              │ Flagged (2)              │
│                                               │ +----------------+       │
│ [x] o ......  ........  [##]                  │ | .............. |   146 │
│ [x] o ......  ........  [##]                  │ +----------------+       │
│ [ ] o ... 44px rows ...                       │                          │
│                                               │ Queue after this ste     │
│               916 wide                        │ ............         110 │
├───────────────────────────────────────────────┼──────────────────────────┤
│ [ Back ]  [ Cancel ] [Approve 347]            │      300 wide         67 │
└───────────────────────────────────────────────┴──────────────────────────┘
```

**Regions.** A stepper across the top naming the six stages with the current one marked. A main
column holding the question in plain words, a filter row with a live checked count, and the
checkable rows themselves. A fixed footer with back, cancel and one primary that names the count it
will act on. A side column of consequences: what this step does, what was flagged, and what is
waiting behind it.

**Good for.** Making a bulk action safe. The count in the primary button is the single best feature
of the six sketches, because it means the user commits to a number rather than to a filter they
believe in. Flagging exceptions into a side column instead of blocking the batch keeps 347 records
moving while 2 get attention. The question in words removes the ambiguity that a toolbar of verbs
always carries.

**Costs.** It does one thing. A user who arrived to check a single record has to leave this screen,
so it works as a mode rather than as a home. The stepper is a promise that the pipeline is linear,
and it becomes a lie the first time a record skips a stage or goes backwards. The layout is also
the most code of the six — no part of it is a shipped surface — and the side column's three panels
are three more queries per step.

**The Frappe surface.** Nothing ships in this shape; the closest precedent in the framework is the
setup wizard, which is also the one screen that gives up the standard page head entirely to own the
whole viewport. Two pieces are reusable: the bulk operation helper behind the list view's Actions
menu already handles submitting, cancelling and editing a set of documents with a progress
indicator, and the confirm dialog is the right home for the final commitment if the primary button
opens one. Building the stepper as markup in the page body and leaving the page head empty except
for a title keeps the browser back button meaningful, which a full-viewport takeover loses.

**Under RTL.** The stepper is the whole risk. It carries direction as meaning, so it mirrors — step
one on the right — and every connector, chevron and "next" arrow in it mirrors with it. A stepper
built from a flex row inherits this correctly, and one built from absolute positions does not. The
footer mirrors too, which puts the primary on the left; keeping back on the far trailing edge and
the primary next to cancel preserves the relationship whichever way it flips. The count inside the
primary label is a number embedded in Arabic text and reads correctly only when the whole label is
one translated string with the number interpolated, rather than a label and a number concatenated.

---

## Three decisions that apply to all six

**Ask for the side column before you need it.** The desk page decides at construction whether a
sidebar node exists at all. When it is built as a single column, the node is never created, and
markup appended to it later is discarded without an error — the page simply renders without the rail
and nothing reports why. C needs it, F wants it, and A, B, D and E are better off without it; that
choice is made once, in the constructor call, and changing it later means rebuilding the page.

**Right-to-left is a document attribute, and your own stylesheet is outside it.** The desk sets the
document direction from the user's language, and only for a small set of languages — Arabic among
them. The stylesheets the framework bundles are built a second time through an RTL transform and
swapped in when that language is active. A page's own `.css` file, sitting beside its `.js`, is read
from disk and injected as-is; it gets no such pass. So every physical direction written in a page
stylesheet — `left`, `right`, `margin-left`, `text-align: left`, `padding-right` — survives the flip
unchanged and lands on the wrong side. Writing the page's own rules with logical properties
(`inset-inline-start`, `margin-inline-start`, `text-align: start`) makes the page mirror with the
document for free, and is the single cheapest thing on this list.

**Decide where the head ends and the body begins, once.** All six sketches draw their own top bar,
and all six could instead be filling the head the page already has — a title, an indicator, inner
buttons, a menu, and a filter strip that the framework prepends to the body when the first field is
added. A head you draw yourself is a head that will not mirror, will not collapse on a narrow
screen, and will not appear in the mobile fallback that the framework's own buttons get. Filling the
shipped head and giving the body entirely to the layout is the version of each of these six sketches
that costs least to keep alive.

## Settled by

| what it settles | leaf |
|---|---|
| the slots `make_app_page` hands back, and why a head rebuilt on the second visit doubles | `knowledge/desk/app-page.md` |
| the Page record, the sibling files that are the whole wiring, and the style never removed | `knowledge/desk/page.md` |
| the row that caps the columns, and the width that caps them when it is empty | `knowledge/desk/list-view.md` |
| the six values `execute` is unpacked to, and the turn that makes a report prepared | `knowledge/desk/report.md` |
| the shared cache key that ignores the user and the filters | `knowledge/desk/dashboard-chart.md` |
| the field that grants the card against the method that produces the number | `knowledge/desk/number-card.md` |
| the one screen that gives up the standard page head | `knowledge/desk/setup-wizard.md` |
| the semantic names dark mode re-points, and the ramp step it does not | `knowledge/ui/theme.md` |
| which slot each kind of command belongs in, and which of those is a law | `references/a-desk-surface-is-filled-not-composed.md` |
| which of these surfaces is a record and which is code | `references/the-desk-what-is-metadata-and-what-must-be-code.md` |
