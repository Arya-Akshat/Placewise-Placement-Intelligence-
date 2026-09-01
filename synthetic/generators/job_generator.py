import pandas as pd
from .base_generator import BaseGenerator
from distributions.stats import right_skewed_salary

class JobGenerator(BaseGenerator):
    def generate(self, num_postings, companies, departments):
        data = []
        roles = ['software_engineering', 'data_engineering', 'frontend', 'backend', 'data_analyst', 'machine_learning']
        dept_ids = departments['department_id'].tolist()
        
        for i in range(num_postings):
            comp = companies.sample(n=1, random_state=self.rng.bit_generator).iloc[0]
            role = self.rng.choice(roles)
            median_ctc = 15.0 if comp['company_type'] == 'PRODUCT' else 6.0
            ctc = float(right_skewed_salary(0, median_ctc, 1, self.rng.bit_generator)[0])
            
            data.append({
                'job_id': self.generate_id('job', f"{comp['company_id']}_{role}_{i}"),
                'company_id': comp['company_id'],
                'role': role,
                'min_cgpa': 7.5 if comp['company_type'] == 'PRODUCT' else 6.0,
                'max_backlogs': 0 if comp['company_type'] == 'PRODUCT' else 2,
                'ctc_lpa': ctc,
                'openings': int(self.rng.poisson(10 if comp['company_type'] == 'SERVICES' else 3)) + 1
            })
            if i % max(1, num_postings // 10) == 0:
                print(f"Job posting generation: {i}/{num_postings}")
        return pd.DataFrame(data)
