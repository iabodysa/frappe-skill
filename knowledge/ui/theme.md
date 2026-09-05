---
name: theme
description: Dark mode waits for something to write data-theme on the root element, and only ink, surface and outline classes read a CSS variable — every other colour class is a frozen hex.
triggers: ["darkMode", "generateCSSVariables", "generateSemanticColors", "generateColorPalette", "resolveColorReference", "addBase", "extend", "lightMode", "themedVariables", "overlay", "neutral", "dark mode does not switch", "data-theme attribute", "dark mode does nothing when i toggle it", "the switch flips but the page stays light", "why is my app ignoring the system dark setting", "half the page goes dark and the rest stays white", "some buttons keep their light colours in dark mode", "the toggle reports a different mode from what is on the screen", "the page flashes light for a second before it turns dark on load", "how do i change one background colour everywhere without editing every component", "my custom colour has no effect on the shared components", "the app gets sluggish after switching themes many times"]
product: frappe-ui
---

# The theme

## paths

src/utils/theme.ts — useTheme, setTheme, initializeTheme, getSystemTheme, toggleTheme, currentTheme
tailwind/preset.js — darkMode
tailwind/colorPalette.js — generateCSSVariables, generateSemanticColors, generateColorPalette, resolveColorReference
tailwind/plugin.js — addBase, extend
tailwind/colors.json — lightMode, darkMode, themedVariables, overlay, neutral

## rules

MUST expect dark mode to key on the attribute selector rather than the media query, so every dark value stays inert until something writes `data-theme="dark"` on the root element.
MUST call `useTheme` inside a component that stays mounted for the session, since it registers its own mounted hook and nothing else in the package writes the attribute.
MUST call `initializeTheme` by hand only outside a component; inside one the mounted hook already calls it.
MUST expect `setTheme` to resolve `system` to the media query's answer at the moment of the call and to store the literal word `system`.
MUST expect `initializeTheme` to read the stored value, to accept only `light`, `dark` and `system`, and to fall back to `system`.
NEVER read `currentTheme` as the rendered theme: it holds `system` while the attribute holds `light` or `dark`, and it holds `light` before the mounted hook runs.
MUST expect the media query listener to live for the page's lifetime, since the composable adds it inside the mounted hook and returns its removal from inside that same hook, where nothing collects it — so each extra `useTheme` call adds one more permanent listener.
MUST expect the returned object to be `currentTheme`, `toggleTheme`, `setTheme`, `initializeTheme` and `getSystemTheme`, with nothing to unbind.
MUST expect exactly three token categories — `outline`, `surface` and `ink` — and a token class to compile to a variable reference with the light value as its fallback.
MUST expect those categories to reach only the utilities the plugin extends, so `text-surface-white` and `bg-ink-gray-8` emit nothing.
MUST expect a palette class such as `bg-blue-500` or `text-red-700` to compile to a literal hex, to ignore every variable, and not to change under the dark attribute, because the dark shades are published under a `dark-` prefix instead.
MUST expect frappe-ui components to mix the two kinds in one class list, so a token override leaves the palette classes in that component unchanged.
MUST recolour a token by redeclaring its variable in a stylesheet imported after the one carrying the Tailwind base layer, since the base layer declares it.
MUST recolour a palette shade under `theme.extend.colors` in the application's own Tailwind config, since no variable reaches it.

## values

dark selector: `[data-theme="dark"]`
attribute writer: `setTheme`, called by `initializeTheme` and `toggleTheme`
stored under: `theme` in localStorage, one of `light`, `dark`, `system`
currentTheme before mount: `light`
token categories: outline 16 names, surface 32 names, ink 27 names
token class compiles to: `var(--<category>-<name>, <light hex>)`
extended utilities: textColor.ink, backgroundColor.surface, fill.ink, fill.surface, stroke.ink, placeholderColor.ink, borderColor.outline, ringColor.outline, divideColor.outline
palette families: gray, blue, green, red, amber, orange, yellow, teal, cyan, purple, pink, violet, each also under a `dark-` prefix
emitted rule bodies: `:root` and `[data-theme="dark"]`, added to the base layer

## how

There are two colour systems in one package and the class name is the only thing that tells them apart. A name in the three token categories follows a variable and therefore follows the theme; every other colour name was resolved to a hex at build time and will not move whatever the attribute says. Before recolouring anything, read the component's class list and count which kind each class is — a control that goes half dark is a control whose classes were mixed, which is the normal case in this package.

Dark mode itself is not automatic. Nothing writes the attribute unless a mounted component called the composable, so a page that ships the preset and no `useTheme` call has a fully compiled dark palette that never applies.
