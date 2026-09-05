# Page layouts D, E and F, and what each one costs

MUST read the comparison table, the choosing rule, shapes A, B and C, and the settled-by
table in `references/page-layout-sketches.md`; this file holds the remaining three shapes
and the rules that apply to all six, split out only because the combined file stood over
the skill's own twelve-thousand-byte chapter ceiling.

---

## D · Command Console

Almost no chrome. A grouped list, and everything reachable by typing.

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

