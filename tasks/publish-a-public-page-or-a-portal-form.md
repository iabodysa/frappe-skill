# Task — publish a public page or a portal form

## Which thing answers the route

What takes the path when more than one thing claims it?
MUST settle the route before writing the template, because the first renderer that can render takes it and a published Web Form or a DocType web view answers above any file at that path.
`knowledge/web/routing.md`

Two apps ship a file at the same path — which one is served?
MUST read a page file as won by the last app installed and a binary asset at the same path as won by the first.
`knowledge/web/page-files.md`

Which site is the request resolved to?
MUST remove the default site from the shared config when the host header has to choose the site.
`knowledge/bench/config.md`

Which of the three sources names the site the request is answered by?
MUST read the resolution order, because a default site pins every request and the site header is never reached.
`knowledge/web/default-site.md`

## What the page can return and render

Which statuses can the page produce?
MUST raise the exception that carries the status, because the status is picked from the exception class and every other one renders the error page.
`knowledge/web/status-codes.md`

Which Jinja tags are available?
MUST comment with the tag the environment was built with, because the environment is built with no extensions.
`knowledge/web/jinja.md`

Why did a number arrive as markup?
MUST ask the formatter for the inline form when the template needs a value rather than a block.
`knowledge/desk/formatters.md`

Which file does a page-builder block actually render?
MUST edit the `.html` beside the exported JSON for a standard Web Template, because the template field in the database is never read and clearing the standard check deletes that folder from the app.
`knowledge/web/web-template.md`

## The Web Form — which Check field gates what

What do the Check fields on the form actually do?
MUST place the restriction on one of the two that reach the write, and MUST NOT hide a Check with `depends_on` and read its stored value as cleared.
`knowledge/web/form-settings.md`

What stands between a Guest and a new document?
MUST set `login_required`, because the insert runs with permissions ignored and nothing else refuses.
`knowledge/web/form-permissions.md`

## What the submission writes

What happens to a declared field the payload leaves out?
MUST send every declared field on an edit, because a missing key is written as an empty string.
`knowledge/web/form-write.md`

## Who the visitor is

Which identity does the visitor hold?
MUST set the user type and read the session as the portal rail.
`knowledge/permission/portal_identity.md`

Where is the website permission hook consulted?
MUST NOT rely on it for an API call; it is read by the web view, the Web Form and the print view only.
`knowledge/permission/hooks.md`

What protects a Guest POST?
MUST authenticate the payload itself, because the session carries no CSRF token.
`knowledge/permission/csrf.md`

How is the route limited?
MUST accept that the limiter reads and writes the counter separately, so a burst passes.
`knowledge/job/rate-limiter.md`

## The page reads in another language

How is the app translated?
MUST follow the method before adding a string.
`references/frappe-translation-methodology.md`

Why is a string always English?
MUST use the lazy form at module level, because the plain call resolves the language when it runs and a module body runs at import.
`knowledge/bench/lazy.md`

Two rows in the CSV share one source — which wins?
MUST keep one row per key, because the file is read into a plain dict in file order.
`knowledge/bench/csv.md`

Which source wins a collision across the merged catalogues?
MUST expect country names to be applied last, and one failure to drop the three highest sources together.
`knowledge/bench/merge.md`

Why is the old translation still served after the file changed?
MUST make the compiled catalogue older than its source, because compilation is decided on timestamps.
`knowledge/bench/gettext.md`

## The page mails or notifies

Does mail leave this site?
MUST check the mute and the suspend flag, because a refused row keeps its unsent status and is picked up by every later flush.
`knowledge/job/email-queue.md`

Who receives the desk notification the page raises?
MUST expect a disabled user and one who switched notifications off to be dropped, and the failure never to reach the caller.
`knowledge/job/notification-log.md`

Which channel failure refuses the save?
MUST read a failure inside the channel as an error log and a failure either side of it as a refused save.
`knowledge/job/notification.md`
