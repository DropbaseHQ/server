import ast
import json
import logging
from datetime import datetime
from functools import reduce
from typing import Any

from dateutil.parser import parse

from dropbase.helpers.utils import get_state_empty_context
from dropbase.schemas.display_rules import DisplayRules

logger = logging.getLogger(__name__)


def get_by_path(root, items):
    try:
        return reduce(lambda x, y: getattr(x, y), items.split("."), root)
    except AttributeError:
        return None


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
        case "integer":
            value = int(value)
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

        if target_value is None and operator in ["gt", "gte", "lt", "lte"]:
            return False

        target_value = coerce_to_target_type(target_type, target_value)
        rule_value = coerce_to_target_type(target_type, rule_value)

        if target_type == "string_array":
            if target_value is not None:
                target_value = ast.literal_eval(target_value)
            else:
                target_value = []
            if operator == "equals":
                return rule_value in target_value
            elif operator == "not_equals":
                return rule_value not in target_value
            elif operator == "exists":
                return len(target_value) > 0
            return False

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
    except Exception as e:
        raise Exception(f"Error comparing values: {e}")


def display_rule(state, context, rules: DisplayRules):
    # iterate through rules based on the display rules for a component
    for component_display_rules in rules.display_rules:
        component_visible = False

        for rule in component_display_rules.rules:
            # If the current component's target is not visible, then even if there
            # is a value in the target that matches the rule, the component should
            # not be visible
            target_widget = rule.target.split(".")[0]
            target_section = rule.target.split(".")[1]
            target_component = rule.target.split(".")[2]

            target_widget_context = getattr(context, target_widget)
            """
            if a component depends on another component that is hidden,
            it should be hidden even if display rule is true
            """
            if hasattr(target_widget_context, target_section):
                components_context = getattr(target_widget_context, target_section)
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
        set_by_path(context, f"{component_display_rules.component}.visible", component_visible)

    return context.dict()


def get_display_rules_from_comp_props(component_props: dict):
    component_display_rules = []
    for data in component_props.values():
        widget_name = data.get("name")
        if not data.get("components"):
            continue
        for component in data.get("components"):
            component_name = component.get("name")
            if component.get("display_rules"):
                comp_name = f"{widget_name}.components.{component_name}"
                comp_rule = {
                    "component": comp_name,
                    "rules": component.get("display_rules"),
                }
                component_display_rules.append(comp_rule)
    return component_display_rules


def run_display_rule(app_name: str, page_name: str, state: dict):
    state, context = get_state_empty_context(app_name=app_name, page_name=page_name, state=state)
    try:
        path = f"workspace/{app_name}/{page_name}/properties.json"
        with open(path, "r") as f:
            properties = json.loads(f.read())
        display_rules = get_display_rules_from_comp_props(properties)

        rules = DisplayRules(display_rules=display_rules)
        return display_rule(state, context, rules)
    except Exception as e:
        logger.error(f"Error running display rule: {e}")
        return context
