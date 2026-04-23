# FRIDAY DC Dashboard - Architecture (1 slide)

## Stack Diagram

User Browser -> ALB (public URL) -> ECS Fargate Service -> Streamlit Container  
ECS Task pulls image from ECR  
GitHub Actions on push to `main` builds Docker image and pushes to ECR, then triggers ECS redeploy  
Infrastructure is managed by Terraform (`infra/`)

## Data Sources

- `data/friday_internal_ops.csv` (operations, incidents, PUE, power)
- `data/market_trends.csv` (market capacity and trends)
- External references cited in Market page: Gartner, Statista, CBRE

## Key Design Decisions

- Multi-page Streamlit structure (Overview + 5 pages) for clearer live demo flow.
- Pure black visual system with fixed `logo_w.png` branding and custom editorial typography.
- Docker-first local testing to match ECS runtime behavior before AWS deployment.
