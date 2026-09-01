import pandas as pd
from .base_generator import BaseGenerator

class DepartmentGenerator(BaseGenerator):
    def generate(self):
        depts = self.config.get('distributions', {}).get('departments', {})
        if not depts:
            depts = {'CSE': 0.32, 'ECE': 0.18, 'ME': 0.15, 'CE': 0.10, 'EE': 0.08, 'IT': 0.17}
        
        data = []
        for d in depts.keys():
            data.append({
                'department_id': self.generate_id('dept', d),
                'name': d,
                'weight': depts[d]
            })
        return pd.DataFrame(data)
