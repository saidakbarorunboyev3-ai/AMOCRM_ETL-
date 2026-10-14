import json
import pandas as pd
from amo import get_table
from load import loader


def stringify(df):
    """list/dict ustunlarni JSON matniga aylantiradi (PostgreSQL'ga yuklash uchun)."""
    for col in df.columns:
        df[col] = df[col].apply(
            lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x
        )
    return df


def load_if_not_empty(df, table_name):
    """Bo'sh jadvalni yuklamaydi, xato bermaydi."""
    if df.empty:
        print(f"{table_name}: ma'lumot yo'q, o'tkazib yuborildi")
        return
    loader(df, table_name)


# 1) Kontaktlarni olish
contactsdf = get_table("contacts")

if contactsdf.empty:
    print("Kontaktlar topilmadi, o'tkazib yuborildi")
    raise SystemExit(0)   # Airflow'da vazifa muvaffaqiyatli hisoblanadi

# 2) Asosiy jadval
columns = ['id', 'name', 'first_name', 'last_name', 'responsible_user_id', 'group_id',
           'created_by', 'updated_by', 'created_at', 'updated_at', 'closest_task_at',
           'is_deleted', 'is_unsorted', 'account_id', '_links.self.href']

contact_tayyor = contactsdf.reindex(columns=columns)

contact_tayyor = stringify(contact_tayyor)

loader(contact_tayyor, 'Contacts')

# 3) Qo'shimcha maydonlar (custom fields)
if 'custom_fields_values' not in contactsdf.columns:
    contactsdf['custom_fields_values'] = None

custom_fiel = []
contact_values = []

for _, row in contactsdf.iterrows():
    contact_id = row.get('id')
    fields = row.get('custom_fields_values')

    # bu kontaktda maydon yo'q (None / NaN), o'tkazib yuboramiz
    if not isinstance(fields, list):
        continue

    for field in fields:
        custom_fiel.append({
            'id': contact_id,
            'field_id': field.get('field_id'),
            'field_name': field.get('field_name'),
            'field_code': field.get('field_code'),
            'field_type': field.get('field_type'),
            'is_masked': field.get('is_masked'),
        })

        for val in field.get('values') or []:
            contact_values.append({
                'id': contact_id,
                'field_id': field.get('field_id'),
                'value': val.get('value'),
                'enum_id': val.get('enum_id'),
                'enum_code': val.get('enum_code'),
            })

load_if_not_empty(pd.DataFrame(custom_fiel), "Custom_contact_field")
load_if_not_empty(pd.DataFrame(contact_values), "Contact_values")
