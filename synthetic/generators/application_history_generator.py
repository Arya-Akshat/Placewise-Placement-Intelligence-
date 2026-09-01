import pandas as pd
from .base_generator import BaseGenerator

class ApplicationHistoryGenerator(BaseGenerator):
    def generate(self, applications):
        data = []
        for i, (_, row) in enumerate(applications.iterrows()):
            data.append({
                'history_id': self.generate_id('hist', f"{row['application_id']}_initial"),
                'application_id': row['application_id'],
                'status': 'APPLIED'
            })
            if row['status'] != 'APPLIED':
                data.append({
                    'history_id': self.generate_id('hist', f"{row['application_id']}_final"),
                    'application_id': row['application_id'],
                    'status': row['status']
                })
            if i % max(1, len(applications) // 10) == 0:
                print(f"Application History generation: {i}/{len(applications)}")
        return pd.DataFrame(data)
