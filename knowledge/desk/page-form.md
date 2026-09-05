---
name: page-form
description: The filter strip a page builds with add_field is a bootstrap row and every control in it is given col-md-2, so a page that relocates or restyles that strip inherits grid geometry it never asked for, and clear_fields empties the markup while leaving every control registered.
triggers: ["page_form", "page-form row", "add_field", "add_select", "add_data", "add_date", "add_break", "clear_fields", "show_form", "hide_form", "get_form_values", "fields_dict", "col-md-2", "input-xs", "only_input", "col-md-offset-4", "page-control-label", "make_control", "desk page filter bar", "page filter strip", "filters at the top of a desk page", "move the filter form on a desk page", "restyle the page filters", "filters are one sixth of the width", "controls squashed on a page", "negative margin on the filter row", "stale filter value after clearing the form", "the filter boxes at the top of my page are far too narrow", "why are the search boxes on my page squashed into a sixth of the width", "the row of filters sticks out past the edges of the page", "my filter bar has extra space on both sides that i cannot remove", "how do i move the filters somewhere else on the page", "the tick box filter sits lower than the boxes next to it", "one control is misaligned with the rest of the filter row", "the seventh filter drops onto a new line on its own", "i cleared the filters but the old values still come back when i read them", "the filter inputs stop responding to clicks after the page redraws", "the field name shows inside the box and again when i hover over it"]
product: frappe
---

# Page form

## paths

frappe/public/js/frappe/ui/page.js — Page.make, Page.add_field, Page.add_select, Page.add_data, Page.add_date, Page.add_break, Page.clear_fields, Page.show_form, Page.hide_form, Page.get_form_values, fields_dict
frappe/public/js/frappe/form/controls/data.js — placeholder

## rules

MUST expect the strip to be a bootstrap `row` prepended into the page's main section, so it carries the negative horizontal margins a row has and sits outside whatever container the page body puts around its own content.
MUST expect every control to be widened to `col-md-2` — one sixth of the row — because add_field applies that class to the control wrapper after it renders it, whatever the field is; six controls fill the line and the seventh wraps.
MUST relocate the strip by moving `page.page_form` as a whole and stripping `row` and `col-md-2` yourself, because nothing takes them off and a restyled strip fights those two classes at every breakpoint.
MUST call add_break to force the next control onto a new line rather than counting on the wrap; it appends a clearfix that is itself hidden below the extra-small breakpoint.
MUST expect the strip to un-hide itself on the first field; it is created carrying `hide` and add_field calls show_form before it builds anything.
NEVER read hide_form as removing the controls; it puts `hide` back on the strip and leaves every control alive and every value readable.
MUST expect each control to be built with only the input rendered and no label, except a Check, which is built whole and then has its bootstrap offset classes stripped, so a Check sits differently from every neighbour in the same strip.
MUST expect the label to be used three ways at once — as the placeholder when none was given, as the wrapper's `title`, and as a hover tooltip bound on the wrapper — so a page that hides the label still shows it on hover and inside the input.
MUST clear the registry yourself after clear_fields; it empties the strip's markup and leaves fields_dict holding every control, so a later get_form_values reads values off detached controls and returns them as if the strip still carried them.
NEVER rebuild the strip on a re-render without detaching it first; the controls are jQuery-bound and emptying their parent destroys their handlers while fields_dict keeps pointing at them.
MUST size a Button field yourself; add_field is the only place that touches it, and it forces the control to full width of its column with the label replaced by a hard space.

## values

markup: `<div class="page-form row hide">` prepended into `.layout-main-section`
per control: `col-md-2` on the wrapper, `input-xs` on the input, `title` and a hover tooltip from the label
only_input: true for every fieldtype except Check
registry key: `df.fieldname || df.label`
clear_fields: empties markup, keeps fields_dict
hide_form: adds `hide`, keeps everything

## how

The strip exists to carry a list view's filters, and it is shaped for that: one row, six slots, small inputs, no labels because the placeholder carries the name. A page that wants a filter bar gets that shape whether it wants it or not, and a page that wants a designed filter bar is undoing bootstrap classes rather than styling a blank element.

Two ways out. Build the controls into your own markup by passing a parent to add_field, and you still get `col-md-2` on the wrapper but not the row around it. Or take `page.page_form`, move it where the design wants it, and remove `row` and `col-md-2` once at build time — cheaper than a stylesheet that fights them, because the grid classes carry margins and widths at several breakpoints.

Whichever route, keep the strip out of any element the page empties on re-render, and remember that the registry outlives the markup: clear_fields is not a reset. Name every field explicitly so the registry key is stable — see [[app-page]].
