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
    response = requests.post(ONBOARDING_WORKER_URL, headers=headers, json=data)
    if response.status_code != 200:
        return {"message": "Failed to submit onboarding request"}

    if request.notes:
        # send notes to slack
        feedback = f"Feedback from {request.first_name} {request.last_name} ({request.email})\n"
        feedback += request.notes
        response = requests.post(SLACK_WEBHOOK_FEEDBACK, headers=headers, json={"text": feedback})
        if response.status_code != 200:
            return {"message": "Failed to send notes to slack"}

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
