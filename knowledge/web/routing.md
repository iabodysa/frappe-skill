---
name: routing
description: A path is offered to the renderers in a fixed order and the first can_render that answers true takes it, so a published Web Form owns its route before any file at that path is looked at.
triggers: ["PathResolver.resolve", "get_custom_page_renderers", "resolve_path", "resolve_from_map", "get_website_rules", "get_response", "WebFormPage.can_render", "set_headers", "DocumentPage.can_render", "search_in_doctypes_with_web_view", "search_web_page_dynamic_routes", "get_page_info_from_web_form", "get_page_info_from_web_page_with_dynamic_routes", "get_published_web_forms", "Web Form", "You need to be in developer mode to edit a Standard Web Form", "Following fields are missing:", "Mandatory Information missing:", "frappe website routing order", "web form vs www page route conflict", "my page is never rendered even though the file is right there", "something else is answering the address i built this page for", "why does my url show a form instead of the page i wrote", "the address worked before i published the form and now it does not", "a record is taking over the url i wanted for my page", "the address still returns not found after i created the page", "how long does a missing address keep answering not found", "my own renderer is silently ignored and nothing is logged anywhere", "the page refuses to load inside a frame on another site", "how do i point one address at a different page", "why did changing the address handler break every other url on the site"]
product: frappe
---

# Routing

## paths

frappe/website/path_resolver.py — PathResolver.resolve, get_custom_page_renderers, resolve_path, resolve_from_map, get_website_rules
frappe/website/serve.py — get_response
frappe/website/page_renderers/web_form.py — WebFormPage.can_render, set_headers
frappe/website/page_renderers/document_page.py — DocumentPage.can_render, search_in_doctypes_with_web_view, search_web_page_dynamic_routes
frappe/website/router.py — get_page_info_from_web_form, get_page_info_from_web_page_with_dynamic_routes
frappe/website/doctype/web_form/web_form.py — get_published_web_forms

## rules

MUST read WebFormPage as ahead of TemplatePage. A published Web Form with route `careers` takes `/careers`, `/careers/list`, `/careers/new`, `/careers/<name>` and `/careers/<name>/edit`, and the `www/careers.html` in your app is never rendered.
MUST read DocumentPage as ahead of TemplatePage. A DocType with `has_web_view` holding a record whose `route` matches the path wins over a file at the same path.
MUST read `published` on a Web Form as the routing condition; get_page_info_from_web_form builds its rules from get_published_web_forms and from nothing else.
MUST give a class named in the `page_renderer` hook both `can_render` and `render`; get_custom_page_renderers drops a class missing either with a click.echo line and raises nothing.
NEVER add a `website_path_resolver` hook to change one route. It replaces resolve_path for every path, and the loop keeps only the last handler's return value.
MUST expect resolve_path to strip a trailing `.html`, map an empty path to `index`, map `index` to the Website Settings home page, then run `website_route_rules` and every `has_web_view` DocType route through resolve_from_map.
MUST clear the `website_404` cache after publishing a route that once answered 404; a URL held there returns NotFoundPage before any renderer is asked.
MUST fill `allowed_embedding_domains` on the Web Form to embed its page in an iframe; WebFormPage sends `Content-Security-Policy: frame-ancestors` from that field alone.
MUST expect DocumentPage to render a record only when its meta has `allow_guest_to_view`, or the session has document permission, or has_website_permission answers true.

## values

order: page_renderer hooks, StaticPage, WebFormPage, DocumentPage, TemplatePage, ListPage, PrintPage
fallback: NotFoundPage
short circuit: website_404 cache, keyed by the full request URL
website_route_rules: cached as website_route_rules, rebuilt on every request while dev_server is set
web form routes: /<route>, /<route>/list, /<route>/new, /<route>/<name>, /<route>/<name>/edit

## how

Resolution is a race, not a lookup. Every renderer is constructed in order and asked `can_render`,
and the first true answer ends the search — so a route is owned by whichever renderer sits earlier
in the list, and the loser is silent. When a page you wrote does not appear, ask which renderer took
the path before asking whether your file is found: a Web Form or a `has_web_view` record with the
same route is the usual answer, and neither logs that it won.

A `page_renderer` hook is the way to add a route the framework has no record for, because it is
asked before every stock renderer and it may refuse. `website_path_resolver` is not that tool; it
replaces the whole resolution for the site.

The path a renderer sees has already been rewritten. Write a route rule when the URL a user types
differs from the endpoint that renders, and read a DocType's `route` field as producing a rule of its
own the moment `has_web_view` is set.
