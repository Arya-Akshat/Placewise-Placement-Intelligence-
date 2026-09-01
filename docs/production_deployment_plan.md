# Placewise Production Deployment & Cloud Architecture Plan

This document outlines the deployment roadmap to promote Placewise from local verification to institutional enterprise production.

---

## 1. Cloud Infrastructure & Hosting
- **Containerization**: Deploy FastAPI backend as a stateless container on AWS ECS Fargate / Azure Container Apps / Google Cloud Run.
- **Frontend Delivery**: Serve Vite static production bundle via CloudFront / Azure CDN / Cloudflare.
- **Persistence**: Managed PostgreSQL / RDS for conversation history and user session management.

---

## 2. Secrets Management
- Use AWS Secrets Manager / Azure Key Vault / HashiCorp Vault to inject:
  - `DATABRICKS_HOST`
  - `DATABRICKS_TOKEN` (Rotated Service Principal OAuth M2M Token)
  - `DATABRICKS_GENIE_SPACE_ID`
  - `DATABASE_URL`

---

## 3. Institutional Authentication & RBAC
- Integrate FastAPI dependency `get_current_user()` with University SAML 2.0 / Okta / Azure AD OIDC.
- Role-Based Access Control:
  - **Student**: View personal placement readiness, personalized skill gaps, and eligible job postings.
  - **Placement Officer / Admin**: Institutional placement rates, recruiter hiring analytics, and candidate shortlisting.
  - **Recruiter**: Job posting applicant pipelines and candidate match rankings.
