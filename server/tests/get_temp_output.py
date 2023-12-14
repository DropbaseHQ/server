import os
import pickle


def get_temp_output():
    temp_file_folder_location = os.path.join(os.getcwd(), ".temp")

    files = [
        f
        for f in os.listdir(temp_file_folder_location)
        if os.path.isfile(os.path.join(temp_file_folder_location, f))
    ]

    if not files:
        return None

    most_recent_file = None
    for f in files:
        change_time = os.path.getctime(os.path.join(temp_file_folder_location, f))
        if (
            most_recent_file is None
            or os.path.getctime(
                os.path.join(temp_file_folder_location, most_recent_file)
            )
            < change_time
        ):
            most_recent_file = f

    most_recent_file_path = os.path.join(
        temp_file_folder_location, str(most_recent_file)
    )
    with open(most_recent_file_path, "rb") as f:
        content = pickle.load(f)

    return content
