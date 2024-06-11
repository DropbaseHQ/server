import json

from dropbase.schemas.files import UpdateFile
from server.controllers.page_controller import PageController


def update_main_file(req: UpdateFile):
    # if properties.json, validate properties
    if req.file_name == "properties.json":
        pageController = PageController(req.app_name, req.page_name)
        pageController.update_page_properties(json.loads(req.code))
    else:
        # TODO: backup file
        file_path = f"workspace/{req.app_name}/{req.page_name}/{req.file_name}"
        with open(file_path, "w") as f:
            f.write(req.code)
    return {"message": f"File {req.file_name} updated successfully"}
