import pandas as pd
from .base_generator import BaseGenerator

class InternshipGenerator(BaseGenerator):
    def generate(self, students, companies):
        data = []
        comp_ids = companies['company_id'].tolist()
        
        for i, (_, row) in enumerate(students.iterrows()):
            prob = 0.2 + (row['cgpa'] - 6.0) * 0.1
            if self.rng.random() < prob:
                data.append({
                    'internship_id': self.generate_id('int', f"{row['student_id']}_int"),
                    'student_id': row['student_id'],
                    'company_id': self.rng.choice(comp_ids),
                    'duration_months': int(self.rng.choice([1, 2, 3, 6])),
                    'conversion_to_ppo': self.rng.random() < 0.15
                })
            if i % max(1, len(students) // 10) == 0:
                print(f"Internship generation: {i}/{len(students)}")
        return pd.DataFrame(data)
