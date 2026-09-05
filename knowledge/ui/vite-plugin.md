---
name: vite-plugin
description: An empty frappeui call already installs four sub-plugins plus a banner and a dependency pre-bundle, so it rewrites the build output directory unless the option carries the value through.
triggers: ["frappeuiPlugin", "lucideIcons", "frappeProxy", "jinjaBootData", "buildConfig", "siteBanner", "frappeTypes", "frappeui vite plugin build output", "frappe-ui vite config", "my build files end up in a folder i did not ask for", "why did the output directory change after i added the plugin", "the built page is blank and the assets point at the wrong path", "i set my own output folder and it got ignored", "the dev server keeps forwarding requests to a backend i did not configure", "my existing page template gets overwritten by a generated one", "why is extra data injected into my html that i never added", "adding it with no options changed my whole build", "how do i turn off the proxy and keep serving from my own template", "the generated html lands somewhere my server does not look", "how do i keep my own build settings when i add this"]
product: frappe-ui
---

# The Vite plugin

## paths

vite/index.js — frappeuiPlugin
vite/lucideIcons.js — lucideIcons
vite/frappeProxy.js — frappeProxy
vite/jinjaBootData.js — jinjaBootData
vite/buildConfig.js — buildConfig
vite/siteBanner.js — siteBanner
vite/frappeTypes.js — frappeTypes

## rules

MUST expect four options to default to on — the lucide icons, the backend proxy, the Jinja boot data injection and the build configuration — so an empty call is not a neutral call.
MUST expect the types plugin to run only when its option is passed.
MUST expect the site banner to be added on its own, and a dependency pre-bundle plugin to be pushed unconditionally.
MUST expect `frontendRoute` not to be a plugin: it is threaded into the banner and into the build configuration and defined for the client.
MUST pass an application's own output directory through the build configuration option, or disable that option, because the plugin otherwise decides the output directory and the emitted HTML path.
MUST disable the Jinja boot data and the proxy for a portal served from an existing template rather than from the plugin's generated one.
MUST expect an object passed in place of `true` to be handed to the sub-plugin as its options.

## values

default on: lucideIcons, frappeProxy, jinjaBootData, buildConfig
opt in: frappeTypes
always added: siteBanner, the dependency pre-bundle plugin
threaded: frontendRoute into siteBanner and buildConfig, and defined for the client
buildConfig decides: the output directory, the emitted HTML path, the base url

## how

Read the call as a set of defaults rather than as a list of opt-ins. Naming the plugin with no options opts into a development proxy to the bench backend, an injection into the HTML, and a rewrite of where the build lands — which is right for an application generated from the frappe-ui template and wrong for one grafted onto an existing site.

So the decision is per option, and the value carries through: an object where `true` would go configures the sub-plugin rather than replacing it. Passing the application's own output directory through the build option keeps both the plugin's HTML path handling and the directory the application wanted.
