---
name: render-address
description: render_address accepts check_permissions=False for a guest context, and returns the rendered Address Template — not a plain string — so a plain-text formatter is work it does not do while a permission bypass is a misreading of it.
triggers: ["get_default_address", "get_address_display", "render_address", "Address", "Address Title is mandatory.", "render address template", "address template guest access", "how do i show a customer address on a page that a logged out visitor can open", "the address does not render for guests and i keep getting a permission error", "why is my address coming back as full html when i just wanted one line", "i need the address as a plain comma separated line for a label", "how do i get the default address of a customer or supplier", "is there a way to skip the permission check when showing an address publicly", "the address shows fine when i am logged in and disappears on the public site", "how do i print an address the same way the desk shows it", "what is the right way to format an address for a qr sticker", "the rendered address has markup in it and it breaks my app screen"]
product: frappe
---

# Render Address

## paths

frappe/contacts/doctype/address/address.py — get_default_address, get_address_display, render_address

## rules

MUST call render_address(address, check_permissions=False) for a guest or token-authenticated context that needs an address rendered, rather than reading the row with frappe.db.get_value to skip the permission check; render_address already offers the bypass as a parameter.
MUST expect get_address_display to always call render_address with check_permissions=True, so a caller that needs the false path calls render_address directly.
MUST expect render_address to return the rendered Address Template — jinja, HTML — never a plain string; a single-line formatter for an SPA, a QR label or a print field is work render_address does not do.
MUST call get_default_address(doctype, name) to resolve the linked default Address through Dynamic Link, ordered by is_primary_address or is_shipping_address.

## how

Two different questions get asked of render_address and only one has an answer inside it. Whether a Guest can read the address is answered — check_permissions=False skips address.check_permission() — so reading the row directly to dodge permissions is not extra work, it is the same call with the flag left at its default. Whether the output can be a plain comma-joined line is not answered, because render_address always renders the Address Template, so a formatter producing anything other than the template's HTML is doing real work render_address does not do.
