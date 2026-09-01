import pandas as pd
from .base_generator import BaseGenerator

class ProjectGenerator(BaseGenerator):
    def generate(self, students):
        data = []
        for i, (_, row) in enumerate(students.iterrows()):
            num_projs = int(self.rng.integers(1, 4))
            for j in range(num_projs):
                ptype = self.rng.choice(['INDUSTRY', 'CAPSTONE', 'ACADEMIC', 'PERSONAL'])
                score = min(100, max(0, int(self.rng.normal(row['cgpa'] * 8, 10))))
                
                data.append({
                    'project_id': self.generate_id('proj', f"{row['student_id']}_{j}"),
                    'student_id': row['student_id'],
                    'project_type': ptype,
                    'industry_relevance_score': score,
                    'github_available': self.rng.random() < (0.7 if ptype == 'PERSONAL' else 0.4),
                    'deployed': self.rng.random() < 0.3
                })
            if i % max(1, len(students) // 10) == 0:
                print(f"Project generation: {i}/{len(students)}")
        return pd.DataFrame(data)
