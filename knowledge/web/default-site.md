---
name: default-site
description: init_request resolves a request's site as _site or the X-Frappe-Site-Name header or the request host, so a bench serve started with default_site set pins every request to one site and the header is never read.
triggers: ["init_request", "serve", "app_group", "get_sites", "Invalid request arguments", "bench serve wrong site", "how does frappe pick the site for a request", "my login keeps failing even though the password is definitely right", "why is the server answering from a different site than the one i asked for", "the site header i send is being ignored completely", "i set the site in the request but it still uses the wrong one", "records i created are showing up on the wrong site", "how do i make the dev server use a specific site when there are several", "everything works on one site and breaks on the other with the same code", "the page loads fine but the data belongs to another company", "why does my script write to the wrong database on a multi site setup", "user exists but the app says invalid login on my local server"]
product: frappe
---

# Default site

## paths

frappe/app.py — init_request
frappe/commands/utils.py — serve
frappe/utils/bench_helper.py — app_group, get_sites

## rules

MUST read `_site` as beating the `X-Frappe-Site-Name` header, and the header as beating the request host, in init_request's site resolution.
MUST expect `bench serve` to fill `_site` from `context.sites[0]` whenever that list is non-empty, before any header reaches init_request.
MUST expect get_sites to resolve a site in order — the `--site` argument, the FRAPPE_SITE environment variable, then `default_site` from `common_site_config.json`.
MUST pass `--site` to `bench serve` on a bench holding more than one site, and MUST NOT rely on `X-Frappe-Site-Name` alone while `default_site` is set.
NEVER read a 200 response as proof that a site header was honoured; read the site back out of the served page instead.

## values

site source order: _site kwarg, X-Frappe-Site-Name header, request host
get_sites order: --site argument, FRAPPE_SITE env, common_site_config default_site
site proof on the served page: frappe.boot.sitename

## how

`bench serve` resolves its site before the WSGI app sees a single request, and once resolved that
site is fixed for the life of the process. A common config carrying `default_site` reaches
`get_sites` through the same path a bare `bench serve` takes with no `--site` and no FRAPPE_SITE
set, so `context.sites` is never empty and `_site` is always truthy — which means
`X-Frappe-Site-Name` is still read by init_request but discarded by the `or` chain the moment
`_site` already holds a value.

A client sending the header sees nothing wrong. A password rejected though it is correct, and a
capture or a scripted write that lands on the wrong site's rows, are both this: the server answered
from the pinned site while the header pointed somewhere else.
