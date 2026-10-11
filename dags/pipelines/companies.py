from amo import get_table
import pandas as pd
import psycopg2
import requests

import json
from sqlalchemy import create_engine 
from load import loader

companies=get_table("companies")

companiesdf =pd.DataFrame(companies)

kerakli = ['id','name','responsible_user_id','group_id','created_by','updated_by','created_at','updated_at','is_deleted','account_id']

companies_tayyor =companies.reindex(columns=kerakli)

companies_tayyordf =pd.DataFrame(companies_tayyor)

loader(companies_tayyordf,"Companies")


companies_custom_field_value = []

companies_custom_value =[]




for _, row in companiesdf.iterrows():
    company_id = row.get("id")
    fields = row.get("custom_fields_values")

    # agar fayldan o'qilgan bo'lsa, ro'yxat matn bo'lib kelishi mumkin
    if isinstance(fields, str):
        try:
            fields = ast.literal_eval(fields)
        except (ValueError, SyntaxError):
            fields = None

    # 1) Qator bo'sh (None / NaN / bo'sh ro'yxat) -> hamma joyga 0
    if not isinstance(fields, list) or len(fields) == 0:
        companies_custom_field_value.append({
            "id": company_id,
            "field_id": 0,
            "field_name": 0,
            "field_code": 0,
            "field_type": 0,
            "is_masked": 0,
        })
        companies_custom_value.append({
            "id": company_id,
            "field_id": 0,
            "value": 0,
            "enum_id": 0,
            "enum_code": 0,
        })
        continue

    # 2) Qator bo'sh emas -> mavjud ma'lumotni olamiz
    for comp in fields:
        companies_custom_field_value.append({
            "id": company_id,
            "field_id": comp.get("field_id"),
            "field_name": comp.get("field_name"),
            "field_code": comp.get("field_code"),
            "field_type": comp.get("field_type"),
            "is_masked": comp.get("is_masked"),
        })

        values = comp.get("values")

        # maydon bor, lekin qiymati yo'q -> 0
        if not isinstance(values, list) or len(values) == 0:
            companies_custom_value.append({
                "id": company_id,
                "field_id": comp.get("field_id"),
                "value": 0,
                "enum_id": 0,
                "enum_code": 0,
            })
            continue

        for ab in values:
            companies_custom_value.append({
                "id": company_id,
                "field_id": comp.get("field_id"),
                "value": ab.get("value", 0),
                "enum_id": ab.get("enum_id"),
                "enum_code": ab.get("enum_code"),
            })

companies_field_df = pd.DataFrame(companies_custom_field_value)
companies_value_df = pd.DataFrame(companies_custom_value)

loader(companies_field_df,"companies_field")

loader(companies_value_df,"companies_value")






    

    
 