import logging
from datetime import datetime
from functools import reduce
from typing import Any

from dateutil.parser import parse

from dropbase.schemas.display_rules import DisplayRules
from server.controllers.properties import read_page_properties
from server.controllers.utils import get_state_context_model

logger = logging.getLogger(__name__)


def get_by_path(root, items):
    return reduce(lambda x, y: getattr(x, y), items.split("."), root)


def set_by_path(root, items, value):
    attrs = items.split(".")
    last_attr = attrs.pop()
    obj = reduce(lambda x, y: getattr(x, y), attrs, root)
    setattr(obj, last_attr, value)


def is_epoch_timestamp(value: str):
    try:
        int_value = int(value)
        int_value_digits = len(str(int_value))

        # if the value is 13 digits long, it is a millisecond timestamp
        if int_value_digits == 13:
            new_timestamp = datetime.utcfromtimestamp(int_value / 1000)
        elif int_value_digits == 10:
            new_timestamp = datetime.utcfromtimestamp(int_value)

        return new_timestamp

    except ValueError:
        return False


def coerce_to_target_type(target_type: str, value: Any):

    if value is None:
        return value

    match target_type:
        case "date":
            new_datetime = None
            if is_epoch_timestamp(value):
                new_datetime = is_epoch_timestamp(value)
            else:
                new_datetime = parse(value)
            if isinstance(new_datetime, datetime):
                new_datetime = new_datetime.date()
            return new_datetime
        case "float":
            value = float(value)
            return value
        case "int":
            value = int(value)
            return value
        case "text":
            value = str(value)
            return value
        case "boolean":
            if isinstance(value, bool):
                return value
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            return value

        case _:
            value = str(value)
            return value


# helper function to compare values with operators
def compare_values(target_value: Any, operator: str, rule_value: Any, target_type: str):
    try:

        target_value = coerce_to_target_type(target_type, target_value)
        rule_value = coerce_to_target_type(target_type, rule_value)

    if operator == "equals":
        return target_value == rule_value
    elif operator == "gt":
        return target_value > rule_value
    elif operator == "gte":
        return target_value >= rule_value
    elif operator == "lt":
        return target_value < rule_value
    elif operator == "lte":
        return target_value <= rule_value
    elif operator == "not_equals":
        return target_value != rule_value
    elif operator == "exists":
        return bool(target_value)
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
            target_type = None
            if hasattr(rule, "target_type"):
                target_type = rule.target_type

            # compare the target value from the state with the rule value
            rule_applies = compare_values(
                target_value=target_value,
                operator=rule.operator,
                rule_value=rule.value,
                target_type=target_type,
            )

            if rule.andor:
                if rule.andor.lower() == "and":
                    component_visible = component_visible and rule_applies
                elif rule.andor.lower() == "or":
                    component_visible = component_visible or rule_applies
            else:
                component_visible = rule_applies

        # the resulting state of the component is defined by the final rule resulting condition
        set_by_path(
            context, f"{component_display_rules.component}.visible", component_visible
        )

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
    try:
        State = get_state_context_model(app_name, page_name, "state")
        Context = get_state_context_model(app_name, page_name, "context")

        state = State(**state)
        context = Context(**context)

        properties = read_page_properties(app_name, page_name)
        display_rules = get_display_rules_from_comp_props(properties)

        rules = DisplayRules(display_rules=display_rules)
        return display_rule(state, context, rules)
    except Exception as e:
        logger.error(f"Error running display rule: {e}")
        return context
