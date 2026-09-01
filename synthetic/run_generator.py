import argparse
import os
import yaml
from generators.department_generator import DepartmentGenerator
from generators.company_generator import CompanyGenerator
from generators.skill_generator import SkillGenerator
from generators.student_generator import StudentGenerator
from generators.student_skill_generator import StudentSkillGenerator
from generators.project_generator import ProjectGenerator
from generators.internship_generator import InternshipGenerator
from generators.job_generator import JobGenerator
from generators.application_generator import ApplicationGenerator
from generators.interview_generator import InterviewGenerator
from generators.offer_generator import OfferGenerator
from generators.placement_generator import PlacementGenerator
from generators.application_history_generator import ApplicationHistoryGenerator

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', choices=['small_demo', 'medium_demo', 'large_demo'], default='small_demo')
    parser.add_argument('--output', default='data/synthetic')
    parser.add_argument('--format', choices=['csv', 'parquet', 'delta'], default='csv')
    parser.add_argument('--validate', action='store_true')
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    
    with open('config/profiles.yaml', 'r') as f:
        config = yaml.safe_load(f)['profiles'][args.profile]
        
    seed = config['seed']
    print(f"Running profile: {args.profile} with seed {seed}")
    
    dept_gen = DepartmentGenerator(seed, config)
    depts = dept_gen.generate()
    depts.to_csv(f"{args.output}/departments.csv", index=False)
    
    comp_gen = CompanyGenerator(seed, config)
    companies = comp_gen.generate(config['companies'])
    companies.to_csv(f"{args.output}/companies.csv", index=False)
    
    skill_gen = SkillGenerator(seed, config)
    skills = skill_gen.generate('config/skill_profiles.yaml')
    skills.to_csv(f"{args.output}/skills.csv", index=False)
    
    stu_gen = StudentGenerator(seed, config)
    students = stu_gen.generate(config['students'], depts)
    
    stu_skill_gen = StudentSkillGenerator(seed, config)
    student_skills = stu_skill_gen.generate(students, skills, 'config/skill_profiles.yaml')
    student_skills.to_csv(f"{args.output}/student_skills.csv", index=False)
    
    proj_gen = ProjectGenerator(seed, config)
    projects = proj_gen.generate(students)
    projects.to_csv(f"{args.output}/projects.csv", index=False)
    
    int_gen = InternshipGenerator(seed, config)
    internships = int_gen.generate(students, companies)
    internships.to_csv(f"{args.output}/internships.csv", index=False)
    
    job_gen = JobGenerator(seed, config)
    jobs = job_gen.generate(config['job_postings'], companies, depts)
    jobs.to_csv(f"{args.output}/jobs.csv", index=False)
    
    app_gen = ApplicationGenerator(seed, config)
    applications = app_gen.generate(students, jobs)
    
    intv_gen = InterviewGenerator(seed, config)
    interviews = intv_gen.generate(applications, students, companies, jobs)
    interviews.to_csv(f"{args.output}/interviews.csv", index=False)
    
    off_gen = OfferGenerator(seed, config)
    offers = off_gen.generate(applications, jobs)
    offers.to_csv(f"{args.output}/offers.csv", index=False)
    
    plc_gen = PlacementGenerator(seed, config)
    placements = plc_gen.generate(offers, applications, students)
    placements.to_csv(f"{args.output}/placements.csv", index=False)
    
    # Save applications and students after updates
    applications.to_csv(f"{args.output}/applications.csv", index=False)
    students.to_csv(f"{args.output}/students.csv", index=False)
    
    hist_gen = ApplicationHistoryGenerator(seed, config)
    history = hist_gen.generate(applications)
    history.to_csv(f"{args.output}/application_history.csv", index=False)
    
    print("Generation complete!")
