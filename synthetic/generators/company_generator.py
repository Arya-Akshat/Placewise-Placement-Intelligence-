import pandas as pd
from .base_generator import BaseGenerator

class CompanyGenerator(BaseGenerator):
    def generate(self, num_companies):
        data = []
        types = ['PRODUCT', 'SERVICES', 'STARTUP', 'CONSULTING', 'OTHER']
        probs = [0.25, 0.45, 0.15, 0.10, 0.05]
        
        for i in range(num_companies):
            c_name = self.faker.company()
            c_type = self.rng.choice(types, p=probs)
            data.append({
                'company_id': self.generate_id('comp', f"{c_name}_{i}"),
                'name': c_name,
                'company_type': c_type,
                'is_product_company': c_type == 'PRODUCT',
                'is_service_company': c_type == 'SERVICES',
                'is_startup': c_type == 'STARTUP',
                'founded_year': int(self.rng.integers(1980, 2023))
            })
            if i % max(1, num_companies // 10) == 0:
                print(f"Company generation: {i}/{num_companies}")
        return pd.DataFrame(data)
