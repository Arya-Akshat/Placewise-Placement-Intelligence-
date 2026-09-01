import numpy as np
from scipy.stats import truncnorm, lognorm

def truncated_normal(mean, std, min_val, max_val, size, random_state=None):
    a, b = (min_val - mean) / std, (max_val - mean) / std
    return truncnorm.rvs(a, b, loc=mean, scale=std, size=size, random_state=random_state)

def right_skewed_salary(mean, median, size, random_state=None):
    rng = np.random.default_rng(random_state)
    shape = 0.5 
    scale = median
    # Using lognormal
    mu = np.log(scale)
    sigma = shape
    return rng.lognormal(mean=mu, sigma=sigma, size=size)

def correlated_variable(base_var, correlation, noise_std, size, random_state=None):
    rng = np.random.default_rng(random_state)
    base_norm = (base_var - np.mean(base_var)) / (np.std(base_var) + 1e-9)
    noise = rng.normal(0, noise_std, size)
    combined = correlation * base_norm + np.sqrt(1 - correlation**2) * noise
    return combined

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def company_selectivity(company_type, average_ctc):
    base_selectivity = {'PRODUCT': 0.3, 'SERVICES': 0.7, 'STARTUP': 0.5, 'CONSULTING': 0.4, 'OTHER': 0.6}
    type_factor = base_selectivity.get(company_type, 0.5)
    ctc_factor = max(0.1, 1 - (average_ctc / 50.0))
    return type_factor * ctc_factor
