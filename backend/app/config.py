from pydantic import BaseModel
import os


class Settings(BaseModel):
    github_owner: str = os.getenv("GITHUB_OWNER", "")
    github_repo: str = os.getenv("GITHUB_REPO", "")
    github_base_branch: str = os.getenv("GITHUB_BASE_BRANCH", "main")
    auto_merge_low_risk: bool = os.getenv("AUTO_MERGE_LOW_RISK", "false").lower() == "true"


def get_settings() -> Settings:
    return Settings()
