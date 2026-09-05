# The frappe-ui data layer — which call refetches

Six constructors reach the same server and the choice between them is not what you are fetching; it
is whether the IDENTITY you fetch changes while the component lives. The resources family —
`createResource`, `createListResource`, `createDocumentResource` — binds its url and identity at
construction and moves only when you call it. The data-fetching family — `useDoc`, `useList`,
`useCall` — takes the identity as a `MaybeRefOrGetter` and follows it.

| Constructor | Identity | What refetches it | What it will not do |
|---|---|---|---|
| `createResource` | fixed at construction | `fetch`, `reload`, `submit` | pick up new options under an existing cache key |
| `createListResource` | fixed at construction | `reload`, `next`, `previous` | swap a page — `next` grows one array |
| `createDocumentResource` | fixed at construction | `reload`, `setValue`, `save` | send only the changed fields on `save` |
| `useDoc` | a getter, followed | the getter changing, `setDoc` | keep one component's ref private from another on the same name |
| `useList` | a getter, followed | the getter changing | nothing beyond its own options |
| `useCall` | a getter, followed | `submit`, and `params` until reset | keep `submit` params out of the option params |

An `exc` on a 2xx response never throws, a thrown error's status is always undefined, and
`handleError` rethrows after `onError`, so a handled error still rejects `fetch`, `reload` and
`submit`.

## Settled by

| what it settles | leaf |
|---|---|
| the cache key that hands back the first caller's object and drops the later options | `knowledge/ui/create-resource.md` |
| the reload that re-asks for every loaded row, and the patch that reaches every list resource of that doctype | `knowledge/ui/list-resource.md` |
| the doctype and name read once at construction, and the whole document sent on a write | `knowledge/ui/document-resource.md` |
| the one ref a doctype and name share across every `useDoc` on the page | `knowledge/ui/doc-store.md` |
| the running list that appends on every start above zero | `knowledge/ui/use-list.md` |
| the params `submit` pins until they are reset | `knowledge/ui/use-call.md` |
| the url ref per instance, and the second submit that moves the loading state | `knowledge/ui/use-doctype.md` |
| the created document `submit` never writes back | `knowledge/ui/use-new-doc.md` |
| the `exc` on a 2xx body, and the status that is always undefined | `knowledge/ui/frappe-request.md` |
