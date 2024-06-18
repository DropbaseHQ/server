import json

import requests
from fastapi import APIRouter, Response

from dropbase.schemas.onboarding import Onboarding
from server.constants import DEFAULT_RESPONSES, ONBOARDING_URL, SLACK_WEBHOOK_FEEDBACK

router = APIRouter(prefix="/workspaces", tags=["workspace"], responses=DEFAULT_RESPONSES)


@router.get("/")
def get_workspace_properties(response: Response):
    with open("workspace/properties.json", "r") as f:
        workspace_properties = json.loads(f.read())
    apps = workspace_properties.get("apps", {})
    for app_name, app in apps.items():
        with open(f"workspace/{app_name}/properties.json", "r") as f:
            app_properties = json.loads(f.read())
        workspace_properties["apps"][app_name]["pages"] = (
            [{"name": p, "label": v.get("label")} for p, v in app_properties.items()],
        )

    return workspace_properties


@router.post("/onboarding")
def onboarding(request: Onboarding, response: Response):
    # send onboarding request to Dropbase worker
    headers = {"Content-Type": "application/json"}
    data = {
        "email": request.email,
        "firstName": request.first_name,
        "lastName": request.last_name,
        "company": request.company or "N/A",
        "userGroup": "Open Source",
        "source": "Dropbase Onboarding",
    }
    requests.post(ONBOARDING_URL, headers=headers, json=data)

    # update Dropbase on slack
    feedback = f"{request.first_name} {request.last_name} ({request.email})"
    if request.company:
        feedback += f" from {request.company}"
    if request.use_case:
        feedback += f"\nUse case: {request.use_case}"
    requests.post(SLACK_WEBHOOK_FEEDBACK, headers=headers, json={"text": feedback})

    # update workspace properties.json
    path = "workspace/properties.json"
    with open(path, "r") as f:
        ws_properties = json.loads(f.read())

    ws_properties["owner"] = {
        "email": request.email,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "company": request.company or "N/A",
    }
    with open(path, "w") as f:
        f.write(json.dumps(ws_properties, indent=2))

    return {"message": "Onboarding request submitted successfully"}
