import pandas as pd
from .base_generator import BaseGenerator
from rules.correlation_rules import get_interview_pass_probability
from distributions.stats import company_selectivity

class InterviewGenerator(BaseGenerator):
    def generate(self, applications, students, companies, jobs):
        data = []
        interview_apps = applications[applications['status'] == 'INTERVIEW']
        app_job = pd.merge(interview_apps, jobs, on='job_id')
        app_job_comp = pd.merge(app_job, companies, on='company_id')
        app_full = pd.merge(app_job_comp, students, on='student_id')
        
        for i, (_, row) in enumerate(app_full.iterrows()):
            rounds = int(self.rng.integers(1, 4))
            passed_all = True
            for r in range(rounds):
                int_score = self.rng.normal(row['cgpa'] / 10.0, 0.2)
                sel_factor = company_selectivity(row['company_type'], row['ctc_lpa'])
                p_pass = get_interview_pass_probability(int_score, 0.8, sel_factor)
                
                status = 'PASS' if self.rng.random() < p_pass else 'FAIL'
                data.append({
                    'interview_id': self.generate_id('intv', f"{row['application_id']}_{r}"),
                    'application_id': row['application_id'],
                    'round_number': r + 1,
                    'status': status
                })
                if status == 'FAIL':
                    passed_all = False
                    break
            
            if passed_all:
                applications.loc[applications['application_id'] == row['application_id'], 'status'] = 'OFFERED'
            else:
                applications.loc[applications['application_id'] == row['application_id'], 'status'] = 'REJECTED'
                
            if i % max(1, len(app_full) // 10) == 0:
                print(f"Interview generation: {i}/{len(app_full)}")
                
        return pd.DataFrame(data)
