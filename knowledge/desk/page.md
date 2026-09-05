---
name: page
description: A Desk Page serves the .js and .css sitting beside its module file with no hooks entry and no build, and its style is appended to head and never removed.
triggers: ["Page DocType", "Page.load_assets", "desk_page.get", "desk_page.getpage", "render_include", "safe_decode", "Page.is_permitted", "frappe.dom.set_style", "pageview set_style", "Page Has Role", "page roles", "Not in Developer Mode", "Only Administrator can edit", "desk page js and css files", "page js file beside the page record", "desk page stylesheet leaks into other screens", "who can open a desk page", "get_module_path", "get_module_app", "modules.txt", "module folder", "where does a desk page live on disk", "where is my page on the server", "page folder path", "path to a desk page in an app", "find the page directory", "No such file or directory when copying a page", "i changed the script for this screen and the browser still runs the old one", "i copied the files to the server and the screen behaves as if nothing shipped", "where on the server do the files for this screen actually live", "the folder i expected is not there and the copy failed with no such file", "i moved this screen to another module and it stopped loading its script", "my styling for one screen is bleeding into every other screen in the app", "after i visit that screen once the rest of the app looks wrong until i reload", "why do my styles stay active after i navigate away", "i shipped the script but forgot the stylesheet and nobody warned me", "the deploy said success but one of the two files never arrived", "a user with no roles at all can open this screen how do i lock it down", "an anonymous visitor reached an internal screen is that expected"]
product: frappe
---

# Desk Page

## paths

frappe/core/doctype/page/page.py — Page.load_assets, render_include, safe_decode, is_permitted
frappe/desk/desk_page.py — get, getpage
frappe/public/js/frappe/dom.js — frappe.dom.set_style
frappe/public/js/frappe/views/pageview.js — set_style
frappe/core/doctype/page/page.json — roles
frappe/__init__.py — get_module_path, get_pymodule_path, scrub
frappe/modules/utils.py — get_module_app

## rules

MUST resolve the page's folder as `<app>/<scrub(module)>/page/<scrub(page name)>/`, because load_assets joins the module path with `page` and the scrubbed page name; the folder never sits under the app repository root and never under the app's public folder.
MUST read the record's `module` field, and never the directory the files happen to sit in, as what decides where the server looks; moving a page to another module moves the folder the server reads and leaves the old files unread and unreported.
MUST list that module in the app's `modules.txt`, because the module is resolved to an app through the map built from that file alone; a module missing from it raises a DoesNotExistError naming the module and not the page.
NEVER guess the folder on a server before writing to it. A module named after its own app sits three segments deep — `apps/<app>/<app>/<app>/page/<page>/` — so a backup or a copy aimed one level up finds nothing and reports only a missing directory; run a read-only search for the folder first and write to what it names.
MUST name the sibling file after the scrubbed page name — `<page>.js` and `<page>.css` in the page folder — because its presence is what loads it; there is no hooks entry, no bundle and no build step.
NEVER style a Desk Page through app_include_css, which loads the file on every Desk route, and NEVER through an inline style element.
MUST read the script and the style as re-read from disk on every load, so a stale desk page is never a server cache and clearing the cache changes nothing about it.
MUST deploy `<page>.js` and `<page>.css` as ONE unit, because the same call reads both and writes the style only when its file is present, so shipping one half serves the new script under the old style with nothing raised.
MUST verify a deployed page by comparing each file the page loads against the local copy, and NEVER by the exit status of whatever carried it, because a transport that drops a file can still exit clean.
MUST carry a second module through the app's public folder and `frappe.require` rather than the include directive, because the hook route and the folder route both pass their javascript through render_include and only the public folder leaves the file whole; see [[require]].
MUST read a file named by the `page_js` hook as passing through render_include too, so a directive inside a hooked file is expanded there as well and a hooked file with no directive is returned unchanged; the hook itself is settled in [[page-js-hook]].
NEVER write a Jinja include in `<page>.css`; load_assets passes the stylesheet through safe_decode alone and only `<page>.js` goes through render_include.
MUST put each `{% include "app/app_relative/path.js" %}` in `<page>.js` on its own line with one space each side of the quoted path and a lower-case underscored filename, because the include pattern matches nothing else and the path is slugified before the file is opened.
MUST mark an `.html` sibling with `<!-- jinja -->` to have it rendered server-side through a get_context in the page module; without the marker it is compiled as a JS template.
MUST scope every rule in a Page stylesheet under a root the page owns, because set_style appends the style element to head and pageview.js passes no id, so the rules outlive the route for the life of the tab.
NEVER write a bare element or utility selector in a Page stylesheet; the Desk is a single-page application and no document reload clears head.
MUST search the bundled assets for a class prefix before adopting it — `fc-` belongs to FullCalendar, which Frappe bundles.
MUST pass an id to frappe.dom.set_style to make the style element replaceable, because only its `if (id)` branch removes the previous one.
MUST read a missing `<page>.js` as an empty script, because load_assets clears the script field before it looks for the file, while it leaves the style field alone and the record's own style survives.
MUST confirm the file is loaded by renaming it and watching the served asset go empty.
MUST add a role to the Page's Has Role table or a custom allowed role to keep it out of a Guest's reach, because getpage is `@frappe.whitelist(allow_guest=True)` and is_permitted returns True whenever both lists are empty.

## values

script sibling: `<page>.js`, read through render_include, with a sourceURL comment appended
style sibling: `<page>.css`, read through safe_decode
template sibling: any `.html` in the folder, compiled as a JS template
server-rendered template: an `.html` containing `<!-- jinja -->`, rendered through get_context in the page module
set_style with no id: appends, never removes
set_style with an id: removes the element of that id, then appends
is_permitted with no Has Role row and no custom allowed role: True, for every caller including Guest

## how

The Page DocType has two ways in and they do not behave alike. Every read through desk_page.get runs load_assets, which clears the script field and then fills it only from `<page>.js`, so the folder always wins the script and an absent file means no script at all. The style field is not cleared, so `<page>.css` overrides it and the record's own value survives when the file is missing. Put the file in the folder and the question does not arise.

The style leak is a property of the appending call, not of the CSS. Each visit adds another style element to head, navigating away leaves it, and returning adds a second copy of the same rules. Scoping under a root the page owns stops the damage but not the append; passing an id stops the append but pageview.js does not pass one. So the durable answer for anything reused is a file in `public/css` loaded through app_include_css, which is versioned and loads once, and the `style` field is for what genuinely belongs to one page.

The failure this produces is diagnosed on the wrong screen. A rule written as `.card { padding: 0 }` on one page reaches every `.card` on every list view, form and report visited after it, so the code being read when the defect appears is innocent. Ask which page was visited first, not what the broken screen does.

getpage is the endpoint desk_page.get exposes and it carries allow_guest=True, so the route itself never turns an anonymous caller away. What turns them away is is_permitted, which builds one allowed list from the Page's Has Role table plus any custom allowed roles and returns True the moment that list is empty, before it ever calls frappe.get_roles(). A Page left without a role row is not access-controlled by allow_guest at all; it is open to anyone who can reach the route, Guest included.
