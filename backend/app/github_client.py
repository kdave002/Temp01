import json
import socket
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import Settings


class GitHubPRCreateError(Exception):
    """Raised when PR creation via GitHub API fails."""


class GitHubPRCreateTimeout(GitHubPRCreateError):
    """Raised when the GitHub API request times out."""


def create_pull_request(pr_payload: dict, settings: Settings) -> dict:
    owner = pr_payload.get("owner")
    repo = pr_payload.get("repo")

    if not owner or not repo:
        raise GitHubPRCreateError("GitHub owner/repo must be configured")
    if not settings.github_token:
        raise GitHubPRCreateError("Missing GITHUB_TOKEN")

    api_payload = {
        "title": pr_payload["title"],
        "body": pr_payload["body"],
        "base": pr_payload["base"],
        "head": settings.github_head_branch,
        "draft": pr_payload.get("draft", True),
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    request = Request(
        url=url,
        method="POST",
        data=json.dumps(api_payload).encode("utf-8"),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {settings.github_token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "driftshield/0.5.0",
        },
    )

    try:
        with urlopen(request, timeout=settings.github_api_timeout_seconds) as response:
            response_body = response.read().decode("utf-8")
    except HTTPError as exc:
        details = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
        raise GitHubPRCreateError(f"GitHub API HTTP {exc.code}: {details}") from exc
    except (TimeoutError, socket.timeout) as exc:
        raise GitHubPRCreateTimeout("GitHub API request timed out") from exc
    except URLError as exc:
        if isinstance(exc.reason, TimeoutError):
            raise GitHubPRCreateTimeout("GitHub API request timed out") from exc
        raise GitHubPRCreateError(f"GitHub API connection failed: {exc.reason}") from exc
    except Exception as exc:  # pragma: no cover - defensive fallback
        raise GitHubPRCreateError(f"Unexpected GitHub API failure: {exc}") from exc

    try:
        return json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise GitHubPRCreateError("GitHub API returned invalid JSON") from exc
