import psycopg2 
import pandas as pd
import json
from sqlalchemy import create_engine
from config import DB_URL

engine = create_engine(DB_URL)   


def loader(df: pd.DataFrame, table_name, conn=engine):

    if df.empty:
        print("Bu jadval bo'sh")
        return

    df.to_sql(table_name, conn, if_exists='replace', index=False)