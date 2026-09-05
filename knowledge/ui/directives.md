---
name: directives
description: Neither directive defines an update hook, so the callback captured at mount keeps running after a re-render passes a new function.
triggers: ["vue directive stale closure", "v-on-outside-click not updating", "the click outside handler is using old values", "my handler keeps seeing the first item in the list", "why does the outside click callback have stale state", "the visible callback never fires", "nothing happens when the element scrolls into view", "how do i stop my callback from going stale after a re-render", "the callback fires with the wrong row inside a loop", "replacing the function on re-render has no effect", "the handler ignores my updated state", "why does clicking outside sometimes do nothing"]
product: frappe-ui
---

# The directives

## paths

src/directives/visibility.ts — beforeMount, unmounted
src/directives/onOutsideClick.ts — beforeMount, unmounted, onDocumentClick
src/directives/focus.ts — focus
src/index.ts — visibilityDirective, onOutsideClickDirective, focusDirective

## rules

MUST expect each directive object to implement `beforeMount` and `unmounted` and nothing else, so the binding is read once, in `beforeMount`, and no later render reaches it.
MUST expect the function captured in the first `beforeMount` to keep running for the element's whole lifetime, with whatever it closed over at that moment.
MUST bind a stable function identity — a method, or a handler held in a ref — and NEVER an inline arrow that closes over changing local state, inside a loop or across a props change.
MUST expect the visibility directive to do nothing at all when the binding is falsy at mount, since it returns before creating the observer.
MUST expect the visibility directive to report visible when the entry is intersecting and its ratio is above zero, and to observe on the next tick.
MUST expect the outside-click directive to attach one document click handler per element, to keep it in a module-level map, to remove any earlier handler for that element first, and to call back only when the event target is neither the element nor inside it.
MUST register them under the names the package exports.

## values

visibility hooks: beforeMount, unmounted
outside-click hooks: beforeMount, unmounted
missing hook: updated
visibility callback: the visible flag and the observer entry
outside-click callback: the click event
outside-click registry: a module-level map from element to handler
exported names: visibilityDirective, onOutsideClickDirective, focusDirective

## how

A directive without an update hook reads its binding once, at mount, so what the binding held when the element appeared is what runs forever. That is invisible in a static template and shows up the moment the expression is an arrow function, because a re-render creates a new closure that nothing reads and the old one keeps answering with stale state.

The rule that avoids it is about identity, not about the directive. Give the binding a value whose reference does not change between renders, and let that stable function read the reactive state when it fires.
