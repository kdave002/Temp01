from .models import DriftResponse
from .config import Settings


def build_pr_payload(response: DriftResponse, settings: Settings) -> dict:
    title = f"DriftShield: auto-repair ({response.risk} risk, impact {response.impact_score})"
    labels = ["driftshield", f"risk:{response.risk}"]

    return {
        "owner": settings.github_owner,
        "repo": settings.github_repo,
        "base": settings.github_base_branch,
        "title": title,
        "body": response.pr_body,
        "labels": labels,
        "draft": response.action_recommendation != "auto_merge_candidate",
    }
