import json

import requests
from fastapi import APIRouter, Response

from dropbase.schemas.onboarding import Onboarding
from server.constants import DEFAULT_RESPONSES, ONBOARDING_WORKER_URL, SLACK_WEBHOOK_FEEDBACK

router = APIRouter(prefix="/workspaces", tags=["workspace"], responses=DEFAULT_RESPONSES)


@router.get("/")
def get_workspace_properties(response: Response):
    path = "workspace/properties.json"
    with open(path, "r") as f:
        return json.loads(f.read())


@router.post("/onboarding")
def onboarding(request: Onboarding, response: Response):
    # implement onboarding logic here
    headers = {"Content-Type": "application/json"}
    data = {
        "email": request.email,
        "firstName": request.first_name,
        "lastName": request.last_name,
        "company": request.company or "N/A",
        "userGroup": "Open Source",
        "source": "Dropbase Onboarding",
    }
    requests.post(ONBOARDING_WORKER_URL, headers=headers, json=data)

    if request.use_case:
        # send notes to slack
        feedback = f"{request.first_name} {request.last_name} ({request.email})\n"
        if request.use_case:
            feedback += f"Use case: {request.use_case}"
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
