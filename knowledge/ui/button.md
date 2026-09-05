---
name: button
description: theme, size and variant are closed unions whose every cell is a class string written inside the component, so a fifth theme cannot be added from outside and redeclaring a semantic token is the only way to recolour one.
triggers: ["buttonClasses", "withDefaults", "name", "frappe-ui button theme variant", "custom button size", "my custom colour prop on the button does nothing", "why can't i add a new button colour", "the button ignores the class i pass it", "how do i add a fifth style to these buttons", "passing my own colour name to the button breaks the build", "the button looks the same no matter what i pass it", "how do i restyle every button in the app at once", "the hover colour stays the old one after i changed the colour", "i need a button shape this library does not have", "it complains that the value i gave the button style is not allowed"]
product: frappe-ui
---

# Button

## paths

src/components/Button/types.ts — ButtonProps, Theme, Size, Variant, ThemeVariant
src/components/Button/Button.vue — buttonClasses, withDefaults
src/components/Button/index.ts — Button, ButtonProps
src/components/FeatherIcon.vue — name

## rules

MUST expect `theme`, `size` and `variant` to be closed unions declared in the types file, and NEVER pass a value outside them.
MUST expect the class string for every theme-and-variant cell to be written inside the component, chosen by a map on the variant, with the disabled state keyed on the pair.
MUST expect a fifth theme or a fifth variant to be impossible from outside: the union refuses the prop and no map carries the cell.
MUST restyle an existing theme by redeclaring the token its classes name, never by editing the component.
MUST write a wrapper component of your own for a shape the grid does not carry, and NEVER expect a new prop to reach the component.
MUST expect the component to name semantic tokens and frozen palette classes in the same rule, so a token override recolours the resting state and leaves a hover unchanged.
MUST read the component's own index file as its exports: the component and its props type.
MUST expect `icon`, `iconLeft` and `iconRight` each to accept a class string, a component or a render function, and to validate none of them.

## values

theme: gray, blue, green, red
variant: solid, subtle, outline, ghost
size: sm, md, lg, xl, 2xl
defaults: theme gray, size sm, variant subtle, loading false, type button
disabled map: keyed on the theme and variant pair
other props: label, tooltip, loadingText, disabled, route, link, type

## how

The appearance is a finished grid, not a set of style props. Four themes by four variants by five sizes are enumerated in the file, and every cell is a prepared class string, so the question a reader should ask is never "which prop adds my colour" — no prop does — but "which of the twenty cells is closest, and what does its token resolve to".

That leaves exactly two ways in. Redeclare a token to move every component that names it, or wrap the component to get a shape it does not offer. Editing the file is a third and it is a fork.
