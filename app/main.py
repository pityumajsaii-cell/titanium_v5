from fastapi import FastAPI, BackgroundTasks
from app.services.orchestrator import create_github_repo, trigger_render_deploy, setup_stripe_product
import os

app = FastAPI(title="TITANIUM V5.2")

@app.get("/")
def status():
    return {"status": "ONLINE", "system": "TITANIUM V5.2"}

@app.post("/launch-saas")
def launch_saas(project_name: str, background_tasks: BackgroundTasks):
    repo_url = create_github_repo(project_name)
    if repo_url:
        stripe_id = setup_stripe_product(project_name)
        background_tasks.add_task(trigger_render_deploy, repo_url, project_name)
        return {"status": "success", "repo": repo_url, "stripe_price_id": stripe_id}
    return {"status": "error", "message": "Failed to create repo"}
