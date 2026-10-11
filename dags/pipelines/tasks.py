from amo import get_table
import pandas as pd
import psycopg2
import requests

import json
from sqlalchemy import create_engine 
from load import loader


tasks =pd.DataFrame(get_table("tasks"))

loader(tasks,"Tasks")

        