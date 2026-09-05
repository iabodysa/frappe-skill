# Task — build a Vue front end on frappe-ui

## Wiring the build and the app shell

Which options does the Vite plugin turn on without being asked?
MUST read the plugin's defaults before adding a build option of your own.
`knowledge/ui/vite-plugin.md`

What has to wrap the app before a component works?
MUST mount the provider above every component that renders through it.
`knowledge/ui/toast.md`

## Choosing the data primitive and its cache key

What does a second construction on one cache key give back?
MUST make the key unique per set of options, because the first caller's object is returned and every later option is dropped in silence.
`knowledge/ui/create-resource.md`

Can a document resource follow a route parameter?
MUST construct a new resource when the name changes, because the doctype and the name are read once at construction.
`knowledge/ui/document-resource.md`

## Reading a list and paging it

What does the array hold after paging?
MUST read the data as a running list rather than a page window, because the fetch replaces it only at the start of the range.
`knowledge/ui/use-list.md`

What does a reload past the first page ask the server for?
MUST expect one request covering every loaded row, and MUST expect a row patch to reach every list built for that doctype whatever its filters.
`knowledge/ui/list-resource.md`

## Writing a document

What does a save put on the wire, and what does a failed write restore?
MUST send only what the server may receive, because every write snapshots and restores the whole document through one slot.
`knowledge/ui/document-resource.md`

What does the local document hold after a create?
MUST read the created document from what submit returned, because nothing is written back and a second submit creates a second record.
`knowledge/ui/use-new-doc.md`

## Sharing one document across components

What do two components on one name share?
MUST expect one ref per doctype and name, and MUST NOT hold the ref past the cache window, because it is deleted before it is returned.
`knowledge/ui/doc-store.md`

## Calling a method

What do two calls in flight at once share?
MUST serialise the calls, because each keeps one url ref per instance and the newer call takes the loading state.
`knowledge/ui/use-doctype.md`

Which params does a call use after a submit?
MUST reset the call before changing its params, and MUST NOT put a guard in the before-submit hook, because an error thrown there reaches no ref and stops nothing.
`knowledge/ui/use-call.md`

## Handling the error the server sends

What does a 2xx carrying an exception do?
MUST inspect the body for the exception, because the call resolves and the status on a thrown error is always undefined.
`knowledge/ui/frappe-request.md`

What happens after your own handler has run?
MUST catch the rejection as well as handle it, because the error is rethrown after the handler.
`knowledge/ui/create-resource.md`

## Offline and the local store

What does the local store fall back to?
MUST treat the fallback as empty after a reload.
`knowledge/ui/idb-store.md`

Which rejection escapes the store's own handler?
MUST attach a rejection handler outside it.
`knowledge/ui/idb-store.md`

## Live updates over the socket

What does each subscription call add?
MUST subscribe once, because every call adds a listener and none is removed, and the doctype map is global.
`knowledge/ui/realtime.md`

## Look, theme and dark mode

Which lever does a component's appearance expose?
MUST change the token, because the variant and size grid is fixed and an icon name is a class that renders nothing when wrong.
`knowledge/ui/button.md`, `knowledge/ui/lucide-icons.md`

What does the preset do to the Tailwind theme, and which roles read a variable?
MUST re-declare what the preset replaced, because it replaces the theme instead of extending it.
`knowledge/ui/tailwind-preset.md`, `knowledge/ui/theme.md`

What does dark mode wait for?
MUST write the theme attribute yourself, and MUST expect the composable never to unbind.
`knowledge/ui/theme.md`

What survives an update?
MUST keep the customisation on the surface the update does not overwrite.
`references/theming-what-survives-an-update.md`

## Directives that bind at mount

When is the callback captured?
MUST bind the final callback before mount, because it is captured once and the element the listener lands on is the one seen then.
`knowledge/ui/directives.md`

Which element does the zoom and pan listener land on?
MUST have the container in the ref at mount, because the listener binds once and nothing rebinds when the ref changes.
`knowledge/ui/zoom-pan.md`
