from pydantic import BaseModel
import os


class Settings(BaseModel):
    github_owner: str = ""
    github_repo: str = ""
    github_base_branch: str = "main"
    github_head_branch: str = "driftshield/auto-fix"
    github_token: str = ""
    github_api_timeout_seconds: int = 10
    auto_merge_low_risk: bool = False
    driftshield_api_key: str = ""


def get_settings() -> Settings:
    return Settings(
        github_owner=os.getenv("GITHUB_OWNER", ""),
        github_repo=os.getenv("GITHUB_REPO", ""),
        github_base_branch=os.getenv("GITHUB_BASE_BRANCH", "main"),
        github_head_branch=os.getenv("GITHUB_HEAD_BRANCH", "driftshield/auto-fix"),
        github_token=os.getenv("GITHUB_TOKEN", ""),
        github_api_timeout_seconds=int(os.getenv("GITHUB_API_TIMEOUT_SECONDS", "10")),
        auto_merge_low_risk=os.getenv("AUTO_MERGE_LOW_RISK", "false").lower() == "true",
        driftshield_api_key=os.getenv("DRIFTSHIELD_API_KEY", ""),
    )
