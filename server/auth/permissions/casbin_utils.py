import logging
from pathlib import Path
from uuid import UUID

import casbin
from casbin import persist
from sqlalchemy.orm import Session

from .. import crud
from ..connect import SQLALCHEMY_DATABASE_URL
from ..controllers.policy import ALLOWED_ACTIONS
from ..models import Policy
from .casbin_sqlalchemy_adaptor import Adapter

adapter = Adapter(SQLALCHEMY_DATABASE_URL, db_class=Policy)

casbin_config = ""
with open(
    str(Path(__file__).parent.absolute().joinpath("./casbin_model.conf")), "r"
) as f:
    casbin_config = f.read()


def load_specific_policies(enforcer: casbin.Enforcer, policies):
    for policy in policies:
        try:
            persist.load_policy_line(str(policy), enforcer.model)
        except Exception as e:
            print("Error loading policy", e)


def unload_specific_policies(enforcer: casbin.Enforcer, policies):
    for policy in policies:
        unload_policy_line(str(policy), enforcer.model)


def get_contexted_enforcer(db, workspace_id):
    model = casbin.Model()
    model.load_model_from_text(casbin_config)
    enforcer = casbin.Enforcer(model, adapter, True)
    logging.getLogger("casbin.enforcer").setLevel(logging.CRITICAL)
    logging.getLogger("casbin.role").setLevel(logging.CRITICAL)
    enforcer.auto_build_role_links = True

    # Refreshes policy. Allows dynamic policy changes while deployed.
    enforcer.load_policy()

    # Load workspace policies
    policies = crud.workspace.get_workspace_policies(db, workspace_id)
    formatted_policies = [str(policy) for policy in policies]
    load_specific_policies(enforcer, formatted_policies)
    # formatted_policies = [str(policy).split(", ")[1:] for policy in policies]
    # enforcer.add_policies(formatted_policies)

    # Load grouping policies
    grouping_policies = crud.workspace.get_workspace_grouping_policies(db, workspace_id)
    formatted_groups = [str(g_policy).split(", ")[1:] for g_policy in grouping_policies]
    enforcer.add_grouping_policies(formatted_groups)

    return enforcer


def enforce_action(
    db, user_id, workspace_id, resource, action, resource_crud, resource_id=None
):
    enforcer = get_contexted_enforcer(db, workspace_id)
    try:
        if resource_id:
            # Check if user has permission to perform action on specific resource
            if enforcer.enforce(str(user_id), resource_id, action):
                return True
            # Check if user has permission to perform action parent app
            if hasattr(resource_crud, "get_app_id"):
                app_id = resource_crud.get_app_id(db, resource_id)
                if enforcer.enforce(str(user_id), str(app_id), action):
                    return True

        # Check if user themselves has permission to perform action on resource
        if enforcer.enforce(str(user_id), resource, action):
            return True

        return False
    except Exception as e:
        print("Permission enforcement error", e)


def add_policy(db: Session, role_id: UUID, resource, action):
    policy = Policy(role_id=role_id, resource=resource, action=action)
    db.add(policy)
    db.commit()
    return policy


def update_policy(db, policy_id, role=None, resource=None, action=None):
    policy: Policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if role:
        policy.v0 = role
    if resource:
        policy.v1 = resource
    if action:
        policy.v2 = action
    db.commit()
    return policy


def unload_policy_line(line, model):
    """unloads a text line by removing a policy rule from the model."""

    if line == "":
        return

    if line[:1] == "#":
        return

    stack = []
    tokens = []
    for c in line:
        if c == "[" or c == "(":
            stack.append(c)
            tokens[-1] += c
        elif c == "]" or c == ")":
            stack.pop()
            tokens[-1] += c
        elif c == "," and len(stack) == 0:
            tokens.append("")
        else:
            if len(tokens) == 0:
                tokens.append(c)
            else:
                tokens[-1] += c

    tokens = [x.strip() for x in tokens]

    key = tokens[0]
    sec = key[0]

    if sec not in model.model.keys():
        return

    if key not in model.model[sec].keys():
        return

    policy_to_remove = tokens[1:]

    # Find and remove the policy rule from the model's memory
    try:
        model.model[sec][key].policy.remove(policy_to_remove)
    except ValueError:
        # Handle the case where the policy rule is not found
        pass


def high_level_enforce(enforcer: casbin.Enforcer, user_id, resource, action):

    if enforcer.enforce(str(user_id), "workspace", action):
        return True
    if enforcer.enforce(str(user_id), resource, action):
        return True
    if enforcer.enforce(str(user_id), "app", action):
        return True


def get_all_action_permissions(
    db: Session, user_id: str, workspace_id: str, app_id: str = None
):
    enforcer = get_contexted_enforcer(db, workspace_id)

    permissions_dict = {"workspace_permissions": {}, "app_permissions": {}}
    # Go through allowed actions and check if user has permission to perform action on resource
    for action in ALLOWED_ACTIONS:
        if enforcer.enforce(str(user_id), "workspace", action):
            permissions_dict["workspace_permissions"][action] = True
        else:
            permissions_dict["workspace_permissions"][action] = False
        if app_id not in permissions_dict["app_permissions"]:
            permissions_dict["app_permissions"][action] = False

        if enforcer.enforce(str(user_id), app_id, action):
            permissions_dict["app_permissions"][action] = True
        if enforcer.enforce(str(user_id), "app", action):
            permissions_dict["app_permissions"][action] = True
    return permissions_dict
