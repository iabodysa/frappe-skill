---
name: get-users-with-role
description: get_users_with_role runs one query joining Has Role and User, filters out disabled users and Administrator, and de-duplicates with .distinct().
triggers: ["get_users_with_role", "get all users with a role", "get_users_with_role query", "how do i get every user who has a certain role", "my list of role holders is missing people who are switched off", "why is the admin account missing from my list of role holders", "the same person shows up twice in my list of users with that role", "getting the users for a role is really slow when there are many of them", "i need to email everyone with a given role but my list is wrong", "does the role holder list include disabled accounts", "why does my role membership list not match what i see on the user screen", "why is my loop over role holders running one query per person", "who has this role and how do i get them in one go"]
product: frappe
---

# Get Users With Role

## paths

frappe/utils/user.py — get_users_with_role

## rules

MUST call frappe.utils.user.get_users_with_role(role) rather than get_all on Has Role plus a per-user enabled check, because get_users_with_role runs one query where a get_all plus a per-user check runs one query per holder.
MUST expect Administrator excluded even when Administrator holds the role, because the query filters User.name != "Administrator".
MUST expect a user holding the role through more than one Has Role row to appear once, because the query ends in .distinct().
NEVER read the result as a full membership list; a disabled user holding the role never appears, because the query filters User.enabled == 1.

## values

filters: HasRole.role == role, User.name != "Administrator", User.enabled == 1
query shape: frappe.qb join of Has Role and User, .distinct(), .run(pluck=True)

## how

get_users_with_role is one join, not a helper worth rebuilding. The enabled check and the Administrator exclusion live in the WHERE clause, so a version that filters after get_all pays one query per user for the same enabled check the join already folds in — and unless it also excludes Administrator and dedupes, it returns a different set, not merely a slower one.
