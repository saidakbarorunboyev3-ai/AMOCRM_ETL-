from amo import get_table
import pandas as pd
import psycopg2
import requests

import json
from sqlalchemy import create_engine 
from load import loader


df = get_table("leads")



Leads = pd.DataFrame(df)

kerakli = ["id","name","price","price_with_minor_units","responsible_user_id","group_id","status_id","pipeline_id","created_by","updated_by","created_at","updated_at","is_deleted","account_id"]

Leads_tayyor = Leads.reindex(columns=kerakli)


Leads_custom_field_values = []

lead_values =[]

for _, column in Leads.iterrows():
    for abs in column['custom_fields_values']:
        Leads_custom_field_values.append({
            "id":column.get("id"),
            "field_id":abs.get("field_id"),
            "field_name":abs.get("field_name"),
            "field_code":abs.get("field_code"),
            "field_type":abs.get("field_type"),
            "is_masked":abs.get("is_masked")

        })

        for asd in abs['values']:
            lead_values.append({
                "id":column.get("id"),
                "value":asd.get("value"),
                "enum_id":asd.get("enum_id"),
                "enum_code":asd.get("enum_code")
            })
   

lead_df =pd.DataFrame(Leads_tayyor)

loader(lead_df,"Leads")


Leads_custom_fielda_valuesDF =pd.DataFrame(Leads_custom_field_values)

loader(Leads_custom_fielda_valuesDF,"Leads_custom_fiel_values")


Lead_valuesDF = pd.DataFrame(lead_values)

loader(Lead_valuesDF,"Lead_values")

