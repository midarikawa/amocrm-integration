import requests
import json
import time
from datetime import datetime, timedelta
from config.config import Config

class AmoCRMClient:
    def __init__(self):
        self.subdomain = Config.AMOCRM_SUBDOMAIN
        self.client_id = Config.AMOCRM_CLIENT_ID
        self.client_secret = Config.AMOCRM_CLIENT_SECRET
        self.redirect_uri = Config.AMOCRM_REDIRECT_URI
        self.access_token = Config.AMOCRM_ACCESS_TOKEN
        self.refresh_token = Config.AMOCRM_REFRESH_TOKEN
        self.base_url = f"https://{self.subdomain}.amocrm.ru/api/v4"

    def get_auth_url(self):
        """ URL  """
        return (
            f"https://www.amocrm.ru/oauth?"
            f"client_id={self.client_id}&"
            f"state=random_state&"
            f"mode=post_message"
        )

    def get_access_token(self, code):
        """ access token   """
        url = f"https://{self.subdomain}.amocrm.ru/oauth2/access_token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }

        response = requests.post(url, json=data)
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens['access_token']
            self.refresh_token = tokens['refresh_token']

            #    .env 
            self._save_tokens(tokens)
            return tokens
        else:
            raise Exception(f"  : {response.text}")

    def refresh_access_token(self):
        """ access token"""
        url = f"https://{self.subdomain}.amocrm.ru/oauth2/access_token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "redirect_uri": self.redirect_uri
        }

        response = requests.post(url, json=data)
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens['access_token']
            self.refresh_token = tokens['refresh_token']
            self._save_tokens(tokens)
            return tokens
        else:
            raise Exception(f"  : {response.text}")

    def _save_tokens(self, tokens):
        """   .env """
        #      
        print(f"Access Token: {tokens['access_token']}")
        print(f"Refresh Token: {tokens['refresh_token']}")
        print("    .env ")

    def _make_request(self, method, endpoint, data=None, params=None):
        """   API    """
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        response = requests.request(method, url, headers=headers, json=data, params=params)

        #   ,    
        if response.status_code == 401:
            self.refresh_access_token()
            headers["Authorization"] = f"Bearer {self.access_token}"
            response = requests.request(method, url, headers=headers, json=data, params=params)

        return response

    def get_lead(self, lead_id):
        """   ID"""
        response = self._make_request("GET", f"leads/{lead_id}", params={"with": "contacts"})
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"  : {response.text}")

    def get_lead_custom_fields(self, lead_id):
        """   """
        lead = self.get_lead(lead_id)
        custom_fields = {}

        if 'custom_fields_values' in lead.get('_embedded', {}).get('leads', [{}])[0]:
            for field in lead['_embedded']['leads'][0]['custom_fields_values']:
                field_name = field.get('field_name', '')
                field_value = field.get('values', [{}])[0].get('value', '')
                custom_fields[field_name] = field_value

        return custom_fields

    def extract_lead_data(self, lead_id):
        """     """
        lead_data = self.get_lead(lead_id)
        lead = lead_data.get('_embedded', {}).get('leads', [{}])[0]

        #  
        contacts = lead_data.get('_embedded', {}).get('contacts', [])
        contact_phone = ""
        contact_email = ""

        if contacts:
            contact = contacts[0]
            if 'custom_fields_values' in contact:
                for field in contact['custom_fields_values']:
                    if field.get('field_code') == 'PHONE':
                        contact_phone = field.get('values', [{}])[0].get('value', '')
                    elif field.get('field_code') == 'EMAIL':
                        contact_email = field.get('values', [{}])[0].get('value', '')

        #   
        custom_fields = {}
        if 'custom_fields_values' in lead:
            for field in lead['custom_fields_values']:
                field_name = field.get('field_name', '')
                field_value = field.get('values', [{}])[0].get('value', '')
                custom_fields[field_name] = field_value

        #   
        return {
            'lead_id': lead.get('id'),
            'name': lead.get('name', ''),
            'price': lead.get('price', 0),
            'address': custom_fields.get('', ''),
            'contact_phone': contact_phone,
            'contact_email': contact_email,
            'visit_date': custom_fields.get(' ', ''),
            'visit_time': custom_fields.get(' ', ''),
            'description': custom_fields.get('', ''),
            'payment_method': custom_fields.get(' ', ''),
            'segment': custom_fields.get('', ''),
            'object_type': custom_fields.get(' ', ''),
            'work_type': custom_fields.get(' ', ''),
            'pests': custom_fields.get('', ''),
            'avr_type': custom_fields.get(' ', ''),
            'specialists_count': int(custom_fields.get(' ', 1)),
            'work_time': int(custom_fields.get('   ()', 0)),
            'cost': float(custom_fields.get('', 0))
        }

    def update_lead_status(self, lead_id, status_id):
        """  """
        data = {
            "status_id": status_id
        }
        response = self._make_request("PATCH", f"leads/{lead_id}", data=data)
        return response.status_code == 200

    def add_note_to_lead(self, lead_id, note_text):
        """   """
        data = [{
            "entity_id": lead_id,
            "note_type": "common",
            "params": {
                "text": note_text
            }
        }]
        response = self._make_request("POST", f"leads/{lead_id}/notes", data=data)
        return response.status_code == 200
