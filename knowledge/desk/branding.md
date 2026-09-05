---
name: branding
description: The desk title comes from Website Settings app_name before System Settings app_name and falls back to the literal "Frappe", and the favicon falls back to the framework SVG in the template as well as in the context.
triggers: ["app_name", "app_title", "app_logo_url", "app_publisher", "app_description", "favicon", "splash_image", "brand_html", "banner_html", "banner_image", "footer_logo", "footer_powered", "copyright", "title_prefix", "website_context", "get_website_settings", "get_boot", "build_version", "desk_theme", "layout_direction", "app.html", "base.html", "frappe-favicon.svg", "frappe-framework-logo.svg", "attach_files:", "change the frappe logo", "rename the desk title", "white label frappe", "i changed the app name but the browser tab still says frappe", "renaming the app did nothing it still shows the default name", "where do i set the name that shows in the browser tab?", "the icon in the tab is still the default one after i uploaded mine", "my uploaded icon never shows up in the tab", "why does the old tab icon keep coming back?", "the logo changed on the public site but not inside the app", "i set the logo in one place and the other side still shows the old one", "the new logo only appears after i clear the browser", "clearing a branding field brought back the default instead of leaving it blank", "the loading screen still shows the old image"]
product: frappe
---

# Branding

## paths

frappe/www/app.py — app_name, build_version, desk_theme, layout_direction, include_icons
frappe/www/app.html — app_name, favicon
frappe/templates/base.html — favicon, title
frappe/website/doctype/website_settings/website_settings.py — get_website_settings, brand_html, banner_html, banner_image, footer_logo, footer_powered, copyright, title_prefix, favicon, splash_image
frappe/core/doctype/system_settings/system_settings.json — app_name
frappe/hooks.py — app_name, app_title, app_publisher, app_description, app_logo_url, app_include_icons

## rules

MUST set `app_name` on Website Settings to rename the desk; www/app.py reads Website Settings first, System Settings second, and substitutes the literal string "Frappe" when both are empty.
MUST expect the same value to render as the desk page title, because app.html puts `app_name` straight into the title element.
MUST set `favicon` on Website Settings for the desk and the portal together; one field feeds both, and both templates fall back to the framework SVG when it is empty.
NEVER read a favicon field holding `attach_files:` as set; get_website_settings copies the value onto the context only when it is not that string.
MUST expect a portal page to be able to override the favicon on its own context, since get_website_settings sets the default only when the context does not already carry one and then lets the Website Settings value replace it.
MUST use `brand_html` for the portal navbar mark and Navbar Settings `app_logo` for the desk mark; they are two different fields, one read by the portal and one by the desk, and neither falls back to the other.
MUST expect every Website Settings branding field to be copied onto the context ONLY when it is truthy, so clearing one restores the template default rather than blanking the field.
MUST declare a branding string an app owns through the `website_context` hook when it must not be editable in the UI, and MUST expect the LAST value to win when several apps declare the same key as a list.
NEVER expect `app_title`, `app_publisher` or `app_description` in hooks.py to reach a rendered page; they name the app in the installer and the app list, and no template reads them.
MUST set `splash_image` on Website Settings to replace the loading splash, and MUST expect no fallback for it — the key is absent from the context when the field is empty.
MUST expect a desk asset change to need a new `build_version`, because app.py stamps the version into the context and the browser caches by it.

## values

desk title: Website Settings app_name, then System Settings app_name, then "Frappe"
favicon default: /assets/frappe/images/frappe-favicon.svg, written in the context and again in both templates
favicon ignored value: attach_files:
desk logo: Website Settings app_logo, Navbar Settings app_logo, app_logo_url hook
portal brand: brand_html
portal footer: footer_logo, footer_powered, copyright
portal banner: banner_html, banner_image
title prefix: title_prefix, prepended on the portal only
splash: splash_image, no default
copied only when truthy: every Website Settings key in the list get_website_settings walks
website_context list value: last entry wins, except top_bar_items, footer_items and post_login

## how

Branding is spread over three places on purpose, and each answers for a different part of the site. Website Settings holds what a portal visitor sees and, for the name and the icon, what a desk user sees as well. Navbar Settings holds the desk mark. hooks.py holds what the app declares about itself, which is read by the installer and the app list and never reaches a page.

The fallback chains all end in a hard-coded framework string rather than in nothing, which is why an incompletely branded site shows "Frappe" and the framework favicon instead of an empty title bar. Both defaults are written twice — once into the render context, once inline in the template — so clearing the field restores the framework mark rather than removing it.

Every field is copied onto the context only when it is truthy. That makes clearing a field the way to restore a default and makes an empty string indistinguishable from an unset one. Where a value must not be editable at all, the `website_context` hook writes it straight onto the context; if two apps declare the same key as a list, the last entry is taken, so the answer depends on install order.
