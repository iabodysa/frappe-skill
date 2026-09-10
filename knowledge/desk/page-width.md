---
name: page-width
description: A plain `.container { max-width: 100% }` rule in global.scss now overrides every bootstrap container breakpoint at once, so a Desk page is full width by default with no toggle needed; the old page-level full-width opt-out class carries no CSS rule any more, and the body-level full-width toggle only still matters for the 900px `--page-max-width` cap inside forms, trees and the workspace.
triggers: ["page-body", "page-container", "container page-body", "full-width", "$container-max-widths", "container-max-widths", "1290px", "page.container", "toggle_full_width", "set_fullwidth_if_enabled", "container_fullwidth", "navbar-toggle-full-width", "media-breakpoint-up", "main-section", "desk page looks narrow", "desk page is centred with white space either side", "make a desk page full bleed", "page does not fill the screen", "page width cap", "widen a desk page", "why is my page not using the whole screen", "my screen is huge but the content sits in a skinny column in the middle", "there is a big empty margin on both sides of the page and i cannot get rid of it", "why does my page stop growing after a certain width", "the content refuses to stretch on a wide monitor", "how do i let a screen use the entire window instead of a narrow strip", "i widened the wrapper above it and nothing changed at all", "the title bar stayed narrow while the content underneath went wide", "the header and the body no longer line up after i widened one of them", "the same screen looks wide on my machine and narrow on my colleague's", "one user sees the full screen and another sees it squeezed same version", "why does the layout change when i log in on a different browser", "how do i stop the layout from being centred and capped"]
product: frappe
---

# Page width

## paths

frappe/public/js/frappe/ui/page.html — container page-body, page-head
frappe/public/js/frappe/ui/page.js — Page.make
frappe/public/scss/desk/variables.scss — $container-max-widths
frappe/public/scss/desk/page.scss — page-container, page-body
frappe/public/scss/desk/global.scss — container
frappe/public/scss/common/css_variables.scss — page-max-width
frappe/public/scss/desk/form.scss — full-width, page-max-width
frappe/public/scss/desk/tree.scss — full-width, page-max-width
frappe/public/scss/desk/desktop.scss — full-width, page-max-width
frappe/public/js/frappe/ui/toolbar/toolbar.js — toggle_full_width, set_fullwidth_if_enabled
frappe/public/js/frappe/views/container.js — add_page
frappe/www/desk.html — main-section
frappe/public/js/frappe/views/kanban/kanban_view.js — full-width

## rules

NEVER read `$container-max-widths` (540/840/1090/1290) as a live cap; variables.scss still declares it and bootstrap still compiles breakpoint rules from it, but global.scss's own `.container { max-width: 100%; }` carries the same specificity and comes later in the cascade, so it wins and every `.container` element — the page body among them — renders at 100% regardless of screen width.
MUST read a Desk page as full width BY DEFAULT; nothing needs adding to reach it, and `.page-container .page-body { width: 100%; padding: 0; }` in page.scss reinforces the same result independently of the global override.
NEVER expect adding `full-width` to `page.container` (what kanban_view.js still does) to change anything; `.page-body.full-width` carries no rule in page.scss, so the class is inert there.
MUST read the navbar's `full-width` toggle as the one opt-out still wired to anything: `toggle_full_width`/`set_fullwidth_if_enabled` still add `full-width` to `document.body` and persist the choice in `localStorage.container_fullwidth`, unchanged from before.
MUST expect that toggle to matter only inside a form, a tree view or the workspace's main-section wrapper, where `body:not(.full-width)` gates `max-width: var(--page-max-width)` — 900px by default, in css_variables.scss; outside those three views the toggle changes nothing, because the generic page body is already unconditionally full width.
MUST widen the page head separately from the body only inside those same gated views; the head is a second `.container` element, and since the global override already frees `.container` from the breakpoint cap everywhere else, the head needs no separate treatment on an ordinary page.

## values

markup: `.main-section > #body > .content.page-container > .page-head > .container` and `> .container.page-body`
declared but overridden: sm 540px, md 840px, lg 1090px, xl 1290px ($container-max-widths, still compiled by bootstrap, still beaten by the plain override)
global override: `.container { max-width: 100%; }` in global.scss — no gating class, applies everywhere
page-level opt-out: gone; `.page-body.full-width` carries no rule
navbar opt-out: `full-width` on `body`, still live only where `body:not(.full-width)` gates `var(--page-max-width)` — form section head/body, tree node width, workspace main-section wrapper
--page-max-width: 900px (css_variables.scss)
navbar opt-out is stored in: `localStorage.container_fullwidth`

## how

Nothing constrains a Desk page any more. The page body still carries the bootstrap classes `container page-body`, and bootstrap still compiles the breakpoint max-widths from `$container-max-widths`, but global.scss's own `.container { max-width: 100%; }` sits later in the same cascade at the same specificity and wins outright, so every container-classed element renders edge to edge with no class to add and no toggle to flip. page.scss's separate `.page-container .page-body { width: 100%; }` rule reaches the same result a second, independent way.

The one surviving toggle is the navbar's, and it now guards a narrower thing than "the page." `toggle_full_width` still flips `full-width` on `document.body` and remembers the choice in `localStorage.container_fullwidth`, exactly as before, but the only rules left that read `body:not(.full-width)` are inside form.scss, tree.scss and desktop.scss, and what they gate is `var(--page-max-width)` — 900px — on a form's section layout, a tree's node width, and the workspace's main-section wrapper. Outside those three surfaces the toggle changes nothing, because there is no cap left there to lift.

kanban_view.js still calls `this.page.container.addClass("full-width")`, and it still runs without error, but it now adds a class with no matching CSS rule on that element — a page-level opt-out preserved in the JS after its stylesheet counterpart was removed.
