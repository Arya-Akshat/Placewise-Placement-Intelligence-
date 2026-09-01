"""
Application Generator
=====================
Generates applications with correlated probabilistic status progressions.

Status flow:  APPLIED → SHORTLISTED → INTERVIEW → OFFERED → ACCEPTED
                                                           → DECLINED
                       → REJECTED (at any stage)
                       → WITHDRAWN

Correlation model (all probabilistic, no hard cutoffs):
  - shortlist_prob: sigmoid(cgpa_z*0.6 + skill_match*0.4 + internship_bonus)
  - interview_prob: P(interview | shortlisted) = 0.72 base
  - offer_prob:     sigmoid(interview_score*0.7 + skill_match*0.3) * selectivity
  - accept_prob:    0.82 base, lower if student has competing offers
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta
from .base_generator import BaseGenerator
from ..rules.correlation_rules import sigmoid, company_selectivity_factor


class ApplicationGenerator(BaseGenerator):
    """Generates applications table with correlated status progressions."""

    def generate(
        self,
        students: pd.DataFrame,
        jobs: pd.DataFrame,
        student_skills: pd.DataFrame | None = None,
        internships: pd.DataFrame | None = None,
    ) -> pd.DataFrame:
        """
        Parameters
        ----------
        students        : silver.students DataFrame
        jobs            : job postings DataFrame (from JobGenerator)
        student_skills  : optional — used to compute skill_match boost
        internships     : optional — used to compute internship_bonus
        """
        # Pre-compute internship counts per student for efficiency
        internship_counts: dict[str, int] = {}
        if internships is not None and not internships.empty:
            internship_counts = (
                internships.groupby("student_id")["internship_id"].count().to_dict()
            )

        # Pre-compute average skill proficiency per student
        skill_avg: dict[str, float] = {}
        if student_skills is not None and not student_skills.empty:
            skill_avg = (
                student_skills.groupby("student_id")["proficiency_score"].mean().to_dict()
            )

        records = []
        n_jobs = len(jobs)

        for i, (_, job) in enumerate(jobs.iterrows()):
            if i % max(1, n_jobs // 10) == 0:
                print(f"  Applications: {i}/{n_jobs} job postings processed …")

            # Eligibility filter
            eligible = students[
                (students["cgpa"] >= job.get("min_cgpa", 0.0))
                & (students["backlogs"] <= job.get("max_backlogs", 999))
            ]
            if eligible.empty:
                continue

            # Application probability varies by job attractiveness
            openings = max(1, job.get("openings", 5))
            # Jobs with more openings draw more applicants; cap at 0.6
            attract_factor = min(0.2, openings / 500.0)
            base_apply_prob = 0.25 + attract_factor

            for _, stu in eligible.iterrows():
                sid = stu["student_id"]

                # Role match bonus
                role_bonus = 0.15 if stu.get("preferred_role") == job.get("role_name") else 0.0
                apply_prob = min(0.75, base_apply_prob + role_bonus)

                if self.rng.random() >= apply_prob:
                    continue  # student did not apply

                # ── Application date ──────────────────────────────────────
                posting_date = job.get("posting_date", date(2024, 8, 1))
                if isinstance(posting_date, str):
                    posting_date = date.fromisoformat(posting_date)
                deadline = job.get("application_deadline", posting_date + timedelta(days=30))
                if isinstance(deadline, str):
                    deadline = date.fromisoformat(deadline)
                days_range = max(1, (deadline - posting_date).days)
                app_date = posting_date + timedelta(days=int(self.rng.integers(0, days_range)))

                # ── Shortlist probability ─────────────────────────────────
                cgpa_z       = (float(stu.get("cgpa", 7.0)) - 7.2) / 0.8
                intern_bonus = min(0.15, internship_counts.get(sid, 0) * 0.05)
                sk_norm      = (skill_avg.get(sid, 50.0) - 50.0) / 25.0  # z-score approx
                p_shortlist  = sigmoid(cgpa_z * 0.55 + sk_norm * 0.35 + intern_bonus)
                p_shortlist  = float(np.clip(p_shortlist, 0.05, 0.85))

                status       = "APPLIED"
                withdrawn_dt = None
                rejection_reason = None

                # Withdrawn before decision (5%)
                if self.rng.random() < 0.05:
                    status = "WITHDRAWN"
                    withdrawn_dt = app_date + timedelta(days=int(self.rng.integers(1, 20)))
                elif self.rng.random() < p_shortlist:
                    status = "SHORTLISTED"

                    # ── Interview ─────────────────────────────────────────
                    if self.rng.random() < 0.72:
                        status = "INTERVIEW"

                        # ── Offer ─────────────────────────────────────────
                        selectivity = company_selectivity_factor(
                            job.get("company_type", "SERVICES"),
                            float(job.get("package_median_lpa", 8.0)),
                        )
                        mock_interview_score = float(np.clip(
                            self.rng.normal(
                                60 + cgpa_z * 8 + sk_norm * 6,
                                12
                            ), 0, 100
                        ))
                        p_offer = sigmoid(
                            mock_interview_score / 100.0 * 2.5 - 1.0
                        ) * selectivity
                        p_offer = float(np.clip(p_offer, 0.02, 0.80))

                        if self.rng.random() < p_offer:
                            status = "OFFERED"

                            # ── Acceptance ───────────────────────────────
                            if self.rng.random() < 0.82:
                                status = "ACCEPTED"
                            else:
                                status = "DECLINED"
                        else:
                            rejection_reason = "Interview not cleared"
                    else:
                        rejection_reason = "Not selected post shortlist"
                else:
                    rejection_reason = "Not shortlisted"
                    status = "REJECTED"

                records.append({
                    "application_id":    self.generate_id("app", f"{sid}_{job.get('job_posting_id','')}"),
                    "student_id":        sid,
                    "job_posting_id":    job.get("job_posting_id", ""),
                    "application_date":  str(app_date),
                    "application_status": status,
                    "withdrawn_date":    str(withdrawn_dt) if withdrawn_dt else None,
                    "rejection_reason":  rejection_reason,
                    "source":            self.rng.choice(
                        ["CAMPUS_PORTAL", "DIRECT", "REFERRAL", "EMAIL"], p=[0.6, 0.2, 0.15, 0.05]
                    ),
                })

        df = pd.DataFrame(records)
        print(f"  Generated {len(df)} applications.")
        return df
