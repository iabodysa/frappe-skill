---
name: zoom-pan
description: The wheel listener is bound once to whatever element containerRef already holds at mount, so a container rendered later never gets one and nothing rebinds when the ref changes.
triggers: ["useZoomPan", "containerRef", "isEnabled", "handleWheel", "handlePanStart", "zoomIn", "zoomOut", "resetZoom", "zoomLevel", "panPosition", "isMousePanning", "snapThresholdLower", "snapThresholdUpper", "frappe-ui zoom pan wheel listener", "wheel zoom does not work", "scrolling the wheel does not zoom at all and nothing errors", "why does wheel zoom stop working when the image loads later", "zoom works the first time and then never again after i swap the content", "the zoom buttons work but the mouse wheel does nothing", "i cannot drag the picture around after zooming in", "dragging keeps going after i let go of the mouse", "zooming out gets stuck and needs an extra click to go smaller", "the view jumps back to the middle on its own when i zoom out", "the page scrolls behind the viewer while i try to zoom", "how do i stop the wheel from zooming without breaking the rest", "why does the zoom land exactly on the default size instead of where i stopped"]
product: frappe-ui
---

# useZoomPan

## paths

src/composables/useZoomPan.ts — useZoomPan, containerRef, isEnabled, handleWheel, handlePanStart, zoomIn, zoomOut, resetZoom, zoomLevel, panPosition, isMousePanning, initialPanPositionOnGestureStart, snapThresholdLower, snapThresholdUpper
src/components/TextEditor/components/ImageViewerModal.vue — useZoomPan, imageContainer

## rules

MUST have `containerRef` already pointing at a mounted element when the composable's own mounted hook runs, because that hook reads the ref once and adds the `wheel` listener to that element and to nothing else.
NEVER put the container behind a `v-if` that is false at mount, and NEVER swap the element the ref holds; no watcher rebinds, so the wheel does nothing afterwards and no error is raised.
MUST call `useZoomPan` from the component that owns the container, since the listener is added in that component's mounted hook and removed in its unmounted hook.
NEVER look for a wheel handler in the returned object: `handleWheel` is not returned, so the mounted hook is the only binding.
MUST expect the listener to be registered with `capture: true` and `passive: false`, and to call `preventDefault` only when the container contains the event target, so a wheel over anything else keeps scrolling the page.
MUST expect `isEnabled` false to leave the listener attached and to return before `preventDefault`, so disabling restores page scrolling rather than removing anything.
MUST import it from `src/composables/useZoomPan`; the package entry exports neither this composable nor an index for the composables directory.
MUST expect wheel zoom to be continuous rather than stepped: it adds `-deltaY` times the damping factor, rounds, and clamps to 25 and 300.
MUST expect a wheel gesture that crosses 100 to land exactly on 100 whenever the distance from 100 is under one and a half times the requested change.
MUST expect `zoomOut` to stop at 100 on the step that would cross it, so a zoomed-in view needs one extra click before it goes under 100.
MUST expect the watcher to reset the pan to the origin whenever `zoomLevel` falls to 100 or below from above, and `handlePanStart` to return without starting a drag at 100 or below.
MUST expect `handlePanStart` to add `mousemove` and `mouseup` on `document` for the drag, and MUST end the drag before the component unmounts, because unmount only clears `isMousePanning` and the `mouseup` handler removes the pair only while that flag is still true — a drag interrupted by unmount leaves both document listeners for the life of the page.
NEVER read `snapThresholdLower` or `snapThresholdUpper` as the snap this composable applies; they are returned for the caller and no branch inside reads them.

## values

listener: `wheel` on `containerRef.value`, `capture: true`, `passive: false`
bound at: the composable's mounted hook, once
zoom bounds: 25 to 300
button step: 25
wheel damping: 0.2, and 0.5 while `ctrlKey` is held
snap: to 100 when the distance from 100 is under 1.5 times the requested change
returned: zoomLevel, panPosition, isMousePanning, initialPanPositionOnGestureStart, zoomIn, zoomOut, resetZoom, handlePanStart, snapThresholdLower, snapThresholdUpper
pan divisor: the current zoom over 100

## how

The composable owns the numbers and the caller owns the elements. Everything except the wheel is driven from the template — `handlePanStart` on the container, `zoomIn` and `zoomOut` on buttons, `zoomLevel` and `panPosition` on a transform. The wheel is the one exception, and it is wired inside on a single reading of the ref, which is why the whole feature does nothing at all when the container is not in the DOM at that instant.

Pan deltas are divided by the zoom factor, so `panPosition` is in unscaled content units and must be applied inside the same transform that applies the scale, not outside it.
