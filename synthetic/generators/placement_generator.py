import pandas as pd
from .base_generator import BaseGenerator

class PlacementGenerator(BaseGenerator):
    def generate(self, offers, applications, students):
        data = []
        accepted = offers[offers['offer_status'] == 'ACCEPTED']
        acc_app = pd.merge(accepted, applications, on='application_id')
        
        for i, (_, row) in enumerate(acc_app.iterrows()):
            data.append({
                'placement_id': self.generate_id('plc', row['offer_id']),
                'offer_id': row['offer_id'],
                'student_id': row['student_id'],
                'placement_type': self.rng.choice(['FULL_TIME', 'INTERNSHIP_TO_FULL_TIME', 'PRE_PLACEMENT_OFFER'], p=[0.7, 0.2, 0.1])
            })
            students.loc[students['student_id'] == row['student_id'], 'placement_status'] = 'PLACED'
            if i % max(1, len(acc_app) // 10) == 0:
                print(f"Placement generation: {i}/{len(acc_app)}")
        return pd.DataFrame(data)
