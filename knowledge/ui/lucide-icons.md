---
name: lucide-icons
description: An icon is either a class name or an auto-imported component, a misspelt one renders an empty element in silence, and a name assembled at runtime emits no CSS at all.
triggers: ["matchComponents", "encodeSvgAsDataUri", "readAvailableIconNames", "lucideIcons", "generateIconModule", "getIcons", "camelToDash", "frappeuiPlugin", "iconLeft", "icon", "iconRight", "name", "lucide icon not rendering", "frappe-ui icon component", "the icon is just a blank space", "my icon does not show up and there is no error anywhere", "why is nothing rendered where the icon should be", "the icon works when i hardcode it but not when it comes from data", "icons chosen dynamically never appear", "how do i show an icon whose name comes from a database field", "my icon is huge or tiny and ignores the size i set", "the icon colour will not change no matter what i set", "my hand drawn icon looks thicker than the ones next to it", "the icons look inconsistent in weight across the page", "i passed a name to the button icon and got the wrong icon set", "i think i misspelled the icon name but nothing warns me"]
product: frappe-ui
---

# Lucide icons

## paths

tailwind/lucideIconsPlugin.js — matchComponents, encodeSvgAsDataUri, readAvailableIconNames
vite/lucideIcons.js — lucideIcons, generateIconModule, getIcons, camelToDash
vite/index.js — frappeuiPlugin
src/components/Button/Button.vue — iconLeft, icon, iconRight
src/components/FeatherIcon.vue — name

## rules

MUST expect two independent paths: the Tailwind plugin registers a `lucide-<name>` class for every icon shipped by the icon package, and the Vite plugin registers auto-imported components through the icons resolver.
MUST expect the Vite path to be on unless it is disabled, since its option defaults to true.
MUST expect an unknown class name to emit an empty rule and to raise nothing, because the encoder returns null for a missing file and the matcher answers with an empty object — a typo renders a bare invisible element.
MUST expect an unknown component name to load nothing, since the module generator returns null when the icon is absent.
MUST write the class as a literal in a file the Tailwind content globs cover, because the compiler emits CSS only for class strings it finds by scanning; a name assembled at runtime produces no rule.
MUST use the component path, or MUST list the candidate names as literals, where the icon is chosen from data.
MUST size an icon class with a size utility and tint it with a text utility, since the plugin registers in the components layer and the utilities layer wins.
MUST expect both paths to rewrite the shipped stroke width from 2 to 1.5, so an icon drawn by hand at stroke 2 sits heavier than every neighbour.
MUST pass a string beginning `lucide-` to a Button icon prop to take the class path, since the component branches on that prefix and sends any other string to the feather icon component.
MUST expect a component or a render function in the same prop to be rendered through a dynamic component, so the prop accepts three shapes and validates none of them.
MUST expect both spellings of a name carrying a digit to resolve on the component path, since the converter registers the dashed and the undashed form.

## values

class form: `lucide-<name>`, a mask image over the current colour
class defaults: 1em square, the ink gray 6 variable, inline block, no shrink
component form: the icon name in Pascal case, auto-imported
stroke width: rewritten to 1.5 on both paths
missing name: an empty rule on the class path, a null module on the component path
Button icon props: `icon`, `iconLeft`, `iconRight` — each a class string, a component, or a render function

## how

Choose the path by where the name comes from. A name written in the template is a class, which is one CSS rule and no component instance. A name that arrives in data must be a component, because the class path depends on a build-time scan of literal strings and a computed class was never scanned.

Both paths fail the same way — nothing renders, nothing is logged — so a blank space where an icon should be is a name question first: check the spelling against the icon package, then check whether the string was a literal.
