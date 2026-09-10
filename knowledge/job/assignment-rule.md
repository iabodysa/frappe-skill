---
name: assignment-rule
description: Assignment Rule performs round-robin ToDo assignment on document create or update and carries no elapsed-time escalation.
triggers: ["Assignment Rule", "do_assignment", "get_user_round_robin", "round robin assignment", "escalate an assignment after N hours", "reassign after inactivity", "assignment rule timer", "priority based escalation of a ToDo"]
product: frappe
---

# Assignment Rule

## paths

frappe/automation/doctype/assignment_rule/assignment_rule.py — AssignmentRule.do_assignment, AssignmentRule.get_user_round_robin

## rules

MUST expect `do_assignment` to fire only from a document create or update event and to distribute a ToDo among users through `get_user_round_robin`.
NEVER expect a timer that re-fires after N hours of inaction, keyed by priority or otherwise; no such mechanism exists on this doctype.
MUST build an escalation-after-elapsed-time requirement on a separate scheduled job; Assignment Rule has no field or method to configure one.

## how

The rule reacts to a document event and assigns once per matching event; anything that must run because time has passed rather than because a document changed is outside what this doctype does.
