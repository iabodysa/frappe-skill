---
name: toast
description: toast.create fills a module-level array that only the provider component renders, and the plugin install registers no component at all.
triggers: ["ToastRoot", "duration", "ToastProvider", "install", "toast.create not showing", "frappe-ui toast plugin", "nothing pops up when i show a message", "my success message never appears anywhere on the screen", "why do my notifications silently do nothing", "the popup message disappears instantly instead of staying", "i set the time to zero and the message vanished right away", "my message shows but all the formatting is gone", "links inside my notification get stripped out", "the loading message never turns into a success message", "how do i make a message stay until the user closes it", "the whole thing still crashes even though i showed an error message"]
product: frappe-ui
---

# Toast

## paths

src/components/Toast/index.ts — toast, create, remove, removeAll, promise, success, error, warning, info, Toasts
src/components/Toast/Toast.vue — ToastRoot, duration
src/components/Toast/ToastProvider.vue — ToastProvider
src/components/Provider/FrappeUIProvider.vue — ToastProvider
src/index.ts — Toast, toast, FrappeUIProvider
src/utils/plugin.js — install

## rules

MUST expect `toast.create` to push a row onto a module-level ref and to return an id, and to raise nothing when no renderer is mounted.
MUST expect that array to be read by exactly one component, declared in the same file and absent from the package's exports.
MUST wrap the application in `FrappeUIProvider` for a toast to appear, since it is the only place that component is mounted.
NEVER expect the plugin install to register a component: it installs the resources plugin and sets the call and socket properties, and does nothing else.
MUST expect the message to pass through the sanitizer with an allow-list of a, em, strong, i, b and u, so any other tag is dropped and nothing reports it.
MUST pass `duration` in seconds, since the helper multiplies by 1000 and falls back to 5000 milliseconds only when the option is absent — passing 0 yields a zero duration rather than the default.
MUST keep `closable` true for the duration to reach the underlying component, since the template forces the duration to 0 when it is false.
MUST expect `toast.promise` to hold its loading toast open with a zero duration, to overwrite that same row on settle, and to re-throw the original error after writing the error toast.

## values

state: a module-level ref of toast rows
id: `toast-<counter>`, or the id passed in the options
renderer: the toasts component, mounted only by the provider
exported: the toast component and the toast object; the renderer is not
allowed tags: a, em, strong, i, b, u
duration unit: seconds in, milliseconds stored
duration default: 5000 milliseconds, only when the option is absent
closable default: true
types: info, success, error, warning

## how

The call and the rendering are deliberately separate: any module can raise a toast without a component reference, because the state is module-level. The price is that a missing provider is indistinguishable from a missing call — the row is created, the id comes back, and nothing appears. When toasts do not show, check the root component before checking the call.

The duration options interact, so read them together. Seconds in, milliseconds stored, zero meaning zero, and a non-closable toast having its duration forced to zero regardless of what was passed. Read a toast that never dismisses as a `closable: false` somewhere, not as a duration that was ignored.
