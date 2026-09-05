---
name: website-theme
description: Saving a Website Theme shells out to node to compile one CSS file into the site's public files and stores its path in theme_url, so a theme that is never saved after a code change serves the CSS compiled by the previous save.
triggers: ["WebsiteTheme", "generate_bootstrap_theme", "get_scss", "get_scss_paths", "get_active_theme", "after_migrate", "clear_cache_if_current_theme", "validate_if_customizable", "is_standard_and_not_valid_user", "delete_old_theme_files", "set_as_default", "get_apps", "export_doc", "theme_url", "theme_scss", "custom_scss", "custom_overrides", "ignored_apps", "google_font", "font_properties", "font_size", "primary_color", "dark_color", "text_color", "background_color", "button_shadows", "button_gradients", "button_rounded_corners", "website_theme_template.scss", "disable_website_theme", "Please Duplicate this Website Theme to customize.", "You are not allowed to delete a standard Website Theme", "Compiled Successfully", "website theme not applying", "custom scss frappe portal", "i changed the colors on the site theme and the website looks exactly the same", "why does my site still show the old styling after i edited the stylesheet", "site theme edits do nothing until i open it and hit save again", "the site went back to its old look right after we deployed", "my color variable is set but the buttons are still the default color", "i put my override in the wrong box and nothing changed on the page", "it will not let me edit the theme that came with the system", "why am i told to make a copy before i can change the look", "saving the theme blows up with an error from some other program on the server", "the theme will not save on the production machine but saves fine locally", "the stylesheet link on the public pages points at a file that is gone", "one page on the site has no styling at all while the rest look fine"]
product: frappe
---

# Website Theme

## paths

frappe/website/doctype/website_theme/website_theme.py — WebsiteTheme, validate, on_update, on_trash, validate_if_customizable, is_standard_and_not_valid_user, export_doc, clear_cache_if_current_theme, generate_bootstrap_theme, delete_old_theme_files, set_as_default, get_apps, get_active_theme, get_scss, get_scss_paths, after_migrate
frappe/website/doctype/website_theme/website_theme_template.scss — google_font, font_properties, primary_color, dark_color, text_color, background_color, custom_overrides, website_theme_scss, font_size, custom_scss
frappe/website/doctype/website_theme/website_theme.json — theme, custom, custom_scss, custom_overrides, theme_url, theme_scss, ignored_apps
frappe/website/doctype/website_settings/website_settings.py — get_website_settings, disable_website_theme
frappe/templates/includes/head.html — theme_url

## rules

MUST re-save a Website Theme after any change to an app's `website.scss`, because generate_bootstrap_theme runs only from validate and the served file is whatever the last save compiled.
MUST expect `bench migrate` to re-save the active theme; after_migrate loads the theme named on Website Settings and saves it, and returns without doing anything when that value is empty or `Standard`.
MUST duplicate a shipped theme before editing it; validate_if_customizable throws "Please Duplicate this Website Theme to customize." for any theme whose `custom` is unset while developer_mode is off.
MUST expect the compile to be a node subprocess run from the frappe app source path, so a theme cannot be saved on a host with no node and the failure arrives as the subprocess stderr rendered into a throw.
MUST put Bootstrap variable assignments in `custom_overrides` and rules in `custom_scss`; the template writes custom_overrides BEFORE the app imports and custom_scss AFTER them, so a variable set in custom_scss is read too late to change anything the imports compiled.
MUST name a Color record in `primary_color`, `dark_color`, `text_color` and `background_color`; the template resolves each through the `color` field of the Color document and writes nothing when the link is empty.
MUST add an app to `ignored_apps` to drop its stylesheet; get_scss filters the import list by app prefix, and there is no per-file exclusion.
MUST expect a custom theme to write a NEW file on every save — the filename carries a random suffix — and delete_old_theme_files to remove the previous ones, so the URL changes and a cached page pointing at the old file finds nothing.
NEVER rely on a theme edit to refresh a live site by itself; clear_cache_if_current_theme clears the website cache only when Website Settings already names this theme.
MUST expect head.html to link `theme.theme_url` only while the theme's name is not `Standard`, and to include the bundled website stylesheet otherwise.
MUST expect `disable_website_theme` on the rendering context to replace the theme with an empty dict, so a page that sets it gets neither the theme URL nor the bundle path that depends on it.
NEVER delete a theme whose `custom` is unset outside developer_mode; on_trash raises PermissionError with "You are not allowed to delete a standard Website Theme".

## values

compile trigger: validate, on every save
compiler: node generate_bootstrap_theme.js, run from the frappe app source path
output: /files/website_theme/<scrubbed name>_<suffix>.css, suffix random for custom and the literal "style" for standard
stored on: theme_url, with the rendered SCSS kept in theme_scss
scss order: google font import, color variables, the three enable flags, custom_overrides, app imports, font_size, custom_scss, the :root block
app imports: public/scss/website.scss and public/scss/website.bundle.scss from every installed app
excluded by: ignored_apps, matched on the app name prefix
active theme: Website Settings website_theme, read through get_active_theme
link emitted: only when theme.name is not Standard

## how

The theme is a compiled file, not a live stylesheet. Every save renders `website_theme_template.scss` from the document's fields, hands the string to a node process, and writes one CSS file into the site's public files; the document then stores that file's path. Nothing recompiles on request. So a change made anywhere but this document — an app's `website.scss`, a Color record, a newly installed app that ships styles — is invisible until the theme is saved again, which is exactly why migrate re-saves it.

The two code fields are not interchangeable. `custom_overrides` lands above the app imports, which is where a Bootstrap variable has to be for the imports to compile against it. `custom_scss` lands below them, which is where a rule that must win has to be. Putting a variable in the lower field produces the classic non-effect: the value is set, the compile succeeds, and nothing on the page changes.

Whether a theme can be changed at all is decided by `custom` rather than by a role. A shipped theme refuses to validate and refuses to be trashed unless developer_mode is on, so the only way to change one on a production site is to duplicate it. That duplicate compiles to a randomly suffixed filename and deletes its predecessors, which keeps the URL fresh at the cost of making the old URL a 404 rather than a stale file.
