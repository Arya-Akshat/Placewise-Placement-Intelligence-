import hashlib
import numpy as np
from faker import Faker

class BaseGenerator:
    def __init__(self, seed, config):
        self.seed = seed
        self.config = config
        self.rng = np.random.default_rng(seed)
        self.faker = Faker(locale='en_IN')
        Faker.seed(seed)

    def generate_id(self, prefix, unique_string):
        hash_val = hashlib.md5(unique_string.encode('utf-8')).hexdigest()[:8]
        return f"{prefix}_{hash_val}"
