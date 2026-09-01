import pandas as pd
from .base_generator import BaseGenerator

class OfferGenerator(BaseGenerator):
    def generate(self, applications, jobs):
        data = []
        offered_apps = applications[applications['status'] == 'OFFERED']
        app_job = pd.merge(offered_apps, jobs, on='job_id')
        
        for i, (_, row) in enumerate(app_job.iterrows()):
            offer_status = self.rng.choice(['ACCEPTED', 'DECLINED', 'EXPIRED'], p=[0.85, 0.10, 0.05])
            data.append({
                'offer_id': self.generate_id('off', row['application_id']),
                'application_id': row['application_id'],
                'ctc_offered': row['ctc_lpa'] * self.rng.normal(1.0, 0.05),
                'offer_status': offer_status
            })
            applications.loc[applications['application_id'] == row['application_id'], 'status'] = offer_status
            if i % max(1, len(app_job) // 10) == 0:
                print(f"Offer generation: {i}/{len(app_job)}")
        return pd.DataFrame(data)
