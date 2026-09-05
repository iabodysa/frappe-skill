---
name: document-page
description: The web view permission check is an or chain whose first term is allow_guest_to_view, so setting that Check on the DocType publishes every record with a route to everyone and the two permission calls after it are never reached.
triggers: ["DocumentPage", "can_render", "search_in_doctypes_with_web_view", "search_web_page_dynamic_routes", "_find_matching_document_webview", "get_condition_field", "get_html", "update_context", "allow_guest_to_view", "has_web_view", "is_published_field", "condition_field", "route", "get_doctypes_with_web_view", "website_generators", "cache_html", "can_cache", "redis_cache", "website_page", "get_web_template", "WebsiteGenerator", "is_website_published", "index_web_pages_for_search", "web view 404 not 403", "publish doctype to website", "all my records are visible to the public and i only wanted a few", "why can anyone on the internet open every row of this table", "my draft records leaked to the website", "the page says not found instead of access denied for an unpublished record", "i published the record but the link is still a 404", "why does it take an hour before a newly published page appears", "i changed the content but the website still shows the old version", "the page is stale in production but fine on my dev machine", "how do i show a record as a public page on the site", "the record has a url but nothing renders it", "why is my page not showing up in the site search or sitemap"]
product: frappe
---

# Document web page

## paths

frappe/website/page_renderers/document_page.py — DocumentPage, can_render, search_in_doctypes_with_web_view, search_web_page_dynamic_routes, get_condition_field, get_html, update_context, _find_matching_document_webview
frappe/website/router.py — get_doctypes_with_web_view, get_page_info_from_web_page_with_dynamic_routes
frappe/website/utils.py — cache_html, can_cache
frappe/website/website_generator.py — WebsiteGenerator, is_website_published, allow_website_search_indexing, send_indexing_request
frappe/core/doctype/doctype/doctype.json — allow_guest_to_view, has_web_view, is_published_field, index_web_pages_for_search
frappe/www/sitemap.py — allow_guest_to_view
frappe/search/website_search.py — allow_guest_to_view

## rules

MUST read `allow_guest_to_view` as the FIRST term of the web view permission check: search_in_doctypes_with_web_view returns true on that meta flag alone, and doc.has_permission and frappe.has_website_permission are evaluated only when it is unset.
NEVER set `allow_guest_to_view` on a DocType holding records that must not all be public; the flag is a property of the DocType and never of the record, so it publishes every row whose `route` matches a request.
MUST use the DocType's `is_published_field`, or the controller's `website.condition_field`, as the per-record switch, because get_condition_field turns that field into a filter on the route lookup.
MUST expect an unpublished record to answer 404 and not 403; the condition field is part of the lookup filter, so a record that fails it never matches a route and no renderer claims the path.
MUST expect the route-to-document lookup to be cached for an hour by route alone; _find_matching_document_webview carries redis_cache with a one-hour ttl and no user in its key, so a newly published or re-routed record can stay unreachable for that long.
MUST set `has_web_view` on the DocType, or name it in the `website_generators` hook, for get_doctypes_with_web_view to consider it at all.
MUST expect the rendered HTML to be cached per path and per language under the `website_page` hash; get_html carries cache_html, so a page whose content varies by user must set `no_cache` on its context.
MUST expect can_cache to return False under developer_mode and under `disable_website_cache`, so a page-cache defect does not reproduce on a development bench.
MUST expect the document's own `get_context` to run after the context already carries the document's fields and page info, so it can override any of them and must not assume they are absent.
MUST name a template on the context or on the DocType; update_context falls back to the meta's web template only when the context named none.
MUST expect the dynamic-route branch to answer true with NO permission check at all — search_web_page_dynamic_routes returns true on a match — so the route table alone decides that path.
MUST expect `allow_guest_to_view` to govern indexing as well: the sitemap skips a DocType without it, and the website search index requires it together with has_web_view and index_web_pages_for_search.

## values

can_render order: doctypes with a web view, then Web Pages with dynamic routes
web view permission check: allow_guest_to_view, else has_permission, else has_website_permission
dynamic route check: a route match, no permission call
DocType considered when: has_web_view is 1, or the DocType is named in the website_generators hook
route filter: route equals the path, plus the condition field equals 1 when there is one
condition field: is_published_field, else the controller's website.condition_field for a non-custom DocType
route lookup cache: redis_cache, one hour, keyed on the route
html cache: the website_page hash, keyed on path then language
html cache disabled by: no_cache on the context, disable_website_cache, developer_mode
search index filter: has_web_view 1, allow_guest_to_view 1, index_web_pages_for_search 1

## how

A DocType reaches the website in two steps and each has its own switch. `has_web_view` decides whether the DocType is searched for a route at all; the condition field decides which of its records carry a live route. Because the condition field is applied as a FILTER rather than as a check, an unpublished record is not refused — it is not found, and the request falls through to whatever renderer comes next. That is why a wrongly unpublished page reads as a missing page.

The permission check is the third step and it is ordered so the cheapest and broadest answer comes first. `allow_guest_to_view` is a Check on the DocType, so turning it on to make one page public makes every routed record of that DocType public at the same time, and the two per-record calls behind it stop running. Where only some records should be visible, the flag stays off and the answer comes from the document's own permission or from a website permission function.

Two caches sit on this path and neither knows about the user. The route lookup is memoised for an hour by route, so publishing is not immediate. The rendered HTML is stored per path and per language, so a template that renders anything session-specific will hand one user's page to the next unless the context sets `no_cache`. Both caches are off under developer_mode, which is precisely why this class of defect appears only after deployment.
