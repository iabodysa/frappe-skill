---
name: render-include
description: The include directive is matched by one regex that allows exactly one whitespace character on each side of the quoted path and nothing between the quote and the path, and the path is slugified before the file is opened, so a capital letter or a hyphen in a filename resolves to a name that does not exist.
triggers: ["render_include", "INCLUDE_DIRECTIVE_PATTERN", "InvalidIncludePath", "Invalid include path", "Security Error: The Path provided is not safe.", "get_app_path", "get_pymodule_path", "scrub", "cstr", "{% include %}", "include a js file in a desk page", "split a page script", "share javascript between desk pages", "include path not found", "page js include", "bad escape", "re.error", "empty page script", "page script comes back empty", "backslash in an included js file", "regex literal in an included file", "my page script is completely blank in the browser but the styles still load", "why did my whole page javascript disappear after i pulled in another file", "the shared bit of javascript i pasted in never runs on the page", "i keep getting an error saying the include path is invalid and it does not tell me which one", "what is wrong with my include line it looks exactly right to me", "renaming the file to lowercase did not help and it still cannot find it", "the file is right there on disk but the page insists it does not exist", "why does a dash in my filename break loading it", "i put two of these on the same line and now it looks for a path nobody wrote", "the directive text is printed out as plain text in my stylesheet instead of doing anything", "adding a regular expression to the shared file blows up the page", "how do i split one huge page script into smaller files"]
product: frappe
---

# Render Include

## paths

frappe/model/utils/__init__.py — render_include, INCLUDE_DIRECTIVE_PATTERN, InvalidIncludePath
frappe/__init__.py — get_app_path, get_pymodule_path, get_module, scrub
frappe/core/doctype/page/page.py — Page.load_assets

## rules

MUST write the directive with exactly one whitespace character after `include` and exactly one before `%}` — `{% include "app/app_relative/path.js" %}` — because the pattern spells both as a single `\s` and matches neither two spaces nor none.
NEVER put a space between the quote and the path; the pattern opens the capture at the quote and a leading space becomes part of the path it tries to open.
NEVER put two directives on one line, because the capture is greedy and stops only at the last quote on that line, so the two collapse into one path that names no file; put each directive on its own line.
MUST write the path in lower case with underscores and never with a capital letter or a hyphen, because every join part goes through scrub before the file is opened and scrub lower-cases the string and turns each hyphen into an underscore.
MUST split the path on the first `/` into the app name and a path relative to the app package, because that is the split render_include performs before it resolves anything.
MUST keep the include chain under five levels; the expansion loop runs five passes and returns whatever is left, so a sixth level is emitted into the served script as literal directive text with no error.
MUST read a `{% include` that the pattern does not match as a thrown InvalidIncludePath rather than as a skipped directive, because the loop throws the moment the marker is present and the findall is empty.
NEVER reach outside the app with `..`; the resolved realpath is required to start with the app root, and anything else throws a security error before the file is read.
An included `.html` file was historically compiled to a JS template; this function has been removed from the current release.
NEVER rely on the backslash doubling below version 15.44.2, because every release before it substitutes the included text raw and the substitution argument is a replacement template rather than a literal.
NEVER put a backslash escape — a regex literal, a `\\n`, a `\\.` — in an included file while the release substitutes raw, because the escape is read as a template reference and raises rather than landing in the script.
MUST read an empty page script with a working stylesheet as this failure rather than as a missing file, because the error is raised after the include is read and the whole script is lost, not the included part alone.
MUST move the shared javascript to the app's public folder and load it with frappe.require rather than repair the escape, below 15.44.2; see [[require]].
NEVER write a directive in a Page stylesheet; only the page script is passed through render_include, so a stylesheet cannot be split this way and the directive text is served as CSS.

## values

pattern: `{% include\s['"](.*)['"]\s%}`
whitespace allowed each side: exactly one character, space or tab
quote: single or double, and the two ends need not agree
path capture: greedy to the last quote on the line
passes: 5, then the loop returns
loop exit: no `{% include` substring remains
marker present and no match: InvalidIncludePath, "Invalid include path"
resolved path outside the app root: "Security Error: The Path provided is not safe."
path transform before open: split on the first `/`, then scrub on the app-relative part
scrub: space to underscore, hyphen to underscore, lower case
substitution: a regex sub keyed on the captured path
substitution argument: a replacement template, never a literal
included text, 15.44.2 and above: every backslash doubled before substitution, and the resolved realpath required to start with the app root
included text, below 15.44.2: passed raw, with no containment check
first release carrying the doubling: 15.44.2
raw substitution meeting a backslash escape: `re.error: bad escape`, and the served page script is empty
`.html` include: removed in current release
carrier: the page script only

## how

Two rules decide whether a directive works and neither is visible in the directive itself. The first is the pattern, which is stricter than a Jinja tag looks — one whitespace character on each side, nothing between quote and path — so a directive that reads correctly to a person can fail to match. Failing to match is not silence: the loop tests for the substring `{% include` first, so an unmatched directive throws rather than passing through, and the message names the path as invalid without naming which one.

The second is the slugification. The app-relative part of every path is passed through the same function that turns `Sales Order` into `sales_order`, and it runs on the whole path string, filename included. So a file genuinely named `MyWidget-v2.js` is looked for as `mywidget_v2.js`. On a case-insensitive file system the capital survives the lookup and the hyphen does not, which produces the confusing half-failure where renaming the file to lower case changes nothing and only removing the hyphen fixes it. Name every included file the way the framework will ask for it and the transform stops mattering.

The greedy capture is the trap that produces a nonsense path from two correct directives. `(.*)` runs to the last quote on the line, so two directives sharing a line yield one captured string containing the closing of the first, the opening of the second, and the tag text between them. The split then hands that whole string to the resolver, which fails on a path nobody wrote. Nothing in the error points at the line having two tags.

The five-pass cap is a quiet ceiling rather than an error. Each pass expands whatever directives are present, and included files may carry their own; on the sixth level the loop has already returned and the unexpanded text is served as part of the script, where it is a syntax error in the browser rather than a framework message on the server.

The backslash is the trap that has no message a reader can act on. The substitution argument is a replacement template, so a backslash in the included file is read as a reference rather than as text. From 15.44.2 the function doubles every backslash first and the problem does not exist. Below that version it does not, and a single regex literal in the included file is enough to raise before the substitution completes. What the operator sees is a page whose stylesheet arrived and whose script is empty, which reads as a missing file rather than as a raised error, so the search goes to permissions and file names and never to the escape. Read the site's version before splitting a page script, and below 15.44.2 carry the second file in the app's public folder instead.
