---
name: tailwind-preset
description: The preset's plugin states a whole theme rather than an extend, so the scale it names replaces Tailwind's and text-4xl, 2xl: and slate emit no CSS.
triggers: ["preset.js", "darkMode", "plugins", "theme", "borderRadius", "boxShadow", "fontSize", "screens", "extend", "addBase", "addComponents", "generateColorPalette", "generateCSSVariables", "generateSemanticColors", "matchComponents", "frappe-ui tailwind preset overrides theme", "text-4xl class missing", "my text size class does nothing and there is no error", "the biggest heading class just renders at normal size", "why does a class straight from the docs produce no styles here", "some colour names work and others are completely ignored", "the widest screen size prefix has no effect at all", "i added one font size to my config and every other size disappeared", "adding a custom size broke all the built in sizes", "how do i change a corner radius or a shadow across the whole app", "the buttons from the component library come in completely unstyled", "styles are missing only for the components that came from the package"]
product: frappe-ui
---

# The Tailwind preset

## paths

tailwind/index.js — preset.js
tailwind/preset.js — darkMode, plugins
tailwind/plugin.js — theme, borderRadius, boxShadow, fontSize, screens, extend, addBase, addComponents
tailwind/colorPalette.js — generateColorPalette, generateCSSVariables, generateSemanticColors
tailwind/lucideIconsPlugin.js — matchComponents

## rules

MUST expect the package's Tailwind entry to re-export the preset, and MUST expect that file to carry two keys only: the dark-mode selector and a four-plugin list.
MUST read the theme plugin as the file holding the design decisions, since it passes a second argument whose `theme` object sits outside `extend`.
MUST expect Tailwind to keep the first theme in its list that defines a top-level key, and a preset's plugin configuration to sit ahead of Tailwind's own defaults, so a key the plugin states replaces Tailwind's scale for that key while a key it leaves alone still comes from Tailwind.
MUST expect exactly 16 font sizes and no more, so `text-4xl` and everything above it emits nothing.
MUST expect exactly 4 breakpoints, so a `2xl:` variant emits nothing.
MUST expect `theme.colors` to be the generated palette, so Tailwind's own slate, zinc, indigo, sky, rose, lime, emerald, fuchsia, stone and neutral are absent.
MUST write every size, radius, shadow or colour change into the application's own Tailwind config under `theme.extend`, never under `theme`, because a bare `theme.fontSize` there replaces all 16 keys and deletes the prose scale.
MUST list the package's own source glob in the application's `content` array, since the class names colouring every frappe-ui component are literals inside the package and nothing is emitted for a file the scanner does not read.
NEVER open a component file to change a size, a radius, a shadow or a breakpoint; the application's Tailwind config is the whole of it.

## values

plugins: forms, typography, the theme plugin, the lucide icons plugin
font sizes: 2xs, xs, sm, base, lg, xl, 2xl, 3xl, and the same eight under a `p-` prose prefix
breakpoints: sm 640px, md 768px, lg 1024px, xl 1280px
rounded: 8px; rounded-sm 4px, rounded-md 10px, rounded-lg 12px, rounded-xl 16px, rounded-2xl 20px
shadows: sm, DEFAULT, md, lg, xl, 2xl, none — the default is a two-layer black shadow
still from Tailwind: spacing, width, height
extended rather than replaced: spacing, and the semantic colour utilities

## how

A preset that replaces is the whole story here. Tailwind merges a theme by first-definition-wins, and the plugin defines `fontSize`, `screens`, `colors`, `borderRadius` and `boxShadow` at the top level, so those five scales are the package's and nothing of Tailwind's remains in them. That is why a class from the documentation compiles to nothing and produces no error — the class is real, the scale key is gone.

The same rule catches an application config written the obvious way. Adding one font size under `theme` rather than `theme.extend` wins the merge and deletes fifteen. Put everything under `extend` and the question stops arising.
