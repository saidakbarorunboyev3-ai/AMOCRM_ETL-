import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from config import DB_URL

engine = create_engine(DB_URL)


def loader(df: pd.DataFrame, table_name, conn=engine):

    if df.empty:
        print("Bu jadval bo'sh")
        return

    df = df.copy()

    # list yoki dict bor ustunlarni aniqlab, JSONB turida saqlaymiz
    dtype_map = {}
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (dict, list))).any():
            dtype_map[col] = JSONB

    df.to_sql(
        table_name,
        conn,
        if_exists='replace',
        index=False,
        dtype=dtype_map,
        chunksize=1000,
    )
