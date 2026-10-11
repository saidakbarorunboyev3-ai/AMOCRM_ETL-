from amo import get_table
import pandas as pd
import psycopg2
import requests

import json
from sqlalchemy import create_engine 
from load import loader

table = get_table("users")

users =pd.DataFrame(table)


not_object_cols = []

for col in users:                      
    if users[col].dtype != "object":   
        not_object_cols.append(col)


users_new = users[not_object_cols]   

users_newdf = pd.DataFrame(users_new)

loader(users_newdf,"Users")



rights_status = []
rights_status_rights = []

for _, user in users.iterrows():
    status_list = user["rights.status_rights"]

    
    if not isinstance(status_list, list):
        continue

    for st in status_list:
        rights_status.append({
            "id": user["id"],
            "entity_type": st.get("entity_type"),
            "pipeline_id": st.get("pipeline_id"),
            "status_id": st.get("status_id"),
        })

        rights = st.get("rights", {})       
        rights_status_rights.append({
            "id": user["id"],
            "pipeline_id": st.get("pipeline_id"),
            "status_id": st.get("status_id"),
            "view": rights.get("view"),
            "edit": rights.get("edit"),
            "delete": rights.get("delete"),
            "export": rights.get("export"),
        })

rights_status_df = pd.DataFrame(rights_status).fillna(0)

loader(rights_status_df,"Rights_status")

rights_status_rights_df = pd.DataFrame(rights_status_rights).fillna(0)

loader(rights_status_rights_df,"Rights_status_rights")








    
   
