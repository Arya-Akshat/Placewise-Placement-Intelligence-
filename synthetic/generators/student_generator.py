import pandas as pd
import numpy as np
from .base_generator import BaseGenerator
from distributions.stats import truncated_normal, correlated_variable

class StudentGenerator(BaseGenerator):
    def generate(self, num_students, departments):
        data = []
        cgpas = truncated_normal(7.2, 0.8, 4.0, 10.0, num_students, self.rng.bit_generator)
        percentages = correlated_variable(cgpas, 0.85, 0.1, num_students, self.rng.bit_generator) * 10 + 75
        percentages = np.clip(percentages, 40, 100)
        
        dept_ids = departments['department_id'].values
        dept_weights = departments['weight'].values
        
        roles = ['software_engineering', 'data_engineering', 'frontend', 'backend', 'data_analyst', 'machine_learning']
        
        for i in range(num_students):
            gender = self.rng.choice(['M', 'F'], p=[0.6, 0.4])
            name = self.faker.name_male() if gender == 'M' else self.faker.name_female()
            cgpa = float(cgpas[i])
            backlogs = max(0, int(self.rng.normal(2 - (cgpa - 4)*0.3, 1))) if cgpa < 7.0 else 0
            
            data.append({
                'student_id': self.generate_id('stu', f"{name}_{i}"),
                'name': name,
                'gender': gender,
                'department_id': self.rng.choice(dept_ids, p=dept_weights),
                'cgpa': cgpa,
                'percentage': float(percentages[i]),
                'backlogs': backlogs,
                'attendance_percentage': float(np.clip(self.rng.normal(cgpa * 8, 10), 50, 100)),
                'preferred_role': self.rng.choice(roles),
                'placement_status': 'ELIGIBLE' if backlogs == 0 and cgpa >= 6.0 else 'NOT_STARTED'
            })
            if i % max(1, num_students // 10) == 0:
                print(f"Student generation: {i}/{num_students}")
        return pd.DataFrame(data)
