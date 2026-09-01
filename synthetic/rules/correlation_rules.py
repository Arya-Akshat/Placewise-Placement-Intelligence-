import numpy as np
from distributions.stats import sigmoid, company_selectivity

def get_shortlist_probability(cgpa_z_score, skill_match, internship_bonus):
    return sigmoid(cgpa_z_score * 0.6 + skill_match * 0.4 + internship_bonus)

def get_interview_pass_probability(interview_score, skill_match, selectivity_factor):
    base = sigmoid(interview_score * 0.7 + skill_match * 0.3)
    return base * selectivity_factor

# Alias used by application_generator
def company_selectivity_factor(company_type: str, median_ctc: float) -> float:
    """Returns selection rate multiplier (0-1). Higher CTC / PRODUCT → lower."""
    base = {"PRODUCT": 0.55, "SERVICES": 0.80, "STARTUP": 0.65,
            "CONSULTING": 0.70, "FINTECH": 0.60, "BANKING": 0.65,
            "CORE": 0.70, "GOVERNMENT": 0.75}
    type_factor = base.get(company_type.upper(), 0.70)
    # Higher CTC companies → lower acceptance (more selective)
    ctc_penalty = max(0.5, 1.0 - median_ctc / 60.0)
    return float(np.clip(type_factor * ctc_penalty, 0.10, 0.95))
