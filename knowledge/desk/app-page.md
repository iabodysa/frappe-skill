---
name: app-page
description: make_app_page hands back a page head whose every action element already exists and starts hidden, nothing on it is cleared by a route change, and the duplicate-label check on menu items never matches, so a toolbar rebuilt on refresh grows one more copy of itself on every visit.
triggers: ["frappe.ui.make_app_page", "frappe.ui.Page", "frappe.ui.pages", "Page.make", "add_main_section", "setup_page", "setup_sidebar_toggle", "update_sidebar_icon", "set_indicator", "clear_indicator", "set_action", "set_primary_action", "set_secondary_action", "clear_action_of", "clear_actions", "clear_custom_actions", "add_menu_item", "add_custom_menu_item", "add_dropdown_item", "is_in_group_button_dropdown", "clear_menu", "clear_user_actions", "add_action_item", "add_actions_menu_item", "show_actions_menu", "add_inner_button", "remove_inner_button", "change_inner_button_type", "get_or_add_inner_group_button", "clear_inner_toolbar", "add_button", "add_custom_button_group", "add_action_icon", "add_help_button", "set_title", "set_title_sub", "get_title_area", "add_field", "get_form_values", "add_view", "set_view", "single_column", "card_layout", "make_page", "required_libs", "disable_sidebar_toggle", "set_document_title", "on_page_load", "on_page_show", "trigger_page_event", "change_to", "add_page", "route_titles", "ui/page.html", "the object make_app_page returns", "wrapper.page", "page head", "page toolbar buttons", "duplicate menu items on a page head", "primary action not showing", "actions button hidden", "inner toolbar button", "every time i go back to the page the buttons are doubled", "the same menu item keeps getting added over and over", "why do my toolbar buttons multiply each time i visit the page?", "my check for whether the button is already there always says yes", "the code thinks the button exists but nothing is on screen", "why does it say the action is already added when i cannot see it?", "leftover buttons from the previous screen stay on the new one", "the old title and status light are still showing after i moved to another screen", "how do i clear the buttons when leaving a custom screen?", "i added a main button and it never appears"]
product: frappe
---

# App Page

## paths

frappe/public/js/frappe/ui/page.js — frappe.ui.make_app_page, frappe.ui.pages, Page.make, Page.add_main_section, Page.setup_page, Page.setup_sidebar_toggle, Page.update_sidebar_icon, Page.set_indicator, Page.clear_indicator, Page.set_action, Page.set_primary_action, Page.set_secondary_action, Page.clear_action_of, Page.add_menu_item, Page.add_dropdown_item, Page.is_in_group_button_dropdown, Page.clear_btn_group, Page.clear_user_actions, Page.add_action_item, Page.add_actions_menu_item, Page.add_inner_button, Page.remove_inner_button, Page.change_inner_button_type, Page.get_or_add_inner_group_button, Page.clear_inner_toolbar, Page.add_button, Page.add_custom_button_group, Page.add_action_icon, Page.add_help_button, Page.set_title, Page.set_title_sub, Page.add_field, Page.get_form_values, Page.add_view, Page.set_view
frappe/public/js/frappe/ui/page.html — title-area, title-text, indicator-pill, sub-heading, page-actions, custom-actions, standard-actions, page-icon-group, menu-btn-group, btn-secondary, actions-btn-group, primary-action, page-body, page-content
frappe/public/js/frappe/views/pageview.js — frappe.views.Page, trigger_page_event
frappe/public/js/frappe/views/container.js — Container.add_page, Container.change_to
frappe/public/js/frappe/utils/utils.js — frappe.utils.set_title
frappe/public/js/frappe/router.js — frappe.route_titles, set_title
frappe/public/js/frappe/ui/alt_keyboard_shortcuts.js — get_shortcut_group, AltShortcutGroup.add
frappe/public/js/frappe/ui/toolbar/toolbar.js — Toolbar.bind_events

## rules

MUST call frappe.ui.make_app_page from on_page_load and keep the return value; it is the same instance it assigns to `wrapper.page`, and it is filed in frappe.ui.pages under whatever `frappe.get_route_str()` returns at construction.
MUST build every toolbar entry in on_page_load and never in on_page_show or refresh, because Container.change_to hides a page container and never destroys it, so the second visit runs those handlers over a head that still holds everything the first visit added.
NEVER expect add_menu_item or add_action_item to skip a label it already carries: is_in_group_button_dropdown looks for `li > a.grey-link > span[data-label="…"]` and add_dropdown_item writes no data-label at all, so the check never matches and the item is appended a second time.
MUST call clear_menu, clear_actions_menu, clear_inner_toolbar, clear_actions, clear_icons or clear_indicator yourself before rebuilding any part of the head, because nothing in the framework clears a page head on a route change.
MUST use add_action_item, not add_actions_menu_item, for the first entry in the Actions group; add_actions_menu_item passes `show_parent: false` and leaves the whole group hidden, so the item is added and cannot be reached until show_actions_menu runs.
MUST expect set_primary_action and set_secondary_action to replace rather than add: set_action calls clear_action_of first, so a second call puts its button where the first one stood.
MUST use add_inner_button, add_button or add_custom_button_group for a second, third and fourth command; they append into `custom-actions`, which is the only part of the page head that grows.
NEVER keep an inner button's identity as a string for later removal; hold the jQuery object add_inner_button returned, because add_inner_button writes `data-label` from the raw label while remove_inner_button maps the label through `__()` before it encodes it, so removal misses under any language but English.
NEVER pass a list of labels to remove_inner_button; it interpolates the array into one `data-label` selector, so anything past a single element matches nothing.
MUST read change_inner_button_type finding no button as success: its `if (btn)` test is true for an empty jQuery set, and its `removeClass()` takes no argument, so it also strips every class the author added to a button it does find.
MUST treat `this.inner_toolbar` and `this.custom_actions` as one element — setup_page assigns the same node to both — so clear_inner_toolbar also erases every button add_button and add_custom_button_group put there.
MUST pass a `standard` of true for a menu item that belongs to the page and false for one that belongs to the current record, because a false item is inserted above a divider and tagged `user-action`, which is the only thing clear_user_actions removes.
MUST read `this.sidebar` as an empty jQuery set whenever single_column is true; add_main_section renders no `.layout-side-section`, so every append to it, the framework's own skip-to-main-content link included, is dropped without an error.
NEVER scope a sidebar-toggle query to the page: setup_sidebar_toggle and update_sidebar_icon both select `$(".page-head")` across the whole document, which holds one head per page container ever visited.
MUST translate the string yourself before passing it to set_title or set_indicator; neither calls `__()`, while add_inner_button, add_custom_button_group and set_title's tooltip_label do.
NEVER build set_indicator's label out of record data without escaping it; the label is interpolated into `.html()`.
MUST pass `tab_title` to set_title when the browser tab needs different text from the heading, and expect the tab text to come back on its own when the route is revisited, because set_title stores it in frappe.route_titles under the sub path and the router replays it.
NEVER pass `set_document_title` in the opts; the constructor sets it and nothing in the repository reads it. `this.buttons` is dead the same way.
NEVER call add_help_button; its body is a comment.
MUST give a page-form field an explicit `fieldname`, because add_field keys fields_dict on `df.fieldname || df.label` and get_form_values returns exactly those keys.
NEVER expect an HTML fieldtype from add_field to appear in get_form_values; add_field returns before it registers the control in fields_dict.
MUST call add_view for a second layout and set_view to swap, rather than emptying `this.main`; every view after the first is appended hidden and set_view toggles between them and fires `view-change` on the wrapper.

## values

handed over by make_app_page: wrapper, body (= main), container, sidebar, footer, page_form, indicator, page_actions, btn_primary, btn_secondary, menu, menu_btn_group, actions, actions_btn_group, standard_actions, custom_actions, inner_toolbar (= custom_actions), icon_group, $title_area, $sub_title_area, views, fields_dict, current_view
exists and starts hidden: primary-action, btn-secondary, menu-btn-group, actions-btn-group, page-icon-group, custom-actions, indicator-pill, sub-heading, page-form, layout-footer
exists and starts visible: title-text, layout-main-section, page-body, layout-side-section unless single_column
opts read by name: title, icon, single_column, card_layout, make_page, required_libs, disable_sidebar_toggle, parent — and `$.extend(this, opts)` copies every other key onto the page
primary action: `.primary-action`, btn-primary, rightmost, one button, replaced
secondary action: `.btn-secondary`, btn-default, left of the Actions group, one button, replaced
menu item: an `<li>` under the "…" icon button, unbounded, un-hides its button on the first add
actions-menu item: an `<li>` under the btn-primary "Actions" button, unbounded, un-hidden by add_action_item only
inner button: a `<button>` in custom-actions, unbounded, matched by label before it is added, copied into the menu as a `hidden-xl` item
custom-actions visibility: `hidden-xs hidden-md` in the template — inner buttons are unreachable at those widths except through the copied menu item
alt-shortcut letter pools: one per Page object for the primary and secondary actions, one per `page_actions` node for the two group buttons, one per dropdown `ul` for its items
cleared on a route change: `header .navbar .custom-menu` in the global navbar, and `window.cur_frm`
cleared on a route change, on the page itself: nothing

## how

The author never builds the head. make_app_page renders `page.html` into the wrapper Container.add_page created, and setup_page then walks that markup once and hangs a named property on the page for every part of it. So `btn_primary`, `menu`, `actions`, `custom_actions`, `icon_group`, `indicator` and the sidebar all exist before a single call, each carrying `hide`. Every `set_` and `add_` method un-hides an element that is already there. This is why a call that appears to do nothing is almost never a missing element — it is an element that was written into and left hidden, and `add_actions_menu_item` is the method that does exactly that on purpose.

Five ways in exist because five parts of the head hold actions, and the choice is a layout decision that cannot be undone by the caller. The primary and secondary actions hold one button each: setting one twice replaces rather than accumulates, so they are for the one thing the page is for and the one thing beside it. The two dropdowns are unbounded but differently framed — the "…" menu is where page-level and record-level entries mix, separated by a divider that only `standard: false` items sit above and only clear_user_actions clears; the "Actions" group is a primary-styled button of its own and reads as a set of commands over the thing on screen. Inner buttons are the only entries that stay visible as buttons, and they cost a copied menu item each, because `custom-actions` is hidden at xs and md widths and the copy is how the page stays usable there.

Nothing clears. A Desk route change hides the page container and shows another one, so on the return every button, menu item, indicator and field is exactly where the last visit left it. The docstring on add_dropdown_item promises the opposite — that a label already in the menu is ignored — and it is wrong, because the selector it checks looks for a `data-label` attribute that add_dropdown_item never writes. Put those two together and a toolbar built inside `refresh` or `on_page_show` produces one menu item on the first visit, two on the second and ten on the tenth, while the inner buttons beside them stay at one because their own check reads an attribute that is genuinely written. The symptom is a growing menu with no error anywhere, and the fix is to build in on_page_load and to clear explicitly before any rebuild.

The label is the identity, and it is not stored the way it is read back. add_inner_button writes `data-label` from the untranslated string and renders `__(label)` as the visible text; remove_inner_button translates first and then searches. On an English desk the two agree and the method works; on a translated desk it removes nothing and reports nothing. change_inner_button_type has the same defect on the group name and cannot fail loudly either, because an empty jQuery set is truthy. Keep the object the add returned, and the question of what the label became never arises.
