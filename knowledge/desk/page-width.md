---
name: page-width
description: A Desk Page's own body element carries the bootstrap class container, so it is centred and capped at 1290px by the page's own markup rather than by anything above it, and the only opt-out the page controls is the class full-width on that same element.
triggers: ["page-body", "page-container", "container page-body", "full-width", "$container-max-widths", "container-max-widths", "1290px", "page.container", "toggle_full_width", "set_fullwidth_if_enabled", "container_fullwidth", "navbar-toggle-full-width", "media-breakpoint-up", "main-section", "desk page looks narrow", "desk page is centred with white space either side", "make a desk page full bleed", "page does not fill the screen", "page width cap", "widen a desk page", "why is my page not using the whole screen", "my screen is huge but the content sits in a skinny column in the middle", "there is a big empty margin on both sides of the page and i cannot get rid of it", "why does my page stop growing after a certain width", "the content refuses to stretch on a wide monitor", "how do i let a screen use the entire window instead of a narrow strip", "i widened the wrapper above it and nothing changed at all", "the title bar stayed narrow while the content underneath went wide", "the header and the body no longer line up after i widened one of them", "the same screen looks wide on my machine and narrow on my colleague's", "one user sees the full screen and another sees it squeezed same version", "why does the layout change when i log in on a different browser", "how do i stop the layout from being centred and capped"]
product: frappe
---

# Page width

## paths

frappe/public/js/frappe/ui/page.html — container page-body, page-head
frappe/public/js/frappe/ui/page.js — Page.make
frappe/public/scss/desk/variables.scss — $container-max-widths
frappe/public/scss/desk/page.scss — .page-body.full-width
frappe/public/scss/desk/global.scss — full-width
frappe/public/js/frappe/ui/toolbar/toolbar.js — toggle_full_width, set_fullwidth_if_enabled
frappe/public/js/frappe/views/container.js — add_page
frappe/www/app.html — main-section
frappe/public/js/frappe/views/kanban/kanban_view.js — full-width

## rules

MUST read the width cap as coming from the page's OWN markup: the template gives the body element the classes `container page-body`, so the cap is inside the page and cannot be escaped by restyling an ancestor.
NEVER look for a bootstrap container in the desk shell; the shell renders `.main-section > #body` and nothing else, and the container the page shows up inside was written by the page template two levels down.
MUST expect the cap to be 1290px on a wide screen, because the desk redeclares `$container-max-widths` before it compiles bootstrap and pins the extra-large breakpoint there.
MUST reach a full-bleed page by adding `full-width` to the element the page object calls `container`, which is the `.page-body` node; that is the class the desk's own stylesheet answers with width and max-width at 100%, and it is what the kanban view uses.
NEVER confuse that with the `full-width` the navbar toggles: that one lands on `document.body`, applies to EVERY container on the screen including the page head's, sets width to 90% rather than 100%, and only above the medium breakpoint.
MUST read the navbar's version as a per-browser preference the page cannot rely on; it is stored in `localStorage.container_fullwidth` and reapplied at boot, so one operator sees a wide page and the next sees a narrow one from the same deploy.
MUST widen the page head separately when the body is widened, because the head is a second `container` element in the same template and the class on the body does not reach it.
NEVER read the container element the page-view creates as the cap; it carries the classes `content page-container` and holds the head and the body, and it sets a background colour and nothing about width.

## values

markup: `.main-section > #body > .content.page-container > .page-head > .container` and `> .container.page-body`
cap: sm 540px, md 840px, lg 1090px, xl 1290px
page opt-out: `full-width` on `.page-body` — width 100%, max-width 100%
navbar opt-out: `full-width` on `body` — every `.container` to width 90%, max-width 100%, at md and up
navbar opt-out is stored in: `localStorage.container_fullwidth`

## how

Nothing above the page constrains it. The desk shell is a bare `#body` div, the page-view wraps each route in a `content page-container` div that only paints a background, and the width cap arrives with the page template itself, which spells its body `<div class="container page-body">`. So a page built to fill the viewport is not fighting the desk; it is fighting one class in its own wrapper.

Add `full-width` to `page.container` in `on_page_load` and the desk's own rule releases the body to the full width. The head keeps its own container and stays capped, which looks deliberate on a page whose head is a title and a few buttons and looks broken on a page whose head carries a toolbar the body must line up with; widen both or neither.

The navbar item of the same name is a different mechanism with a colliding name. It sets the class on `body`, which the global stylesheet answers by taking every `.container` to 90%, and it remembers the choice in the browser rather than on the user record. A page that looks right only because an operator turned that on will look wrong on the next machine.
