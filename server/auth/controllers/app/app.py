from ...permissions.casbin_utils import high_level_enforce, get_contexted_enforcer
from ... import crud
from sqlalchemy.orm import Session


def filter_apps(db: Session, apps, workspace_id, user_id):
    filtered_apps = []
    workspace = crud.workspace.get_object_by_id_or_404(db, id=workspace_id)
    enforcer = get_contexted_enforcer(db, workspace_id)
    for app in apps:
        can_use = high_level_enforce(
            enforcer=enforcer,
            user_id=user_id,
            resource=str(app.get("id")),
            action="use",
        )
        if can_use:
            filtered_apps.append(app)
    return filtered_apps
