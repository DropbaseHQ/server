from functools import reduce
from typing import Any

from server.controllers.properties import read_page_properties
from server.controllers.utils import get_state_context_model
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
    if not type(value_a) == type(value_b):  # noqa
        # TODO: @Jon could this be repalces with type(value_a) is not type(value_b) ?
        value_a = str(value_a)
        value_b = str(value_b)

    if operator == "equals":
        return value_a == value_b
    elif operator == "gt":
        return value_a > value_b
    elif operator == "lt":
        return value_a < value_b
    elif operator == "not_equals":
        return value_a != value_b
    elif operator == "exists":
        return bool(value_a)
    else:
        return False


def display_rule(state, context, rules: DisplayRules):
    # iterate through rules based on the display rules for a component
    for component_display_rules in rules.display_rules:
        component_visible = False

        for rule in component_display_rules.rules:
            # If the current component's target is not visible, then even if there
            # is a value in the target that matches the rule, the component should
            # not be visible
            if rule.target.startswith("widgets"):
                widgets_context = getattr(context, "widgets")
                target_widget = rule.target.split(".")[1]
                target_component = rule.target.split(".")[2]

                widget_context = getattr(widgets_context, target_widget)
                components_context = getattr(widget_context, "components")
                component_context = getattr(components_context, target_component)

                if component_context.visible is False:
                    component_visible = False
                    break

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
