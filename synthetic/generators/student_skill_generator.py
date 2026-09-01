import pandas as pd
from .base_generator import BaseGenerator
import yaml

class StudentSkillGenerator(BaseGenerator):
    def generate(self, students, skills_df, skill_profiles_path):
        with open(skill_profiles_path, 'r') as f:
            profiles = yaml.safe_load(f)['role_skill_profiles']
        
        data = []
        for i, (_, row) in enumerate(students.iterrows()):
            role = row['preferred_role']
            cgpa = row['cgpa']
            prof_skills = profiles.get(role, {}).get('primary', [])
            
            for s in prof_skills:
                prof_score = min(100, max(0, int(self.rng.normal(cgpa * 10, 15))))
                source = self.rng.choice(['SELF', 'COURSE', 'PROJECT', 'CERTIFICATION'], p=[0.4, 0.3, 0.2, 0.1])
                if prof_score > 80 and self.rng.random() > 0.5:
                    source = 'CERTIFICATION'
                
                skill_id = self.generate_id('skill', s)
                data.append({
                    'student_id': row['student_id'],
                    'skill_id': skill_id,
                    'proficiency_score': prof_score,
                    'verification_source': source
                })
            if i % max(1, len(students) // 10) == 0:
                print(f"Student Skill generation: {i}/{len(students)}")
        return pd.DataFrame(data)
