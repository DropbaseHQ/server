from functools import reduce
from typing import Any

from server.controllers.utils import get_state_context_model, read_page_properties
from server.schemas.display_rules import DisplayRules


def get_by_path(root, items):
    return reduce(lambda x, y: getattr(x, y), items.split("."), root)


def set_by_path(root, items, value):
    attrs = items.split(".")
    last_attr = attrs.pop()
    obj = reduce(lambda x, y: getattr(x, y), attrs, root)
    setattr(obj, last_attr, value)


# helper function to compare values with operators
def compare_values(value_a: Any, operator: str, value_b: Any):
    # Values entered in the UI are always strings for now
    # For proper comparison, we need to convert value_a to string
    value_a = str(value_a)
    if operator == "equals":
        return value_a == value_b
    elif operator == "gt":
        return value_a > value_b
    elif operator == "lt":
        return value_a < value_b
    elif operator == "not_equals":
        return value_a != value_b
    else:
        return False


def display_rule(state, context, rules: DisplayRules):
    # iterate through rules based on the display rules for a component
    for component_display_rules in rules.display_rules:
        component_visible = False

        for rule in component_display_rules.rules:
            # get the relevant value from the state based on the target
            target_value = get_by_path(state, rule.target)

            # compare the target value from the state with the rule value
            rule_applies = compare_values(target_value, rule.operator, rule.value)

            if rule.andor:
                if rule.andor.lower() == "and":
                    component_visible = component_visible and rule_applies
                elif rule.andor.lower() == "or":
                    component_visible = component_visible or rule_applies
            else:
                component_visible = rule_applies

        # the resulting state of the component is defined by the final rule resulting condition
        set_by_path(context, f"{component_display_rules.component}.visible", component_visible)

    return context.dict()


def get_display_rules_from_comp_props(component_props):
    component_display_rules = []
    for widget_data in component_props.get("widgets"):
        widget_name = widget_data.get("name")
        for component in widget_data.get("components"):
            component_name = component.get("name")
            if component.get("display_rules"):
                comp_name = f"widgets.{widget_name}.components.{component_name}"
                comp_rule = {
                    "component": comp_name,
                    "rules": component.get("display_rules"),
                }
                component_display_rules.append(comp_rule)
    return component_display_rules


def run_display_rule(app_name: str, page_name: str, state: dict, context: dict):
    State = get_state_context_model(app_name, page_name, "state")
    Context = get_state_context_model(app_name, page_name, "context")

    state = State(**state)
    context = Context(**context)

    properties = read_page_properties(app_name, page_name)
    display_rules = get_display_rules_from_comp_props(properties)

    rules = DisplayRules(display_rules=display_rules)

    return display_rule(state, context, rules)
