import pandas as pd
import yaml
from .base_generator import BaseGenerator

class SkillGenerator(BaseGenerator):
    def generate(self, skill_profiles_path):
        with open(skill_profiles_path, 'r') as f:
            profiles = yaml.safe_load(f)
        
        skills = set()
        for role, cats in profiles.get('role_skill_profiles', {}).items():
            for cat, sks in cats.items():
                skills.update(sks)
        
        data = []
        for s in skills:
            data.append({
                'skill_id': self.generate_id('skill', s),
                'name': s
            })
        return pd.DataFrame(data)
