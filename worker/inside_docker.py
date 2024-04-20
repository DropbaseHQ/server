import pandas as pd
import redis
from dotenv import load_dotenv

from dropbase.helpers.dataframe import to_dtable

load_dotenv()


pd.DataFrame.to_dtable = to_dtable


if __name__ == "__main__":
    # TODO: only return stdout and traceback in dev mode

    r = redis.Redis(host="host.docker.internal", port=6379, db=0)
    response = {
        "stdout": "",
        "traceback": "",
        "message": "",
        "type": "",
        "status_code": 202,
    }
    from dropbase.worker.run_python_class import run

    run(r, response)
