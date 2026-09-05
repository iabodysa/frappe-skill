---
name: realtime
description: Every onDocUpdate call adds a list_update listener that nothing removes, while the subscribe dedup is keyed on doctype alone and ignores which socket asked.
triggers: ["createDocumentResource", "createListResource", "initSocket", "install", "socket updates repeat", "onDocUpdate listener not removed", "the same list reloads five times every time one record changes", "why does my page fetch the same data over and over after a live update", "the network tab is flooded with duplicate requests whenever someone edits a record", "requests keep firing for a page i already navigated away from", "the app gets slower the more times i open and close the same screen", "how do i stop background refreshes coming from a screen that is already closed", "the list never updates when someone else changes a record", "live updates worked on the first load and stopped after part of the app reloaded", "why do i get no live updates and no error either", "two browser tabs open and only one of them gets live updates"]
product: frappe-ui
---

# onDocUpdate

## paths

src/resources/realtime.ts — onDocUpdate, subscribe, subscribed
src/resources/documentResource.js — createDocumentResource
src/resources/listResource.js — createListResource
src/utils/socketio.js — initSocket
src/utils/plugin.js — install

## rules

MUST expect `onDocUpdate` to call `socket.on('list_update', ...)` on every invocation, with no check and no matching removal, and MUST expect the file to export nothing that unsubscribes.
MUST expect a resource built with `realtime` to call it once per construction, so each rebuild of the same logical resource adds one more live listener bound to the shared socket.
MUST expect one realtime update to trigger the resource's refetch once per accumulated listener, and MUST expect those listeners to keep firing for the life of the socket after the component is gone.
MUST give a realtime resource a stable `cache` key so the constructor returns the cached object instead of building another.
MUST expect `subscribed` to be one module-level object keyed on doctype alone, checked before the `doctype_subscribe` emit and never cleared.
MUST expect a second socket asking for a doctype already marked to skip that emit, so the server's room membership stays with the first socket and the new socket's listener never fires.
NEVER create a second socket for a page that has already subscribed a doctype — a second plugin install, an application remount, or replacing the socket by hand.
MUST read a resource that never refetches on a realtime update as a lost room join rather than as a missing listener, because the listener is registered either way and nothing reports the skip.

## values

event: `list_update`, matched on the payload's doctype
callback argument: the document name
emit: `doctype_subscribe` with the doctype
dedup map: `subscribed`, module-level, keyed on doctype, ignores the socket
removal: none

## how

Registration and subscription are two steps and only one of them is deduplicated, which is exactly backwards. Repeating the subscription would be harmless; repeating the listener is what multiplies the refetches. So the cost grows with how often the resource is rebuilt, and the fix belongs at construction — a stable cache key — rather than at teardown, because there is no teardown to write.

The second failure is the mirror of the first. The flag says a doctype is subscribed when what it means is that some socket once subscribed it, so replacing the socket produces a page that listens perfectly to a room it never joined and reports nothing at all.
