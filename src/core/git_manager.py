import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from git import Repo
from git.objects import Commit


class GitManager:
    def __init__(self, repo_path: Path):
        self.repo = Repo(repo_path)
        self.current_user = self._get_current_user()

    def _get_current_user(self) -> str:
        return self.repo.config_reader().get_value('user', 'name')

    def _get_todays_commits(self) -> Dict[str, List[Commit]]:
        tz = datetime.now().astimezone().tzinfo
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz)
        formatted_date = current_date.strftime('%Y-%m-%d %H:%M:%S.%f')
        commits_by_branch = defaultdict(list)

        for branch in self.repo.heads:
            latest_commit = branch.commit
            if latest_commit.committed_datetime < current_date:
                continue
            for commit in self.repo.iter_commits(branch, since=formatted_date, author=self.current_user):
                commits_by_branch[branch.name].append(commit)

        return commits_by_branch

    @staticmethod
    def _extract_card_id(branch_name: str) -> Optional[int]:
        match = re.search(r'[^-]+-(\d+)', branch_name)
        return int(match.group(1)) if match else None

    def get_branches_with_commits(self) -> List[Tuple[str, int, List[str]]]:
        result = []
        commits_by_branch = self._get_todays_commits()
        for branch_name, commits in commits_by_branch.items():
            if commits and (card_id := self._extract_card_id(branch_name)):
                commit_messages = [commit.message.strip() for commit in commits]
                result.append((branch_name, card_id, commit_messages))
        return result
