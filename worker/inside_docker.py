import pandas as pd
import redis
from dotenv import load_dotenv

from dropbase.helpers.dataframe import to_dtable
from dropbase.worker.run_python_class import run

load_dotenv()


pd.DataFrame.to_dtable = to_dtable


if __name__ == "__main__":
    # TODO: maybe move run logic here
    r = redis.Redis(host="host.docker.internal", port=6379, db=0)
    run(r)
