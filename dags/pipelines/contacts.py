
from amo import get_table
import pandas as pd
import psycopg2
import requests

import json
from sqlalchemy import create_engine 
from load import loader



contacts =get_table("contacts")

contactsdf = pd.DataFrame(contacts)

contacts =['id','name','first_name','last_name','responsible_user_id','group_id','created_by','updated_by','created_at','updated_at','closest_task_at','is_deleted','is_unsorted','account_id','links_self.href','_embedded.tags']

contact_tayyor  =contactsdf.reindex(columns=contacts)

loader(contact_tayyor,'Contacts')

custom_fiel =[]
contact_values = []

for _,column in contactsdf.iterrows():
    for contact in column['custom_fields_values']:
        custom_fiel.append({
            'id':column.get('id'),
            'field_id':contact.get('field_id'),
            'field_name':contact.get('field_name'),
            'field_code':contact.get('field_code'),
            'field_type':contact.get('field_type'),
            'is_masked':contact.get('is_masked')
            

        })

        for abs in contact['values']:
            contact_values.append({
                'id':column.get('id'),
                'value':abs.get('value'),
                'enum_id':abs.get('enum_id'),
                'enum_code':abs.get('enum_code')

            })

custom_contact_fieldf =pd.DataFrame(custom_fiel)

loader(custom_contact_fieldf,"Custom_contact_field")

contact_valuesdf = pd.DataFrame(contact_values)

loader(contact_valuesdf,"Contact_values")