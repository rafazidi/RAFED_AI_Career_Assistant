import base64
import unittest
from unittest.mock import patch

from app.services.github import GitHubProject, GitHubProjectsService


class GitHubProjectsServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = GitHubProjectsService(
            owner="rafazidi",
            topic="portfolio",
            cache_ttl_seconds=300,
        )

    def test_lists_only_public_non_fork_repositories_with_topic(self) -> None:
        repositories = [
            {
                "name": "portfolio-app",
                "full_name": "rafazidi/portfolio-app",
                "description": "Career portfolio",
                "html_url": "https://github.com/rafazidi/portfolio-app",
                "language": "TypeScript",
                "updated_at": "2026-11-01T12:00:00Z",
                "topics": ["portfolio"],
                "private": False,
                "fork": False,
            },
            {
                "name": "unrelated",
                "full_name": "rafazidi/unrelated",
                "topics": [],
                "private": False,
                "fork": False,
            },
            {
                "name": "forked-portfolio",
                "full_name": "rafazidi/forked-portfolio",
                "topics": ["portfolio"],
                "private": False,
                "fork": True,
            },
            {
                "name": "private-portfolio",
                "full_name": "rafazidi/private-portfolio",
                "topics": ["portfolio"],
                "private": True,
                "fork": False,
            },
        ]
        with patch.object(self.service, "_request_json", return_value=repositories):
            projects = self.service.list_projects()

        self.assertEqual([project.name for project in projects], ["portfolio-app"])

    def test_readme_is_included_in_index_documents(self) -> None:
        readme = "# Portfolio App\n\nA bilingual data science portfolio."
        encoded_readme = base64.b64encode(readme.encode("utf-8")).decode("ascii")
        repository = {
            "name": "portfolio-app",
            "full_name": "rafazidi/portfolio-app",
            "description": "Career portfolio",
            "html_url": "https://github.com/rafazidi/portfolio-app",
            "language": "TypeScript",
            "updated_at": "2026-11-01T12:00:00Z",
            "topics": ["portfolio"],
            "private": False,
            "fork": False,
        }
        with patch.object(
            self.service,
            "_request_json",
            side_effect=[
                [repository],
                {"encoding": "base64", "content": encoded_readme},
            ],
        ):
            projects = self.service.list_projects()
            documents = self.service.knowledge_documents(projects)

        self.assertTrue(any("bilingual data science portfolio" in item["text"] for item in documents))
        self.assertTrue(all(item["source"] == "github" for item in documents))

    def test_repository_list_is_cached(self) -> None:
        with patch.object(self.service, "_request_json", return_value=[]) as request:
            self.service.list_projects()
            self.service.list_projects()

        request.assert_called_once()


class GitHubIndexSyncTests(unittest.TestCase):
    def test_projects_are_indexed_once_per_repository_update(self) -> None:
        from app import main

        project = GitHubProject(
            name="portfolio-app",
            full_name="rafazidi/portfolio-app",
            description="Career portfolio",
            html_url="https://github.com/rafazidi/portfolio-app",
            language="TypeScript",
            updated_at="2026-11-01T12:00:00Z",
            topics=("portfolio",),
        )
        documents = [
            {
                "id": "github-rafazidi-portfolio-app-0",
                "filename": "rafazidi/portfolio-app README",
                "text": "Career portfolio",
                "source": "github",
            }
        ]
        previous_signature = main._github_index_signature
        main._github_index_signature = None
        try:
            with (
                patch.object(main.github_projects, "list_projects", return_value=[project]),
                patch.object(main.github_projects, "knowledge_documents", return_value=documents),
                patch.object(main.rag_service, "replace_source_documents") as replace_documents,
            ):
                main._sync_github_projects()
                main._sync_github_projects()

            replace_documents.assert_called_once_with("github", documents)
        finally:
            main._github_index_signature = previous_signature


if __name__ == "__main__":
    unittest.main()
