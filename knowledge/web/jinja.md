---
name: jinja
description: get_jenv builds the environment with no extensions argument, so a `{% comment %}` tag is an unknown tag and the template raises TemplateSyntaxError at parse time.
triggers: ["get_jenv", "FrappeSandboxedEnvironment", "get_jloader", "set_filters", "get_jinja_hooks", "UNSAFE_ATTRIBUTES", "get_safe_globals", "Illegal template", "Read-Only queries are allowed", "Query must be of SELECT or read-only WITH type.", "jinja template tag not found", "get_jenv extensions", "my whole page broke after i added a comment to the template", "one bad line in the template took down every page on the site", "why does a small template edit make the entire page fail to load", "part of my comment is showing up on the live page as visible text", "text i meant to hide is printing on the page", "why is my commented out block still rendering", "the variable name prints itself on the page instead of the value", "the page shows the raw braces instead of the actual value", "why does a misspelled variable not raise an error", "my custom helper is not available inside the template", "the helper works on a normal page but is missing when i render in the background", "how do i make my own function usable from a template", "the wrong app's copy of the template is being used"]
product: frappe
---

# Jinja

## paths

frappe/utils/jinja.py — get_jenv, FrappeSandboxedEnvironment, get_jloader, set_filters, get_jinja_hooks
frappe/utils/safe_exec.py — UNSAFE_ATTRIBUTES, get_safe_globals

## rules

MUST write a template comment as `{# … #}`, and NEVER write `#}` inside one; Jinja closes at the first one and the rest of the comment renders as visible text.
MUST render a template after changing it. A parse error takes the whole file down on every request, before any condition inside it is evaluated, so nothing that stops short of rendering the page sees it.
MUST register a template method or filter through the `jinja` hook, since get_jinja_hooks is the only source get_jenv reads for either.
MUST expect an app's template to take precedence over frappe's for an unprefixed template name; get_jloader orders the installed apps reversed, so frappe is searched last.
MUST address a specific app's copy of a template by prefixing it with the app name, which get_jloader registers alongside the unprefixed search.
NEVER set the `template_apps` hook to add an app; it replaces the whole app list, and an app missing from it loses every template.
MUST expect `format` and `format_map` to be callable on an object in a template and every other name in UNSAFE_ATTRIBUTES to be refused by is_safe_attribute.
MUST expect get_jinja_hooks to return nothing at all when there is no site on frappe.local, so a template rendered outside a site request loses every hooked method and filter.

## values

environment: FrappeSandboxedEnvironment, a Jinja SandboxedEnvironment subclass
extensions: none
undefined: DebugUndefined — an undefined name renders as its own placeholder rather than raising
loader: ChoiceLoader — a PrefixLoader keyed by app name, then one PackageLoader per app, apps reversed
globals: get_safe_globals, then the methods from the jinja hook
comment syntax: {# … #}

## how

The environment is sandboxed and bare. Every tag a template can use is the Jinja default set, so any
tag borrowed from another template language fails at parse time — the whole file, on every request,
not the branch it sits in. That failure mode is why a template change is not finished until the page
has been rendered once.

`DebugUndefined` is the other half of the same shape: a misspelled variable does not raise, it prints
itself into the page. So an unrendered template hides a syntax error and a rendered one hides a name
error, and the two need different checks — parse by loading it, names by reading the output.
