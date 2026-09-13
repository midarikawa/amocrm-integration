import gspread
from google.oauth2.service_account import Credentials
from config.config import Config

class GoogleSheetsClient:
    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.creds = Credentials.from_service_account_file(
            Config.GOOGLE_SERVICE_ACCOUNT_FILE,
            scopes=self.scopes
        )
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open_by_key(Config.GOOGLE_SHEETS_ID)
        self.specialists_worksheet = self.sheet.sheet1

        #      
        try:
            self.schedule_worksheet = self.sheet.worksheet('')
        except:
            self.schedule_worksheet = self.sheet.add_worksheet(title='', rows=1000, cols=15)
            self._init_schedule_sheet()

    def get_all_specialists(self):
        """    """
        try:
            records = self.specialists_worksheet.get_all_records()
            return records
        except Exception as e:
            print(f"  : {e}")
            return []

    def get_specialist_by_id(self, specialist_id):
        """   ID"""
        specialists = self.get_all_specialists()
        for specialist in specialists:
            if specialist.get('ID') == specialist_id:
                return specialist
        return None

    def get_specialist_by_telegram_id(self, telegram_id):
        """   Telegram ID"""
        specialists = self.get_all_specialists()
        for specialist in specialists:
            if str(specialist.get('Telegram ID')) == str(telegram_id):
                return specialist
        return None

    def get_active_specialists(self):
        """   """
        specialists = self.get_all_specialists()
        return [s for s in specialists if s.get('', '').lower() == '']

    def add_specialist(self, name, telegram_id, specialization=''):
        """  """
        try:
            #   ID
            specialists = self.get_all_specialists()
            last_id = max([s.get('ID', 0) for s in specialists], default=0)
            new_id = last_id + 1

            #   
            row = [new_id, name, telegram_id, '', specialization]
            self.specialists_worksheet.append_row(row)
            return new_id
        except Exception as e:
            print(f"  : {e}")
            return None

    def update_specialist_status(self, specialist_id, status):
        """  """
        try:
            cell = self.specialists_worksheet.find(str(specialist_id))
            if cell:
                #    4-  (D)
                self.specialists_worksheet.update_cell(cell.row, 4, status)
                return True
            return False
        except Exception as e:
            print(f"   : {e}")
            return False

    def delete_specialist(self, specialist_id):
        """  (  )"""
        return self.update_specialist_status(specialist_id, '')

    def get_available_specialists(self, specialization=None):
        """   (   )"""
        active = self.get_active_specialists()

        if specialization:
            #   
            active = [s for s in active if specialization.lower() in s.get('', '').lower()]

        return active

    def create_specialists_sheet(self):
        """    (  )"""
        try:
            # ,   
            headers = self.specialists_worksheet.row_values(1)

            if not headers or headers[0] != 'ID':
                #  
                headers = ['ID', '', 'Telegram ID', '', '']
                self.specialists_worksheet.update('A1:E1', [headers])

                #   ( )
                self.specialists_worksheet.format('A1:E1', {
                    'textFormat': {'bold': True},
                    'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                })

                print("  ")
            return True
        except Exception as e:
            print(f"  : {e}")
            return False

    def get_specialist_stats(self, specialist_id):
        """   ( )"""
        specialist = self.get_specialist_by_id(specialist_id)
        if specialist:
            return {
                'id': specialist.get('ID'),
                'name': specialist.get(''),
                'status': specialist.get(''),
                'specialization': specialist.get('')
            }
        return None

    def _init_schedule_sheet(self):
        """  """
        headers = [
            'ID ', 'ID ', ' ', '', '',
            '', '', ' ', '', '   ()',
            '', '', 'AmoCRM ID', 'Notion ID', ''
        ]
        self.schedule_worksheet.update('A1:O1', [headers])
        self.schedule_worksheet.format('A1:O1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.8, 'green': 0.9, 'blue': 1.0}
        })

    def add_task_to_schedule(self, task_data, specialist_id, specialist_name, notion_page_id):
        """   """
        try:
            #   ID 
            records = self.schedule_worksheet.get_all_records()
            last_id = max([r.get('ID ', 0) for r in records], default=0)
            new_id = last_id + 1

            row = [
                new_id,
                specialist_id,
                specialist_name,
                task_data.get('visit_date', ''),
                task_data.get('visit_time', ''),
                task_data.get('address', ''),
                task_data.get('contact_phone', ''),
                task_data.get('work_type', ''),
                task_data.get('pests', ''),
                task_data.get('work_time', 60),
                task_data.get('cost', 0),
                '',
                task_data.get('lead_id', ''),
                notion_page_id,
                task_data.get('description', '')
            ]

            self.schedule_worksheet.append_row(row)
            print(f"  {new_id}     {specialist_name}")
            return new_id

        except Exception as e:
            print(f"     : {e}")
            return None

    def get_specialist_schedule(self, specialist_id, date=None):
        """       """
        try:
            records = self.schedule_worksheet.get_all_records()

            #   ID 
            schedule = [r for r in records if r.get('ID ') == specialist_id]

            #   ,   
            if date:
                schedule = [r for r in schedule if r.get('') == date]

            return schedule

        except Exception as e:
            print(f"  : {e}")
            return []

    def get_all_schedule(self, date=None):
        """    """
        try:
            records = self.schedule_worksheet.get_all_records()

            if date:
                records = [r for r in records if r.get('') == date]

            return records

        except Exception as e:
            print(f"  : {e}")
            return []

    def update_task_status(self, task_id, status):
        """    """
        try:
            cell = self.schedule_worksheet.find(str(task_id))
            if cell:
                #    12-  (L)
                self.schedule_worksheet.update_cell(cell.row, 12, status)
                return True
            return False
        except Exception as e:
            print(f"   : {e}")
            return False

    def get_specialist_workload(self, specialist_id, date):
        """     ( )"""
        schedule = self.get_specialist_schedule(specialist_id, date)
        total_minutes = sum(task.get('   ()', 60) for task in schedule)
        return total_minutes

