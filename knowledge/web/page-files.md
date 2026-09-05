---
name: page-files
description: TemplatePage walks the installed apps reversed so the last app installed wins a page file, and StaticPage walks them forward so frappe wins a binary asset at the same path.
triggers: ["TemplatePage.set_template_path", "can_render", "get_index_path_options", "get_start_folders", "PY_LOADER_SUFFIXES", "StaticPage.set_file_path", "is_valid_file_path", "UNSUPPORTED_STATIC_PAGE_TYPES", "is_binary_file", "cache_html", "can_cache", "Invalid Sidebar JSON at", "www page file resolution order", "which app's page file wins", "i put my own version of the page in my app but the old one still shows", "my replacement image is ignored and the original one keeps loading", "why does my override work for the text page but not for the picture", "the stylesheet i dropped into the web folder returns not found", "a plain text file in the web folder is never served", "why can i not download a file i placed in the web folder", "the page still shows the old content after i edited the file", "my edits only appear after i restart everything", "why is a stale version of the page being served to visitors", "my new page returns not found even though the file is in the right folder", "how do i make a folder answer a url instead of a single file", "how do i keep a shared snippet from becoming its own address"]
product: frappe
---

# Page files

## paths

frappe/website/page_renderers/template_page.py — TemplatePage.set_template_path, can_render, get_index_path_options, get_start_folders, PY_LOADER_SUFFIXES
frappe/website/page_renderers/static_page.py — StaticPage.set_file_path, can_render, is_valid_file_path, UNSUPPORTED_STATIC_PAGE_TYPES
frappe/website/utils.py — is_binary_file, cache_html, can_cache

## rules

MUST put a page that replaces a stock one at the same path under your app's `www/`; the reversed walk hands it to the app installed after frappe.
NEVER expect that to work for a binary asset under `www/`. StaticPage stops at the first installed app holding the path, frappe is first, and the only fix is a different filename.
MUST expect StaticPage to serve a file only when it is binary and its extension is outside the refused list, so a `.css`, `.js`, `.json`, `.txt` or `.xml` file placed in `www/` is never served as a file.
NEVER give a page file a Python import suffix; can_render refuses a template_path ending in one and the route falls through to the next renderer.
MUST expect the same path to be searched under `templates/pages` as well as `www` in every app.
MUST expect a directory route to resolve through `index.html` or `index.md` inside it.
MUST set `developer_mode` while editing a page file, or clear the `website_page` cache; a rendered page is cached per path and per language and can_cache answers false only for developer_mode, disable_website_cache, or a page that set no_cache.

## values

folders searched per app: www, templates/pages
names tried per path: the path itself, .html, .md, /index.html, /index.md
template page order: installed apps reversed — the last installed app wins
static page order: installed apps forward — frappe wins
static page refuses: css, html, js, json, md, py, pyc, pyo, txt, xml
static page requires: the file is binary and resolves inside the app's www directory
render cache: website_page, hashed by path, then keyed by language

## how

Two renderers read the same folder with opposite precedence, and that is the whole of it. A template
is meant to be overridden, so the search runs from the newest app back to frappe. A static file is
served straight off disk, so the search runs from frappe forward and your app never gets asked. The
question to hold is not "is my file there" but "which app's copy of this path answers", and the two
answers differ for text and for binary content at the same path.

Choose the folder by what the file is. A file under `www` is a route — its path is the URL. Anything
under `templates/pages` behaves the same way, and is the older home for the same thing. A partial that
must never own a URL belongs in `templates/` instead, where no renderer searches it.

A page you cannot reach is either shadowed by an earlier renderer or served out of the render cache.
Turn developer_mode on before concluding anything about a page file, because the cache answers with
the previous render and reports nothing.
