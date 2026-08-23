from github_issue_pilot.github import GitHubHttpAdapter


def test_github_adapter_recognizes_only_the_configured_human_user() -> None:
    adapter = GitHubHttpAdapter("token", human_login="Daniel")
    try:
        assert adapter.is_configured_human("daniel", "User") is True
        assert adapter.is_configured_human("DANIEL", "user") is True
        assert adapter.is_configured_human("daniel", "Bot") is False
        assert adapter.is_configured_human("other-user", "User") is False
    finally:
        adapter.close()
