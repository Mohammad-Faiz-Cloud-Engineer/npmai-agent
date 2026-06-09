"""
tools_developer_cli.py
NPM Agent — Developer CLI Vertical
Covers: Git, GitHub, GitLab, Docker, PackageManager, VSCode,
        Terminal, Makefile, CMake, Debugger
"""

import os, sys, json, re, shutil, subprocess, tempfile, traceback, platform
from pathlib import Path
from typing import Optional

# ── auto-install deps ──────────────────────────────────────────────────────────
def _ensure(pkg: str, imp: str = None):
    n = imp or pkg
    try:
        __import__(n)
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", pkg, "-q"], check=False)

for _p, _i in [
    ("gitpython",    "git"),
    ("PyGithub",     "github"),
    ("python-gitlab","gitlab"),
    ("docker",       "docker"),
    ("psutil",       "psutil"),
    ("cryptography", "cryptography"),
]:
    _ensure(_p, _i)

# ── imports from agent_core ────────────────────────────────────────────────────
from agent_core import ToolResult, CredStore


# ══════════════════════════════════════════════════════════════════════════════
# 1. GitTool
# ══════════════════════════════════════════════════════════════════════════════
class GitTool:
    name = "git"
    description = (
        "Full local Git operations: init, clone, commit, push, pull, branch, "
        "merge, rebase, stash, tag, diff, log, blame, cherry-pick, submodules"
    )

    # ── helpers ────────────────────────────────────────────────────────────────
    @staticmethod
    def _run(args: list, cwd: str = None) -> tuple:
        """Returns (returncode, stdout+stderr)"""
        r = subprocess.run(
            ["git"] + args, cwd=cwd,
            capture_output=True, text=True
        )
        return r.returncode, (r.stdout + r.stderr).strip()

    # ── core ──────────────────────────────────────────────────────────────────
    @staticmethod
    def init(path: str) -> ToolResult:
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            rc, out = GitTool._run(["init"], cwd=path)
            return ToolResult(rc == 0, f"✓ Initialized repo at {path}\n{out}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ git init failed: {e}")

    @staticmethod
    def clone(url: str, dest: str) -> ToolResult:
        try:
            rc, out = GitTool._run(["clone", url, dest])
            return ToolResult(rc == 0, f"✓ Cloned {url} → {dest}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ git clone failed: {e}")

    @staticmethod
    def status(path: str) -> ToolResult:
        try:
            rc, out = GitTool._run(["status", "--short"], cwd=path)
            return ToolResult(rc == 0, out or "✓ Working tree clean", out)
        except Exception as e:
            return ToolResult(False, f"✗ git status failed: {e}")

    @staticmethod
    def add(path: str, files: str = ".") -> ToolResult:
        try:
            targets = files if isinstance(files, list) else [files]
            rc, out = GitTool._run(["add"] + targets, cwd=path)
            return ToolResult(rc == 0, f"✓ Staged: {files}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ git add failed: {e}")

    @staticmethod
    def commit(path: str, message: str, all: bool = True) -> ToolResult:
        try:
            args = ["commit", "-m", message]
            if all:
                args.insert(1, "-a")
            rc, out = GitTool._run(args, cwd=path)
            return ToolResult(rc == 0, f"✓ Committed: {message}\n{out}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ git commit failed: {e}")

    @staticmethod
    def push(path: str, remote: str = "origin", branch: str = "main") -> ToolResult:
        try:
            rc, out = GitTool._run(["push", remote, branch], cwd=path)
            return ToolResult(rc == 0, f"✓ Pushed to {remote}/{branch}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ git push failed: {e}")

    @staticmethod
    def pull(path: str, remote: str = "origin", branch: str = "main") -> ToolResult:
        try:
            rc, out = GitTool._run(["pull", remote, branch], cwd=path)
            return ToolResult(rc == 0, f"✓ Pulled {remote}/{branch}\n{out}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ git pull failed: {e}")

    @staticmethod
    def fetch(path: str, remote: str = "origin") -> ToolResult:
        try:
            rc, out = GitTool._run(["fetch", remote], cwd=path)
            return ToolResult(rc == 0, f"✓ Fetched {remote}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ git fetch failed: {e}")

    @staticmethod
    def create_branch(path: str, name: str) -> ToolResult:
        try:
            rc, out = GitTool._run(["checkout", "-b", name], cwd=path)
            return ToolResult(rc == 0, f"✓ Created and switched to branch '{name}'" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ create branch failed: {e}")

    @staticmethod
    def checkout(path: str, branch: str) -> ToolResult:
        try:
            rc, out = GitTool._run(["checkout", branch], cwd=path)
            return ToolResult(rc == 0, f"✓ Switched to '{branch}'" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ git checkout failed: {e}")

    @staticmethod
    def merge(path: str, branch: str) -> ToolResult:
        try:
            rc, out = GitTool._run(["merge", branch], cwd=path)
            return ToolResult(rc == 0, f"✓ Merged '{branch}'\n{out}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ git merge failed: {e}")

    @staticmethod
    def log(path: str, n: int = 10) -> ToolResult:
        try:
            fmt = "--pretty=format:%h %an %ar %s"
            rc, out = GitTool._run(["log", fmt, f"-{n}"], cwd=path)
            lines = out.splitlines()
            return ToolResult(rc == 0, f"✓ Last {len(lines)} commits", lines)
        except Exception as e:
            return ToolResult(False, f"✗ git log failed: {e}")

    @staticmethod
    def diff(path: str, file: str = None) -> ToolResult:
        try:
            args = ["diff"] + ([file] if file else [])
            rc, out = GitTool._run(args, cwd=path)
            return ToolResult(True, out or "✓ No differences", out)
        except Exception as e:
            return ToolResult(False, f"✗ git diff failed: {e}")

    @staticmethod
    def stash(path: str) -> ToolResult:
        try:
            rc, out = GitTool._run(["stash"], cwd=path)
            return ToolResult(rc == 0, f"✓ Stashed changes\n{out}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ git stash failed: {e}")

    @staticmethod
    def stash_pop(path: str) -> ToolResult:
        try:
            rc, out = GitTool._run(["stash", "pop"], cwd=path)
            return ToolResult(rc == 0, f"✓ Stash popped\n{out}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ git stash pop failed: {e}")

    @staticmethod
    def tag(path: str, name: str, message: str = "") -> ToolResult:
        try:
            args = ["tag", "-a", name, "-m", message or name]
            rc, out = GitTool._run(args, cwd=path)
            return ToolResult(rc == 0, f"✓ Tagged '{name}'" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ git tag failed: {e}")

    @staticmethod
    def reset(path: str, mode: str = "--soft", commit: str = "HEAD~1") -> ToolResult:
        try:
            rc, out = GitTool._run(["reset", mode, commit], cwd=path)
            return ToolResult(rc == 0, f"✓ Reset {mode} to {commit}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ git reset failed: {e}")

    @staticmethod
    def rebase(path: str, branch: str) -> ToolResult:
        try:
            rc, out = GitTool._run(["rebase", branch], cwd=path)
            return ToolResult(rc == 0, f"✓ Rebased onto '{branch}'\n{out}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ git rebase failed: {e}")

    @staticmethod
    def cherry_pick(path: str, commit: str) -> ToolResult:
        try:
            rc, out = GitTool._run(["cherry-pick", commit], cwd=path)
            return ToolResult(rc == 0, f"✓ Cherry-picked {commit}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ git cherry-pick failed: {e}")

    @staticmethod
    def blame(path: str, file: str) -> ToolResult:
        try:
            rc, out = GitTool._run(["blame", "--porcelain", file], cwd=path)
            return ToolResult(rc == 0, f"✓ Blame for {file}", out)
        except Exception as e:
            return ToolResult(False, f"✗ git blame failed: {e}")

    @staticmethod
    def show(path: str, commit: str) -> ToolResult:
        try:
            rc, out = GitTool._run(["show", commit], cwd=path)
            return ToolResult(rc == 0, out[:3000], out)
        except Exception as e:
            return ToolResult(False, f"✗ git show failed: {e}")

    @staticmethod
    def remote_add(path: str, name: str, url: str) -> ToolResult:
        try:
            rc, out = GitTool._run(["remote", "add", name, url], cwd=path)
            return ToolResult(rc == 0, f"✓ Remote '{name}' added → {url}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ remote add failed: {e}")

    @staticmethod
    def remote_list(path: str) -> ToolResult:
        try:
            rc, out = GitTool._run(["remote", "-v"], cwd=path)
            remotes = [l for l in out.splitlines() if l]
            return ToolResult(rc == 0, f"✓ {len(remotes)} remote entries", remotes)
        except Exception as e:
            return ToolResult(False, f"✗ remote list failed: {e}")

    @staticmethod
    def submodule_init(path: str) -> ToolResult:
        try:
            rc1, o1 = GitTool._run(["submodule", "init"], cwd=path)
            rc2, o2 = GitTool._run(["submodule", "update"], cwd=path)
            ok = rc1 == 0 and rc2 == 0
            return ToolResult(ok, f"✓ Submodules initialized\n{o1}\n{o2}" if ok else f"✗ {o1}\n{o2}")
        except Exception as e:
            return ToolResult(False, f"✗ submodule init failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# 2. GitHubTool (full API)
# ══════════════════════════════════════════════════════════════════════════════
class GitHubTool:
    name = "github"
    description = (
        "Full GitHub API: repos, issues, PRs, files, releases, Actions, "
        "branches, collaborators, gists, stars, forks"
    )

    @staticmethod
    def _gh(cred_key: str = "github"):
        from github import Github
        token = CredStore.load(cred_key).get("token", "")
        if not token:
            raise ValueError("No GitHub token. Save via CredStore.save('github', {'token':'...'}).")
        return Github(token)

    @staticmethod
    def create_repo(name: str, private: bool = True, description: str = "",
                    cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            user = gh.get_user()
            repo = user.create_repo(name=name, private=private, description=description, auto_init=True)
            return ToolResult(True, f"✓ Repo created: {repo.html_url}", {"url": repo.html_url, "full_name": repo.full_name})
        except Exception as e:
            return ToolResult(False, f"✗ create_repo failed: {e}")

    @staticmethod
    def delete_repo(repo: str, cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            gh.get_repo(repo).delete()
            return ToolResult(True, f"✓ Repo '{repo}' deleted")
        except Exception as e:
            return ToolResult(False, f"✗ delete_repo failed: {e}")

    @staticmethod
    def fork_repo(repo: str, cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            fork = gh.get_user().create_fork(gh.get_repo(repo))
            return ToolResult(True, f"✓ Forked → {fork.html_url}", {"url": fork.html_url})
        except Exception as e:
            return ToolResult(False, f"✗ fork_repo failed: {e}")

    @staticmethod
    def create_issue(repo: str, title: str, body: str = "",
                     labels: list = None, assignees: list = None,
                     cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            issue = gh.get_repo(repo).create_issue(
                title=title, body=body,
                labels=labels or [], assignees=assignees or []
            )
            return ToolResult(True, f"✓ Issue #{issue.number}: {issue.html_url}", {"number": issue.number, "url": issue.html_url})
        except Exception as e:
            return ToolResult(False, f"✗ create_issue failed: {e}")

    @staticmethod
    def close_issue(repo: str, number: int, cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            gh.get_repo(repo).get_issue(number).edit(state="closed")
            return ToolResult(True, f"✓ Issue #{number} closed")
        except Exception as e:
            return ToolResult(False, f"✗ close_issue failed: {e}")

    @staticmethod
    def list_issues(repo: str, state: str = "open", labels: list = None,
                    cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            kwargs = {"state": state}
            if labels:
                kwargs["labels"] = labels
            issues = gh.get_repo(repo).get_issues(**kwargs)
            data = [{"#": i.number, "title": i.title, "state": i.state, "url": i.html_url} for i in issues]
            return ToolResult(True, f"✓ {len(data)} issues", data)
        except Exception as e:
            return ToolResult(False, f"✗ list_issues failed: {e}")

    @staticmethod
    def create_pr(repo: str, title: str, body: str, head: str, base: str = "main",
                  cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            pr = gh.get_repo(repo).create_pull(title=title, body=body, head=head, base=base)
            return ToolResult(True, f"✓ PR #{pr.number}: {pr.html_url}", {"number": pr.number, "url": pr.html_url})
        except Exception as e:
            return ToolResult(False, f"✗ create_pr failed: {e}")

    @staticmethod
    def merge_pr(repo: str, number: int, method: str = "squash",
                 cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            pr = gh.get_repo(repo).get_pull(number)
            result = pr.merge(merge_method=method)
            return ToolResult(result.merged, f"✓ PR #{number} merged" if result.merged else f"✗ Merge failed: {result.message}")
        except Exception as e:
            return ToolResult(False, f"✗ merge_pr failed: {e}")

    @staticmethod
    def list_prs(repo: str, state: str = "open", cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            prs = gh.get_repo(repo).get_pulls(state=state)
            data = [{"#": p.number, "title": p.title, "head": p.head.ref, "base": p.base.ref, "url": p.html_url} for p in prs]
            return ToolResult(True, f"✓ {len(data)} PRs", data)
        except Exception as e:
            return ToolResult(False, f"✗ list_prs failed: {e}")

    @staticmethod
    def review_pr(repo: str, number: int, body: str, event: str = "COMMENT",
                  cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            pr = gh.get_repo(repo).get_pull(number)
            review = pr.create_review(body=body, event=event)
            return ToolResult(True, f"✓ Review submitted on PR #{number}", {"id": review.id})
        except Exception as e:
            return ToolResult(False, f"✗ review_pr failed: {e}")

    @staticmethod
    def push_file(repo: str, path: str, content: str,
                  message: str = "Update via NPM Agent",
                  cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            r = gh.get_repo(repo)
            try:
                existing = r.get_contents(path)
                r.update_file(path, message, content, existing.sha)
                return ToolResult(True, f"✓ Updated {path} in {repo}")
            except Exception:
                r.create_file(path, message, content)
                return ToolResult(True, f"✓ Created {path} in {repo}")
        except Exception as e:
            return ToolResult(False, f"✗ push_file failed: {e}")

    @staticmethod
    def delete_file(repo: str, path: str, message: str = "Delete via NPM Agent",
                    cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            r = gh.get_repo(repo)
            contents = r.get_contents(path)
            r.delete_file(path, message, contents.sha)
            return ToolResult(True, f"✓ Deleted {path} from {repo}")
        except Exception as e:
            return ToolResult(False, f"✗ delete_file failed: {e}")

    @staticmethod
    def get_file(repo: str, path: str, cred_key: str = "github") -> ToolResult:
        try:
            import base64
            gh = GitHubTool._gh(cred_key)
            f = gh.get_repo(repo).get_contents(path)
            content = base64.b64decode(f.content).decode(errors="replace")
            return ToolResult(True, f"✓ Got {path}", content)
        except Exception as e:
            return ToolResult(False, f"✗ get_file failed: {e}")

    @staticmethod
    def list_files(repo: str, path: str = "", cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            contents = gh.get_repo(repo).get_contents(path)
            files = [{"name": f.name, "type": f.type, "path": f.path} for f in contents]
            return ToolResult(True, f"✓ {len(files)} entries in '{path or '/'}'", files)
        except Exception as e:
            return ToolResult(False, f"✗ list_files failed: {e}")

    @staticmethod
    def create_release(repo: str, tag: str, name: str, body: str = "",
                       cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            rel = gh.get_repo(repo).create_git_release(tag=tag, name=name, message=body)
            return ToolResult(True, f"✓ Release '{name}' created: {rel.html_url}", {"url": rel.html_url})
        except Exception as e:
            return ToolResult(False, f"✗ create_release failed: {e}")

    @staticmethod
    def get_actions_status(repo: str, cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            runs = list(gh.get_repo(repo).get_workflow_runs())[:10]
            data = [{"id": r.id, "name": r.name, "status": r.status, "conclusion": r.conclusion} for r in runs]
            return ToolResult(True, f"✓ {len(data)} recent workflow runs", data)
        except Exception as e:
            return ToolResult(False, f"✗ get_actions_status failed: {e}")

    @staticmethod
    def trigger_workflow(repo: str, workflow_id: str, ref: str = "main",
                         cred_key: str = "github") -> ToolResult:
        try:
            import requests
            token = CredStore.load(cred_key).get("token", "")
            url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_id}/dispatches"
            r = requests.post(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
                              json={"ref": ref}, timeout=15)
            return ToolResult(r.status_code == 204, f"✓ Workflow triggered" if r.status_code == 204 else f"✗ {r.text}")
        except Exception as e:
            return ToolResult(False, f"✗ trigger_workflow failed: {e}")

    @staticmethod
    def list_branches(repo: str, cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            branches = [b.name for b in gh.get_repo(repo).get_branches()]
            return ToolResult(True, f"✓ {len(branches)} branches", branches)
        except Exception as e:
            return ToolResult(False, f"✗ list_branches failed: {e}")

    @staticmethod
    def protect_branch(repo: str, branch: str, cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            b = gh.get_repo(repo).get_branch(branch)
            b.edit_protection(required_approving_review_count=1)
            return ToolResult(True, f"✓ Branch '{branch}' protected")
        except Exception as e:
            return ToolResult(False, f"✗ protect_branch failed: {e}")

    @staticmethod
    def add_collaborator(repo: str, user: str, permission: str = "push",
                         cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            gh.get_repo(repo).add_to_collaborators(user, permission=permission)
            return ToolResult(True, f"✓ Added '{user}' as collaborator with '{permission}' permission")
        except Exception as e:
            return ToolResult(False, f"✗ add_collaborator failed: {e}")

    @staticmethod
    def create_gist(files: dict, description: str = "", public: bool = True,
                    cred_key: str = "github") -> ToolResult:
        try:
            from github import InputFileContent
            gh = GitHubTool._gh(cred_key)
            gist_files = {name: InputFileContent(content) for name, content in files.items()}
            gist = gh.get_user().create_gist(public=public, files=gist_files, description=description)
            return ToolResult(True, f"✓ Gist created: {gist.html_url}", {"url": gist.html_url})
        except Exception as e:
            return ToolResult(False, f"✗ create_gist failed: {e}")

    @staticmethod
    def get_user_info(username: str, cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            u = gh.get_user(username)
            data = {"login": u.login, "name": u.name, "bio": u.bio,
                    "public_repos": u.public_repos, "followers": u.followers}
            return ToolResult(True, f"✓ User info for '{username}'", data)
        except Exception as e:
            return ToolResult(False, f"✗ get_user_info failed: {e}")

    @staticmethod
    def star_repo(repo: str, cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            gh.get_user().add_to_starred(gh.get_repo(repo))
            return ToolResult(True, f"✓ Starred '{repo}'")
        except Exception as e:
            return ToolResult(False, f"✗ star_repo failed: {e}")

    @staticmethod
    def watch_repo(repo: str, cred_key: str = "github") -> ToolResult:
        try:
            gh = GitHubTool._gh(cred_key)
            gh.get_user().add_to_watched(gh.get_repo(repo))
            return ToolResult(True, f"✓ Now watching '{repo}'")
        except Exception as e:
            return ToolResult(False, f"✗ watch_repo failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# 3. GitLabTool
# ══════════════════════════════════════════════════════════════════════════════
class GitLabTool:
    name = "gitlab"
    description = (
        "Full GitLab API: projects, issues, merge requests, pipelines, "
        "jobs, files, branches, members"
    )

    @staticmethod
    def _gl(cred_key: str = "gitlab"):
        import gitlab
        c = CredStore.load(cred_key)
        url = c.get("url", "https://gitlab.com")
        token = c.get("token", "")
        if not token:
            raise ValueError("No GitLab token. Save via CredStore.save('gitlab', {'token':'...','url':'...'}).")
        gl = gitlab.Gitlab(url, private_token=token)
        gl.auth()
        return gl

    @staticmethod
    def create_project(name: str, visibility: str = "private",
                       cred_key: str = "gitlab") -> ToolResult:
        try:
            gl = GitLabTool._gl(cred_key)
            p = gl.projects.create({"name": name, "visibility": visibility})
            return ToolResult(True, f"✓ Project '{name}' created: {p.web_url}", {"id": p.id, "url": p.web_url})
        except Exception as e:
            return ToolResult(False, f"✗ create_project failed: {e}")

    @staticmethod
    def list_projects(cred_key: str = "gitlab") -> ToolResult:
        try:
            gl = GitLabTool._gl(cred_key)
            projects = gl.projects.list(owned=True)
            data = [{"id": p.id, "name": p.name, "url": p.web_url} for p in projects]
            return ToolResult(True, f"✓ {len(data)} projects", data)
        except Exception as e:
            return ToolResult(False, f"✗ list_projects failed: {e}")

    @staticmethod
    def get_project(id: int, cred_key: str = "gitlab") -> ToolResult:
        try:
            gl = GitLabTool._gl(cred_key)
            p = gl.projects.get(id)
            data = {"id": p.id, "name": p.name, "description": p.description,
                    "url": p.web_url, "default_branch": p.default_branch}
            return ToolResult(True, f"✓ Project {id}", data)
        except Exception as e:
            return ToolResult(False, f"✗ get_project failed: {e}")

    @staticmethod
    def create_issue(project_id: int, title: str, description: str = "",
                     labels: list = None, cred_key: str = "gitlab") -> ToolResult:
        try:
            gl = GitLabTool._gl(cred_key)
            p = gl.projects.get(project_id)
            issue = p.issues.create({"title": title, "description": description,
                                     "labels": labels or []})
            return ToolResult(True, f"✓ Issue #{issue.iid} created: {issue.web_url}", {"iid": issue.iid})
        except Exception as e:
            return ToolResult(False, f"✗ GitLab create_issue failed: {e}")

    @staticmethod
    def close_issue(project_id: int, iid: int, cred_key: str = "gitlab") -> ToolResult:
        try:
            gl = GitLabTool._gl(cred_key)
            p = gl.projects.get(project_id)
            issue = p.issues.get(iid)
            issue.state_event = "close"
            issue.save()
            return ToolResult(True, f"✓ Issue #{iid} closed")
        except Exception as e:
            return ToolResult(False, f"✗ close_issue failed: {e}")

    @staticmethod
    def create_mr(project_id: int, title: str, source: str, target: str,
                  description: str = "", cred_key: str = "gitlab") -> ToolResult:
        try:
            gl = GitLabTool._gl(cred_key)
            p = gl.projects.get(project_id)
            mr = p.mergerequests.create({"title": title, "source_branch": source,
                                         "target_branch": target, "description": description})
            return ToolResult(True, f"✓ MR #{mr.iid}: {mr.web_url}", {"iid": mr.iid, "url": mr.web_url})
        except Exception as e:
            return ToolResult(False, f"✗ create_mr failed: {e}")

    @staticmethod
    def merge_mr(project_id: int, iid: int, cred_key: str = "gitlab") -> ToolResult:
        try:
            gl = GitLabTool._gl(cred_key)
            mr = gl.projects.get(project_id).mergerequests.get(iid)
            mr.merge()
            return ToolResult(True, f"✓ MR #{iid} merged")
        except Exception as e:
            return ToolResult(False, f"✗ merge_mr failed: {e}")

    @staticmethod
    def list_pipelines(project_id: int, cred_key: str = "gitlab") -> ToolResult:
        try:
            gl = GitLabTool._gl(cred_key)
            pipelines = gl.projects.get(project_id).pipelines.list()
            data = [{"id": p.id, "status": p.status, "ref": p.ref} for p in pipelines[:20]]
            return ToolResult(True, f"✓ {len(data)} pipelines", data)
        except Exception as e:
            return ToolResult(False, f"✗ list_pipelines failed: {e}")

    @staticmethod
    def trigger_pipeline(project_id: int, ref: str = "main",
                         cred_key: str = "gitlab") -> ToolResult:
        try:
            gl = GitLabTool._gl(cred_key)
            pipeline = gl.projects.get(project_id).pipelines.create({"ref": ref})
            return ToolResult(True, f"✓ Pipeline #{pipeline.id} triggered on '{ref}'", {"id": pipeline.id})
        except Exception as e:
            return ToolResult(False, f"✗ trigger_pipeline failed: {e}")

    @staticmethod
    def get_pipeline_jobs(project_id: int, pipeline_id: int,
                          cred_key: str = "gitlab") -> ToolResult:
        try:
            gl = GitLabTool._gl(cred_key)
            pipeline = gl.projects.get(project_id).pipelines.get(pipeline_id)
            jobs = pipeline.jobs.list()
            data = [{"id": j.id, "name": j.name, "status": j.status, "stage": j.stage} for j in jobs]
            return ToolResult(True, f"✓ {len(data)} jobs in pipeline #{pipeline_id}", data)
        except Exception as e:
            return ToolResult(False, f"✗ get_pipeline_jobs failed: {e}")

    @staticmethod
    def retry_job(project_id: int, job_id: int, cred_key: str = "gitlab") -> ToolResult:
        try:
            gl = GitLabTool._gl(cred_key)
            job = gl.projects.get(project_id).jobs.get(job_id)
            job.retry()
            return ToolResult(True, f"✓ Job #{job_id} retried")
        except Exception as e:
            return ToolResult(False, f"✗ retry_job failed: {e}")

    @staticmethod
    def push_file(project_id: int, file_path: str, content: str,
                  message: str = "Update via NPM Agent", branch: str = "main",
                  cred_key: str = "gitlab") -> ToolResult:
        try:
            import base64
            gl = GitLabTool._gl(cred_key)
            p = gl.projects.get(project_id)
            encoded = base64.b64encode(content.encode()).decode()
            try:
                f = p.files.get(file_path=file_path, ref=branch)
                p.files.update(file_path=file_path, branch=branch,
                               content=encoded, commit_message=message, encoding="base64")
                return ToolResult(True, f"✓ Updated '{file_path}' on '{branch}'")
            except Exception:
                p.files.create({"file_path": file_path, "branch": branch,
                                "content": encoded, "commit_message": message, "encoding": "base64"})
                return ToolResult(True, f"✓ Created '{file_path}' on '{branch}'")
        except Exception as e:
            return ToolResult(False, f"✗ push_file failed: {e}")

    @staticmethod
    def list_branches(project_id: int, cred_key: str = "gitlab") -> ToolResult:
        try:
            gl = GitLabTool._gl(cred_key)
            branches = [b.name for b in gl.projects.get(project_id).branches.list()]
            return ToolResult(True, f"✓ {len(branches)} branches", branches)
        except Exception as e:
            return ToolResult(False, f"✗ list_branches failed: {e}")

    @staticmethod
    def create_branch(project_id: int, name: str, ref: str = "main",
                      cred_key: str = "gitlab") -> ToolResult:
        try:
            gl = GitLabTool._gl(cred_key)
            b = gl.projects.get(project_id).branches.create({"branch": name, "ref": ref})
            return ToolResult(True, f"✓ Branch '{name}' created from '{ref}'")
        except Exception as e:
            return ToolResult(False, f"✗ create_branch failed: {e}")

    @staticmethod
    def list_members(project_id: int, cred_key: str = "gitlab") -> ToolResult:
        try:
            gl = GitLabTool._gl(cred_key)
            members = gl.projects.get(project_id).members.list()
            data = [{"id": m.id, "username": m.username, "access_level": m.access_level} for m in members]
            return ToolResult(True, f"✓ {len(data)} members", data)
        except Exception as e:
            return ToolResult(False, f"✗ list_members failed: {e}")

    @staticmethod
    def add_member(project_id: int, user_id: int, access_level: int = 30,
                   cred_key: str = "gitlab") -> ToolResult:
        try:
            gl = GitLabTool._gl(cred_key)
            gl.projects.get(project_id).members.create({"user_id": user_id, "access_level": access_level})
            return ToolResult(True, f"✓ User {user_id} added with access level {access_level}")
        except Exception as e:
            return ToolResult(False, f"✗ add_member failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# 4. DockerTool
# ══════════════════════════════════════════════════════════════════════════════
class DockerTool:
    name = "docker"
    description = (
        "Full Docker operations: build, push, pull, run, exec, logs, "
        "networks, volumes, docker-compose, system prune"
    )

    @staticmethod
    def _client():
        import docker
        return docker.from_env()

    @staticmethod
    def _run_docker(args: list) -> tuple:
        r = subprocess.run(["docker"] + args, capture_output=True, text=True)
        return r.returncode, (r.stdout + r.stderr).strip()

    @staticmethod
    def build_image(path: str, tag: str, dockerfile: str = "Dockerfile",
                    build_args: dict = None) -> ToolResult:
        try:
            client = DockerTool._client()
            ba = build_args or {}
            image, logs = client.images.build(path=path, tag=tag, dockerfile=dockerfile, buildargs=ba, rm=True)
            log_text = "\n".join(l.get("stream", "") for l in logs if "stream" in l).strip()
            return ToolResult(True, f"✓ Image '{tag}' built\n{log_text[-500:]}", {"id": image.id})
        except Exception as e:
            return ToolResult(False, f"✗ build_image failed: {e}")

    @staticmethod
    def push_image(image: str, registry: str = "", cred_key: str = "docker") -> ToolResult:
        try:
            client = DockerTool._client()
            full_tag = f"{registry}/{image}" if registry else image
            result = client.images.push(full_tag)
            return ToolResult(True, f"✓ Pushed '{full_tag}'", result)
        except Exception as e:
            return ToolResult(False, f"✗ push_image failed: {e}")

    @staticmethod
    def pull_image(image: str) -> ToolResult:
        try:
            client = DockerTool._client()
            img = client.images.pull(image)
            return ToolResult(True, f"✓ Pulled '{image}'", {"id": img.id})
        except Exception as e:
            return ToolResult(False, f"✗ pull_image failed: {e}")

    @staticmethod
    def tag_image(source: str, target: str) -> ToolResult:
        try:
            client = DockerTool._client()
            img = client.images.get(source)
            repo, _, tag = target.rpartition(":")
            img.tag(repo or target, tag=tag or "latest")
            return ToolResult(True, f"✓ Tagged '{source}' → '{target}'")
        except Exception as e:
            return ToolResult(False, f"✗ tag_image failed: {e}")

    @staticmethod
    def remove_image(image: str, force: bool = False) -> ToolResult:
        try:
            client = DockerTool._client()
            client.images.remove(image, force=force)
            return ToolResult(True, f"✓ Image '{image}' removed")
        except Exception as e:
            return ToolResult(False, f"✗ remove_image failed: {e}")

    @staticmethod
    def list_images(filter: str = None) -> ToolResult:
        try:
            client = DockerTool._client()
            images = client.images.list(filters={"reference": filter} if filter else {})
            data = [{"id": i.short_id, "tags": i.tags, "size_mb": round(i.attrs["Size"] / 1e6, 1)} for i in images]
            return ToolResult(True, f"✓ {len(data)} images", data)
        except Exception as e:
            return ToolResult(False, f"✗ list_images failed: {e}")

    @staticmethod
    def run_container(image: str, name: str = None, ports: dict = None,
                      volumes: dict = None, env: dict = None,
                      detach: bool = True, command: str = None) -> ToolResult:
        try:
            client = DockerTool._client()
            kwargs = {
                "image": image, "detach": detach,
                "ports": ports or {}, "volumes": volumes or {},
                "environment": env or {},
            }
            if name:
                kwargs["name"] = name
            if command:
                kwargs["command"] = command
            container = client.containers.run(**kwargs)
            cid = container.id[:12] if detach else "completed"
            return ToolResult(True, f"✓ Container started: {cid}", {"id": cid})
        except Exception as e:
            return ToolResult(False, f"✗ run_container failed: {e}")

    @staticmethod
    def stop_container(name: str) -> ToolResult:
        try:
            DockerTool._client().containers.get(name).stop()
            return ToolResult(True, f"✓ Container '{name}' stopped")
        except Exception as e:
            return ToolResult(False, f"✗ stop_container failed: {e}")

    @staticmethod
    def start_container(name: str) -> ToolResult:
        try:
            DockerTool._client().containers.get(name).start()
            return ToolResult(True, f"✓ Container '{name}' started")
        except Exception as e:
            return ToolResult(False, f"✗ start_container failed: {e}")

    @staticmethod
    def remove_container(name: str, force: bool = False) -> ToolResult:
        try:
            DockerTool._client().containers.get(name).remove(force=force)
            return ToolResult(True, f"✓ Container '{name}' removed")
        except Exception as e:
            return ToolResult(False, f"✗ remove_container failed: {e}")

    @staticmethod
    def exec_in_container(name: str, command: str) -> ToolResult:
        try:
            container = DockerTool._client().containers.get(name)
            exit_code, output = container.exec_run(command, demux=False)
            out = output.decode(errors="replace") if isinstance(output, bytes) else str(output)
            return ToolResult(exit_code == 0, out.strip() or "✓ Done", out)
        except Exception as e:
            return ToolResult(False, f"✗ exec_in_container failed: {e}")

    @staticmethod
    def get_logs(name: str, tail: int = 100, follow: bool = False) -> ToolResult:
        try:
            container = DockerTool._client().containers.get(name)
            logs = container.logs(tail=tail, follow=follow, timestamps=True)
            out = logs.decode(errors="replace") if isinstance(logs, bytes) else str(logs)
            return ToolResult(True, f"✓ Logs from '{name}'", out)
        except Exception as e:
            return ToolResult(False, f"✗ get_logs failed: {e}")

    @staticmethod
    def list_containers(all: bool = False, filter: str = None) -> ToolResult:
        try:
            client = DockerTool._client()
            kwargs = {"all": all}
            if filter:
                kwargs["filters"] = {"name": filter}
            containers = client.containers.list(**kwargs)
            data = [{"id": c.short_id, "name": c.name, "status": c.status, "image": c.image.tags} for c in containers]
            return ToolResult(True, f"✓ {len(data)} containers", data)
        except Exception as e:
            return ToolResult(False, f"✗ list_containers failed: {e}")

    @staticmethod
    def inspect_container(name: str) -> ToolResult:
        try:
            container = DockerTool._client().containers.get(name)
            return ToolResult(True, f"✓ Inspected '{name}'", container.attrs)
        except Exception as e:
            return ToolResult(False, f"✗ inspect_container failed: {e}")

    @staticmethod
    def create_network(name: str, driver: str = "bridge") -> ToolResult:
        try:
            net = DockerTool._client().networks.create(name, driver=driver)
            return ToolResult(True, f"✓ Network '{name}' created (driver: {driver})", {"id": net.id})
        except Exception as e:
            return ToolResult(False, f"✗ create_network failed: {e}")

    @staticmethod
    def list_networks() -> ToolResult:
        try:
            nets = DockerTool._client().networks.list()
            data = [{"id": n.short_id, "name": n.name, "driver": n.attrs["Driver"]} for n in nets]
            return ToolResult(True, f"✓ {len(data)} networks", data)
        except Exception as e:
            return ToolResult(False, f"✗ list_networks failed: {e}")

    @staticmethod
    def remove_network(name: str) -> ToolResult:
        try:
            DockerTool._client().networks.get(name).remove()
            return ToolResult(True, f"✓ Network '{name}' removed")
        except Exception as e:
            return ToolResult(False, f"✗ remove_network failed: {e}")

    @staticmethod
    def create_volume(name: str) -> ToolResult:
        try:
            v = DockerTool._client().volumes.create(name)
            return ToolResult(True, f"✓ Volume '{name}' created", {"name": v.name})
        except Exception as e:
            return ToolResult(False, f"✗ create_volume failed: {e}")

    @staticmethod
    def list_volumes() -> ToolResult:
        try:
            vols = DockerTool._client().volumes.list()
            data = [{"name": v.name, "driver": v.attrs["Driver"]} for v in vols]
            return ToolResult(True, f"✓ {len(data)} volumes", data)
        except Exception as e:
            return ToolResult(False, f"✗ list_volumes failed: {e}")

    @staticmethod
    def remove_volume(name: str) -> ToolResult:
        try:
            DockerTool._client().volumes.get(name).remove()
            return ToolResult(True, f"✓ Volume '{name}' removed")
        except Exception as e:
            return ToolResult(False, f"✗ remove_volume failed: {e}")

    @staticmethod
    def compose_up(path: str, detach: bool = True, services: list = None) -> ToolResult:
        try:
            args = ["compose", "-f", path, "up"]
            if detach:
                args.append("-d")
            if services:
                args += services
            rc, out = DockerTool._run_docker(args)
            return ToolResult(rc == 0, f"✓ Compose up\n{out}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ compose_up failed: {e}")

    @staticmethod
    def compose_down(path: str, volumes: bool = False) -> ToolResult:
        try:
            args = ["compose", "-f", path, "down"]
            if volumes:
                args.append("-v")
            rc, out = DockerTool._run_docker(args)
            return ToolResult(rc == 0, f"✓ Compose down\n{out}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ compose_down failed: {e}")

    @staticmethod
    def compose_logs(path: str, services: list = None, tail: int = 50) -> ToolResult:
        try:
            args = ["compose", "-f", path, "logs", f"--tail={tail}"] + (services or [])
            rc, out = DockerTool._run_docker(args)
            return ToolResult(rc == 0, out, out)
        except Exception as e:
            return ToolResult(False, f"✗ compose_logs failed: {e}")

    @staticmethod
    def compose_ps(path: str) -> ToolResult:
        try:
            rc, out = DockerTool._run_docker(["compose", "-f", path, "ps"])
            return ToolResult(rc == 0, out, out)
        except Exception as e:
            return ToolResult(False, f"✗ compose_ps failed: {e}")

    @staticmethod
    def login(registry: str, username: str, password: str) -> ToolResult:
        try:
            client = DockerTool._client()
            result = client.login(username=username, password=password, registry=registry)
            return ToolResult(True, f"✓ Logged into {registry or 'DockerHub'}", result)
        except Exception as e:
            return ToolResult(False, f"✗ docker login failed: {e}")

    @staticmethod
    def system_prune(all: bool = False, volumes: bool = False) -> ToolResult:
        try:
            args = ["system", "prune", "-f"]
            if all:
                args.append("-a")
            if volumes:
                args.append("--volumes")
            rc, out = DockerTool._run_docker(args)
            return ToolResult(rc == 0, f"✓ System pruned\n{out}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ system_prune failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# 5. PackageManagerTool
# ══════════════════════════════════════════════════════════════════════════════
class PackageManagerTool:
    name = "package_manager"
    description = (
        "pip, npm, yarn, pnpm, cargo, go modules — install, uninstall, "
        "list, update, audit, build, publish"
    )

    @staticmethod
    def _run(args: list, cwd: str = None, timeout: int = 180) -> tuple:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()

    # ── pip ───────────────────────────────────────────────────────────────────
    @staticmethod
    def pip_install(packages: list = None, upgrade: bool = False,
                    user: bool = False, requirements_file: str = None) -> ToolResult:
        try:
            args = [sys.executable, "-m", "pip", "install"]
            if upgrade:
                args.append("--upgrade")
            if user:
                args.append("--user")
            if requirements_file:
                args += ["-r", requirements_file]
            elif packages:
                args += packages
            else:
                return ToolResult(False, "✗ No packages or requirements file specified")
            rc, out = PackageManagerTool._run(args)
            return ToolResult(rc == 0, f"✓ pip install done\n{out[-500:]}" if rc == 0 else f"✗ {out[-500:]}")
        except Exception as e:
            return ToolResult(False, f"✗ pip install failed: {e}")

    @staticmethod
    def pip_uninstall(packages: list) -> ToolResult:
        try:
            args = [sys.executable, "-m", "pip", "uninstall", "-y"] + packages
            rc, out = PackageManagerTool._run(args)
            return ToolResult(rc == 0, f"✓ Uninstalled {packages}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ pip uninstall failed: {e}")

    @staticmethod
    def pip_list(outdated: bool = False) -> ToolResult:
        try:
            args = [sys.executable, "-m", "pip", "list", "--format=json"]
            if outdated:
                args.append("--outdated")
            rc, out = PackageManagerTool._run(args)
            data = json.loads(out) if rc == 0 else []
            return ToolResult(rc == 0, f"✓ {len(data)} packages", data)
        except Exception as e:
            return ToolResult(False, f"✗ pip list failed: {e}")

    @staticmethod
    def pip_show(package: str) -> ToolResult:
        try:
            rc, out = PackageManagerTool._run([sys.executable, "-m", "pip", "show", package])
            return ToolResult(rc == 0, out, out)
        except Exception as e:
            return ToolResult(False, f"✗ pip show failed: {e}")

    @staticmethod
    def pip_freeze(output_file: str = None) -> ToolResult:
        try:
            rc, out = PackageManagerTool._run([sys.executable, "-m", "pip", "freeze"])
            if output_file and rc == 0:
                Path(output_file).write_text(out)
                return ToolResult(True, f"✓ requirements saved to {output_file}", out)
            return ToolResult(rc == 0, out, out)
        except Exception as e:
            return ToolResult(False, f"✗ pip freeze failed: {e}")

    # ── npm ───────────────────────────────────────────────────────────────────
    @staticmethod
    def npm_install(path: str = ".", packages: list = None,
                    dev: bool = False, global_: bool = False) -> ToolResult:
        try:
            args = ["npm", "install"]
            if global_:
                args.append("-g")
            if packages:
                args += packages
                if dev:
                    args.append("--save-dev")
            rc, out = PackageManagerTool._run(args, cwd=None if global_ else path)
            return ToolResult(rc == 0, f"✓ npm install done\n{out[-400:]}" if rc == 0 else f"✗ {out[-400:]}")
        except Exception as e:
            return ToolResult(False, f"✗ npm install failed: {e}")

    @staticmethod
    def npm_uninstall(path: str = ".", packages: list = None, global_: bool = False) -> ToolResult:
        try:
            args = ["npm", "uninstall"] + (packages or [])
            if global_:
                args.append("-g")
            rc, out = PackageManagerTool._run(args, cwd=None if global_ else path)
            return ToolResult(rc == 0, f"✓ npm uninstall done" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ npm uninstall failed: {e}")

    @staticmethod
    def npm_run(path: str, script: str) -> ToolResult:
        try:
            rc, out = PackageManagerTool._run(["npm", "run", script], cwd=path)
            return ToolResult(rc == 0, out[-1000:] if rc == 0 else f"✗ {out[-500:]}")
        except Exception as e:
            return ToolResult(False, f"✗ npm run failed: {e}")

    @staticmethod
    def npm_build(path: str) -> ToolResult:
        try:
            rc, out = PackageManagerTool._run(["npm", "run", "build"], cwd=path)
            return ToolResult(rc == 0, f"✓ Build done\n{out[-400:]}" if rc == 0 else f"✗ {out[-400:]}")
        except Exception as e:
            return ToolResult(False, f"✗ npm build failed: {e}")

    @staticmethod
    def npm_publish(path: str) -> ToolResult:
        try:
            rc, out = PackageManagerTool._run(["npm", "publish"], cwd=path)
            return ToolResult(rc == 0, f"✓ Package published\n{out}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ npm publish failed: {e}")

    @staticmethod
    def npm_list(path: str = ".", depth: int = 0) -> ToolResult:
        try:
            rc, out = PackageManagerTool._run(["npm", "list", f"--depth={depth}", "--json"], cwd=path)
            try:
                data = json.loads(out)
            except Exception:
                data = out
            return ToolResult(rc == 0, f"✓ npm list", data)
        except Exception as e:
            return ToolResult(False, f"✗ npm list failed: {e}")

    @staticmethod
    def npm_update(path: str = ".", packages: list = None) -> ToolResult:
        try:
            args = ["npm", "update"] + (packages or [])
            rc, out = PackageManagerTool._run(args, cwd=path)
            return ToolResult(rc == 0, f"✓ npm update done" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ npm update failed: {e}")

    @staticmethod
    def npm_audit(path: str = ".", fix: bool = False) -> ToolResult:
        try:
            args = ["npm", "audit"] + (["--fix"] if fix else [])
            rc, out = PackageManagerTool._run(args, cwd=path)
            return ToolResult(True, out[-1000:], out)
        except Exception as e:
            return ToolResult(False, f"✗ npm audit failed: {e}")

    # ── yarn ──────────────────────────────────────────────────────────────────
    @staticmethod
    def yarn_install(path: str = ".") -> ToolResult:
        try:
            rc, out = PackageManagerTool._run(["yarn", "install"], cwd=path)
            return ToolResult(rc == 0, f"✓ yarn install done\n{out[-400:]}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ yarn install failed: {e}")

    @staticmethod
    def yarn_add(path: str, packages: list, dev: bool = False) -> ToolResult:
        try:
            args = ["yarn", "add"] + packages + (["--dev"] if dev else [])
            rc, out = PackageManagerTool._run(args, cwd=path)
            return ToolResult(rc == 0, f"✓ yarn add done" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ yarn add failed: {e}")

    @staticmethod
    def yarn_remove(path: str, packages: list) -> ToolResult:
        try:
            rc, out = PackageManagerTool._run(["yarn", "remove"] + packages, cwd=path)
            return ToolResult(rc == 0, f"✓ yarn remove done" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ yarn remove failed: {e}")

    # ── cargo ─────────────────────────────────────────────────────────────────
    @staticmethod
    def cargo_build(path: str, release: bool = False) -> ToolResult:
        try:
            args = ["cargo", "build"] + (["--release"] if release else [])
            rc, out = PackageManagerTool._run(args, cwd=path, timeout=300)
            return ToolResult(rc == 0, f"✓ cargo build done\n{out[-500:]}" if rc == 0 else f"✗ {out[-500:]}")
        except Exception as e:
            return ToolResult(False, f"✗ cargo build failed: {e}")

    @staticmethod
    def cargo_test(path: str) -> ToolResult:
        try:
            rc, out = PackageManagerTool._run(["cargo", "test"], cwd=path, timeout=300)
            return ToolResult(rc == 0, out[-1000:], out)
        except Exception as e:
            return ToolResult(False, f"✗ cargo test failed: {e}")

    @staticmethod
    def cargo_run(path: str, args_extra: list = None) -> ToolResult:
        try:
            args = ["cargo", "run"] + (args_extra or [])
            rc, out = PackageManagerTool._run(args, cwd=path, timeout=120)
            return ToolResult(rc == 0, out[-1000:], out)
        except Exception as e:
            return ToolResult(False, f"✗ cargo run failed: {e}")

    # ── go ────────────────────────────────────────────────────────────────────
    @staticmethod
    def go_build(path: str, output: str = None) -> ToolResult:
        try:
            args = ["go", "build"] + (["-o", output] if output else []) + ["."]
            rc, out = PackageManagerTool._run(args, cwd=path, timeout=300)
            return ToolResult(rc == 0, f"✓ go build done" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ go build failed: {e}")

    @staticmethod
    def go_test(path: str, verbose: bool = False) -> ToolResult:
        try:
            args = ["go", "test"] + (["-v"] if verbose else []) + ["./..."]
            rc, out = PackageManagerTool._run(args, cwd=path, timeout=300)
            return ToolResult(rc == 0, out[-1000:], out)
        except Exception as e:
            return ToolResult(False, f"✗ go test failed: {e}")

    @staticmethod
    def go_get(path: str, package: str) -> ToolResult:
        try:
            rc, out = PackageManagerTool._run(["go", "get", package], cwd=path)
            return ToolResult(rc == 0, f"✓ go get {package}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ go get failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# 6. VSCodeTool
# ══════════════════════════════════════════════════════════════════════════════
class VSCodeTool:
    name = "vscode"
    description = (
        "VS Code automation: open files/folders, install/list extensions, "
        "apply settings, format, lint, create/open workspaces"
    )

    @staticmethod
    def _code(args: list) -> tuple:
        r = subprocess.run(["code"] + args, capture_output=True, text=True)
        return r.returncode, (r.stdout + r.stderr).strip()

    @staticmethod
    def _settings_path(scope: str = "user") -> Path:
        s = platform.system()
        if s == "Windows":
            base = Path(os.environ.get("APPDATA", "")) / "Code" / "User"
        elif s == "Darwin":
            base = Path.home() / "Library" / "Application Support" / "Code" / "User"
        else:
            base = Path.home() / ".config" / "Code" / "User"
        return base / "settings.json"

    @staticmethod
    def open_file(path: str) -> ToolResult:
        try:
            rc, out = VSCodeTool._code([path])
            return ToolResult(rc == 0, f"✓ Opened {path} in VS Code" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ open_file failed: {e}")

    @staticmethod
    def open_folder(path: str) -> ToolResult:
        try:
            rc, out = VSCodeTool._code([path])
            return ToolResult(rc == 0, f"✓ Opened folder {path}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ open_folder failed: {e}")

    @staticmethod
    def install_extension(extension_id: str) -> ToolResult:
        try:
            rc, out = VSCodeTool._code(["--install-extension", extension_id])
            return ToolResult(rc == 0, f"✓ Extension '{extension_id}' installed\n{out}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ install_extension failed: {e}")

    @staticmethod
    def uninstall_extension(extension_id: str) -> ToolResult:
        try:
            rc, out = VSCodeTool._code(["--uninstall-extension", extension_id])
            return ToolResult(rc == 0, f"✓ Extension '{extension_id}' uninstalled" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ uninstall_extension failed: {e}")

    @staticmethod
    def list_extensions() -> ToolResult:
        try:
            rc, out = VSCodeTool._code(["--list-extensions", "--show-versions"])
            exts = [l for l in out.splitlines() if l]
            return ToolResult(rc == 0, f"✓ {len(exts)} extensions installed", exts)
        except Exception as e:
            return ToolResult(False, f"✗ list_extensions failed: {e}")

    @staticmethod
    def run_task(task_name: str, workspace: str) -> ToolResult:
        try:
            # Use code CLI to run a task in the given workspace
            rc, out = VSCodeTool._code([workspace, "--run-task", task_name])
            return ToolResult(rc == 0, f"✓ Task '{task_name}' run" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ run_task failed: {e}")

    @staticmethod
    def open_terminal(workspace: str) -> ToolResult:
        try:
            # Open VS Code integrated terminal in the workspace
            rc, out = VSCodeTool._code([workspace, "--command", "workbench.action.terminal.new"])
            return ToolResult(rc == 0, f"✓ Terminal opened in {workspace}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ open_terminal failed: {e}")

    @staticmethod
    def apply_settings(settings_dict: dict, scope: str = "user") -> ToolResult:
        try:
            sp = VSCodeTool._settings_path(scope)
            sp.parent.mkdir(parents=True, exist_ok=True)
            existing = {}
            if sp.exists():
                try:
                    existing = json.loads(sp.read_text())
                except Exception:
                    existing = {}
            existing.update(settings_dict)
            sp.write_text(json.dumps(existing, indent=4))
            return ToolResult(True, f"✓ Applied {len(settings_dict)} settings to {scope} settings.json")
        except Exception as e:
            return ToolResult(False, f"✗ apply_settings failed: {e}")

    @staticmethod
    def get_settings(scope: str = "user") -> ToolResult:
        try:
            sp = VSCodeTool._settings_path(scope)
            if not sp.exists():
                return ToolResult(True, "✓ No settings file found (using defaults)", {})
            data = json.loads(sp.read_text())
            return ToolResult(True, f"✓ {len(data)} settings loaded", data)
        except Exception as e:
            return ToolResult(False, f"✗ get_settings failed: {e}")

    @staticmethod
    def format_file(path: str) -> ToolResult:
        try:
            rc, out = VSCodeTool._code(["--wait", path, "--command", "editor.action.formatDocument"])
            return ToolResult(rc == 0, f"✓ Formatted {path}" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ format_file failed: {e}")

    @staticmethod
    def lint_workspace(path: str) -> ToolResult:
        try:
            # Run eslint if available, otherwise pylint for Python
            if any(Path(path).glob("*.js")) or any(Path(path).glob("*.ts")):
                rc, out = subprocess.run(["npx", "eslint", path, "--format=compact"],
                                         capture_output=True, text=True, cwd=path).returncode, ""
                r = subprocess.run(["npx", "eslint", path, "--format=compact"],
                                   capture_output=True, text=True, cwd=path)
                return ToolResult(r.returncode == 0, (r.stdout + r.stderr)[-1000:])
            else:
                r = subprocess.run([sys.executable, "-m", "pylint", path, "--output-format=text"],
                                   capture_output=True, text=True)
                return ToolResult(r.returncode in (0, 4), (r.stdout + r.stderr)[-1000:])
        except Exception as e:
            return ToolResult(False, f"✗ lint_workspace failed: {e}")

    @staticmethod
    def create_workspace(path: str, folders: list, settings: dict = None) -> ToolResult:
        try:
            ws_data = {
                "folders": [{"path": f} for f in folders],
                "settings": settings or {}
            }
            ws_path = Path(path)
            if not ws_path.suffix == ".code-workspace":
                ws_path = ws_path.with_suffix(".code-workspace")
            ws_path.parent.mkdir(parents=True, exist_ok=True)
            ws_path.write_text(json.dumps(ws_data, indent=4))
            return ToolResult(True, f"✓ Workspace created: {ws_path}", {"path": str(ws_path)})
        except Exception as e:
            return ToolResult(False, f"✗ create_workspace failed: {e}")

    @staticmethod
    def open_workspace(path: str) -> ToolResult:
        try:
            rc, out = VSCodeTool._code([path])
            return ToolResult(rc == 0, f"✓ Workspace '{path}' opened" if rc == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ open_workspace failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# 7. TerminalTool
# ══════════════════════════════════════════════════════════════════════════════
class TerminalTool:
    name = "terminal"
    description = (
        "Advanced terminal/shell: run commands, scripts, env vars, aliases, "
        "process management, which/is_installed checks"
    )

    @staticmethod
    def run(command: str, cwd: str = None, timeout: int = 60,
            env: dict = None, shell: bool = True, capture: bool = True) -> ToolResult:
        try:
            merged_env = {**os.environ, **(env or {})}
            r = subprocess.run(
                command, cwd=cwd, timeout=timeout,
                env=merged_env, shell=shell,
                capture_output=capture, text=True
            )
            out = ((r.stdout or "") + (r.stderr or "")).strip() if capture else "✓ Done (output not captured)"
            return ToolResult(r.returncode == 0, out or "✓ Done", out)
        except subprocess.TimeoutExpired:
            return ToolResult(False, f"✗ Command timed out after {timeout}s")
        except Exception as e:
            return ToolResult(False, f"✗ run failed: {e}")

    @staticmethod
    def run_interactive(command: str, cwd: str = None) -> ToolResult:
        try:
            import shlex
            proc = subprocess.Popen(
                shlex.split(command) if not isinstance(command, list) else command,
                cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            lines = []
            for line in proc.stdout:
                lines.append(line.rstrip())
            proc.wait()
            out = "\n".join(lines)
            return ToolResult(proc.returncode == 0, out[-2000:] or "✓ Done", out)
        except Exception as e:
            return ToolResult(False, f"✗ run_interactive failed: {e}")

    @staticmethod
    def run_script(script_content: str, shell: str = None, cwd: str = None) -> ToolResult:
        try:
            shell = shell or ("bash" if platform.system() != "Windows" else "powershell")
            suffix = ".sh" if "bash" in shell else (".ps1" if "powershell" in shell else ".sh")
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode="w") as tf:
                tf.write(script_content)
                tf.flush()
                script_path = tf.name
            if platform.system() != "Windows":
                os.chmod(script_path, 0o755)
            r = subprocess.run([shell, script_path], cwd=cwd, capture_output=True, text=True, timeout=120)
            os.unlink(script_path)
            out = (r.stdout + r.stderr).strip()
            return ToolResult(r.returncode == 0, out[-2000:] or "✓ Script done", out)
        except Exception as e:
            return ToolResult(False, f"✗ run_script failed: {e}")

    @staticmethod
    def run_in_new_terminal(command: str) -> ToolResult:
        try:
            s = platform.system()
            if s == "Windows":
                subprocess.Popen(["start", "cmd", "/k", command], shell=True)
            elif s == "Darwin":
                apple_script = f'tell app "Terminal" to do script "{command}"'
                subprocess.Popen(["osascript", "-e", apple_script])
            else:
                for term in ["gnome-terminal", "xterm", "konsole"]:
                    if shutil.which(term):
                        subprocess.Popen([term, "--", "bash", "-c", command])
                        break
            return ToolResult(True, f"✓ Command launched in new terminal")
        except Exception as e:
            return ToolResult(False, f"✗ run_in_new_terminal failed: {e}")

    @staticmethod
    def set_env_var(key: str, value: str, persistent: bool = False, scope: str = "user") -> ToolResult:
        try:
            os.environ[key] = value
            if persistent:
                s = platform.system()
                if s == "Windows":
                    subprocess.run(["setx", key, value], capture_output=True)
                else:
                    shell_rc = Path.home() / (".bashrc" if "bash" in os.environ.get("SHELL", "") else ".zshrc")
                    if not shell_rc.exists():
                        shell_rc = Path.home() / ".bashrc"
                    content = shell_rc.read_text() if shell_rc.exists() else ""
                    marker = f"export {key}="
                    lines = [l for l in content.splitlines() if not l.startswith(marker)]
                    lines.append(f'export {key}="{value}"')
                    shell_rc.write_text("\n".join(lines) + "\n")
            return ToolResult(True, f"✓ Set {key}={value}" + (" (persistent)" if persistent else ""))
        except Exception as e:
            return ToolResult(False, f"✗ set_env_var failed: {e}")

    @staticmethod
    def get_env_var(key: str) -> ToolResult:
        try:
            val = os.environ.get(key)
            if val is None:
                return ToolResult(False, f"✗ Env var '{key}' not found")
            return ToolResult(True, f"✓ {key}={val}", val)
        except Exception as e:
            return ToolResult(False, f"✗ get_env_var failed: {e}")

    @staticmethod
    def list_env_vars(filter: str = None) -> ToolResult:
        try:
            env = dict(os.environ)
            if filter:
                env = {k: v for k, v in env.items() if filter.lower() in k.lower()}
            return ToolResult(True, f"✓ {len(env)} env vars", env)
        except Exception as e:
            return ToolResult(False, f"✗ list_env_vars failed: {e}")

    @staticmethod
    def source_file(path: str) -> ToolResult:
        try:
            content = Path(path).read_text()
            updated = {}
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("export "):
                    line = line[7:]
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    os.environ[k] = v
                    updated[k] = v
            return ToolResult(True, f"✓ Sourced {len(updated)} vars from {path}", updated)
        except Exception as e:
            return ToolResult(False, f"✗ source_file failed: {e}")

    @staticmethod
    def which(command: str) -> ToolResult:
        try:
            path = shutil.which(command)
            if path:
                return ToolResult(True, f"✓ {command} → {path}", path)
            return ToolResult(False, f"✗ '{command}' not found in PATH")
        except Exception as e:
            return ToolResult(False, f"✗ which failed: {e}")

    @staticmethod
    def is_installed(command: str) -> ToolResult:
        try:
            found = shutil.which(command) is not None
            return ToolResult(found, f"✓ '{command}' is installed" if found else f"✗ '{command}' not found", found)
        except Exception as e:
            return ToolResult(False, f"✗ is_installed failed: {e}")

    @staticmethod
    def install_via_package_manager(package: str) -> ToolResult:
        try:
            s = platform.system()
            if s == "Windows":
                r = subprocess.run(["winget", "install", package], capture_output=True, text=True)
            elif s == "Darwin":
                r = subprocess.run(["brew", "install", package], capture_output=True, text=True)
            else:
                # Try apt, then dnf, then pacman
                for pm in [["apt-get", "install", "-y"], ["dnf", "install", "-y"], ["pacman", "-S", "--noconfirm"]]:
                    if shutil.which(pm[0]):
                        r = subprocess.run(["sudo"] + pm + [package], capture_output=True, text=True)
                        break
                else:
                    return ToolResult(False, "✗ No supported package manager found (apt/dnf/pacman)")
            out = (r.stdout + r.stderr).strip()
            return ToolResult(r.returncode == 0, f"✓ Installed '{package}'\n{out[-300:]}" if r.returncode == 0 else f"✗ {out[-300:]}")
        except Exception as e:
            return ToolResult(False, f"✗ install_via_package_manager failed: {e}")

    @staticmethod
    def create_alias(name: str, command: str, persistent: bool = False) -> ToolResult:
        try:
            alias_str = f"alias {name}='{command}'"
            if persistent:
                shell_rc = Path.home() / ".bashrc"
                content = shell_rc.read_text() if shell_rc.exists() else ""
                if alias_str not in content:
                    with open(shell_rc, "a") as f:
                        f.write(f"\n{alias_str}\n")
            return ToolResult(True, f"✓ Alias created: {alias_str}" + (" (persistent)" if persistent else " (session only)"))
        except Exception as e:
            return ToolResult(False, f"✗ create_alias failed: {e}")

    @staticmethod
    def list_processes(filter: str = None) -> ToolResult:
        try:
            import psutil
            procs = []
            for p in psutil.process_iter(["pid", "name", "status", "cpu_percent", "memory_info"]):
                try:
                    info = p.info
                    if filter and filter.lower() not in info["name"].lower():
                        continue
                    procs.append({"pid": info["pid"], "name": info["name"],
                                  "status": info["status"],
                                  "mem_mb": round(info["memory_info"].rss / 1e6, 1) if info["memory_info"] else 0})
                except Exception:
                    continue
            return ToolResult(True, f"✓ {len(procs)} processes", procs)
        except Exception as e:
            return ToolResult(False, f"✗ list_processes failed: {e}")

    @staticmethod
    def kill_process(pid_or_name: str) -> ToolResult:
        try:
            import psutil, signal
            killed = []
            for p in psutil.process_iter(["pid", "name"]):
                try:
                    info = p.info
                    if str(info["pid"]) == str(pid_or_name) or info["name"] == pid_or_name:
                        p.kill()
                        killed.append(info["pid"])
                except Exception:
                    continue
            if killed:
                return ToolResult(True, f"✓ Killed PIDs: {killed}", killed)
            return ToolResult(False, f"✗ No process matching '{pid_or_name}' found")
        except Exception as e:
            return ToolResult(False, f"✗ kill_process failed: {e}")

    @staticmethod
    def get_process_info(pid: int) -> ToolResult:
        try:
            import psutil
            p = psutil.Process(pid)
            info = {
                "pid": p.pid, "name": p.name(), "status": p.status(),
                "cpu_percent": p.cpu_percent(interval=0.5),
                "mem_mb": round(p.memory_info().rss / 1e6, 1),
                "cmdline": " ".join(p.cmdline()),
                "cwd": p.cwd(), "created": p.create_time()
            }
            return ToolResult(True, f"✓ Process info for PID {pid}", info)
        except Exception as e:
            return ToolResult(False, f"✗ get_process_info failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# 8. MakefileTool
# ══════════════════════════════════════════════════════════════════════════════
class MakefileTool:
    name = "makefile"
    description = "Makefile build system: run targets, list targets, create and edit Makefiles"

    @staticmethod
    def run_target(makefile_path: str, target: str = "all",
                   args: list = None, env: dict = None) -> ToolResult:
        try:
            make_dir = str(Path(makefile_path).parent)
            cmd = ["make", "-f", str(makefile_path), target] + (args or [])
            merged_env = {**os.environ, **(env or {})}
            r = subprocess.run(cmd, cwd=make_dir, capture_output=True, text=True,
                               env=merged_env, timeout=300)
            out = (r.stdout + r.stderr).strip()
            return ToolResult(r.returncode == 0,
                              f"✓ make {target} done\n{out[-800:]}" if r.returncode == 0 else f"✗ make {target} failed\n{out[-800:]}")
        except Exception as e:
            return ToolResult(False, f"✗ run_target failed: {e}")

    @staticmethod
    def list_targets(makefile_path: str) -> ToolResult:
        try:
            content = Path(makefile_path).read_text()
            targets = []
            for line in content.splitlines():
                # Match lines like "target:" or "target: dep1 dep2"
                m = re.match(r'^([a-zA-Z0-9_\-\.]+)\s*:', line)
                if m and not line.startswith("\t") and not line.startswith("#"):
                    target = m.group(1)
                    if target not in (".PHONY", ".DEFAULT", "targets"):
                        targets.append(target)
            return ToolResult(True, f"✓ {len(targets)} targets found", targets)
        except Exception as e:
            return ToolResult(False, f"✗ list_targets failed: {e}")

    @staticmethod
    def create_makefile(path: str, targets_dict: dict) -> ToolResult:
        """targets_dict: {'target_name': {'deps': ['dep1'], 'commands': ['cmd1']}}"""
        try:
            lines = [".PHONY: " + " ".join(targets_dict.keys()), ""]
            for target, info in targets_dict.items():
                deps = " ".join(info.get("deps", []))
                lines.append(f"{target}: {deps}")
                for cmd in info.get("commands", []):
                    lines.append(f"\t{cmd}")
                lines.append("")
            content = "\n".join(lines)
            Path(path).write_text(content)
            return ToolResult(True, f"✓ Makefile created at {path}", content)
        except Exception as e:
            return ToolResult(False, f"✗ create_makefile failed: {e}")

    @staticmethod
    def add_target(makefile_path: str, name: str,
                   deps: list = None, commands: list = None) -> ToolResult:
        try:
            existing = Path(makefile_path).read_text() if Path(makefile_path).exists() else ""
            deps_str = " ".join(deps or [])
            new_block = f"\n{name}: {deps_str}\n"
            for cmd in (commands or []):
                new_block += f"\t{cmd}\n"
            # Update .PHONY if present
            if ".PHONY:" in existing:
                existing = re.sub(r"(\.PHONY:.*)", r"\1 " + name, existing, count=1)
            Path(makefile_path).write_text(existing + new_block)
            return ToolResult(True, f"✓ Target '{name}' added to {makefile_path}")
        except Exception as e:
            return ToolResult(False, f"✗ add_target failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# 9. CMakeTool
# ══════════════════════════════════════════════════════════════════════════════
class CMakeTool:
    name = "cmake"
    description = "CMake build system: configure, build, install, clean, ctest"

    @staticmethod
    def configure(source_dir: str, build_dir: str,
                  generator: str = None, defines: dict = None) -> ToolResult:
        try:
            Path(build_dir).mkdir(parents=True, exist_ok=True)
            args = ["cmake", source_dir, "-B", build_dir]
            if generator:
                args += ["-G", generator]
            for k, v in (defines or {}).items():
                args.append(f"-D{k}={v}")
            r = subprocess.run(args, capture_output=True, text=True, cwd=source_dir, timeout=120)
            out = (r.stdout + r.stderr).strip()
            return ToolResult(r.returncode == 0,
                              f"✓ CMake configured\n{out[-600:]}" if r.returncode == 0 else f"✗ CMake configure failed\n{out[-600:]}")
        except Exception as e:
            return ToolResult(False, f"✗ configure failed: {e}")

    @staticmethod
    def build(build_dir: str, target: str = None, jobs: int = None) -> ToolResult:
        try:
            args = ["cmake", "--build", build_dir]
            if target:
                args += ["--target", target]
            if jobs:
                args += ["--", f"-j{jobs}"]
            r = subprocess.run(args, capture_output=True, text=True, timeout=600)
            out = (r.stdout + r.stderr).strip()
            return ToolResult(r.returncode == 0,
                              f"✓ Build done\n{out[-600:]}" if r.returncode == 0 else f"✗ Build failed\n{out[-600:]}")
        except Exception as e:
            return ToolResult(False, f"✗ build failed: {e}")

    @staticmethod
    def install(build_dir: str, prefix: str = None) -> ToolResult:
        try:
            args = ["cmake", "--install", build_dir]
            if prefix:
                args += ["--prefix", prefix]
            r = subprocess.run(args, capture_output=True, text=True, timeout=120)
            out = (r.stdout + r.stderr).strip()
            return ToolResult(r.returncode == 0,
                              f"✓ Installed to {prefix or 'default prefix'}\n{out}" if r.returncode == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ install failed: {e}")

    @staticmethod
    def clean(build_dir: str) -> ToolResult:
        try:
            r = subprocess.run(["cmake", "--build", build_dir, "--target", "clean"],
                               capture_output=True, text=True, timeout=120)
            out = (r.stdout + r.stderr).strip()
            return ToolResult(r.returncode == 0, f"✓ Cleaned {build_dir}\n{out}" if r.returncode == 0 else f"✗ {out}")
        except Exception as e:
            return ToolResult(False, f"✗ clean failed: {e}")

    @staticmethod
    def run_ctest(build_dir: str, verbose: bool = False) -> ToolResult:
        try:
            args = ["ctest", "--test-dir", build_dir] + (["-V"] if verbose else [])
            r = subprocess.run(args, capture_output=True, text=True, timeout=300)
            out = (r.stdout + r.stderr).strip()
            return ToolResult(r.returncode == 0, out[-1500:], out)
        except Exception as e:
            return ToolResult(False, f"✗ run_ctest failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# 10. DebuggerTool
# ══════════════════════════════════════════════════════════════════════════════
class DebuggerTool:
    name = "debugger"
    description = (
        "Debugging utilities: run with pdb, analyze tracebacks, profile scripts, "
        "memory profiling, find deadlocks, strace"
    )

    @staticmethod
    def run_python_with_pdb(script: str, args: list = None) -> ToolResult:
        try:
            cmd = [sys.executable, "-m", "pdb", script] + (args or [])
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60,
                               input="c\nq\n")  # continue then quit
            out = (r.stdout + r.stderr).strip()
            return ToolResult(True, f"✓ pdb run completed\n{out[-1000:]}", out)
        except Exception as e:
            return ToolResult(False, f"✗ run_python_with_pdb failed: {e}")

    @staticmethod
    def analyze_traceback(traceback_text: str) -> ToolResult:
        try:
            lines = traceback_text.strip().splitlines()
            # Extract the exception type and message
            exc_line = next((l for l in reversed(lines) if ": " in l and not l.startswith(" ")), lines[-1] if lines else "")
            # Extract file references
            file_refs = []
            for line in lines:
                m = re.search(r'File "(.+?)", line (\d+), in (.+)', line)
                if m:
                    file_refs.append({"file": m.group(1), "line": int(m.group(2)), "in": m.group(3)})
            analysis = {
                "exception": exc_line,
                "traceback_frames": file_refs,
                "root_cause_file": file_refs[-1] if file_refs else None,
                "summary": f"Exception at {file_refs[-1]['file']}:{file_refs[-1]['line']} in {file_refs[-1]['in']}" if file_refs else exc_line
            }
            return ToolResult(True, f"✓ Traceback analyzed: {analysis['exception']}", analysis)
        except Exception as e:
            return ToolResult(False, f"✗ analyze_traceback failed: {e}")

    @staticmethod
    def profile_script(script: str, output: str = None) -> ToolResult:
        try:
            out_file = output or str(Path(tempfile.gettempdir()) / "profile_stats.prof")
            r = subprocess.run(
                [sys.executable, "-m", "cProfile", "-o", out_file, script],
                capture_output=True, text=True, timeout=120
            )
            # Read and display top stats
            import pstats, io
            stream = io.StringIO()
            ps = pstats.Stats(out_file, stream=stream)
            ps.sort_stats("cumulative")
            ps.print_stats(20)
            stats_text = stream.getvalue()
            return ToolResult(True, f"✓ Profile saved to {out_file}\n{stats_text[:2000]}", stats_text)
        except Exception as e:
            return ToolResult(False, f"✗ profile_script failed: {e}")

    @staticmethod
    def memory_profile(script: str) -> ToolResult:
        try:
            _ensure("memory-profiler", "memory_profiler")
            r = subprocess.run(
                [sys.executable, "-m", "memory_profiler", script],
                capture_output=True, text=True, timeout=120
            )
            out = (r.stdout + r.stderr).strip()
            return ToolResult(r.returncode == 0, out[-2000:] if out else "✓ No output", out)
        except Exception as e:
            return ToolResult(False, f"✗ memory_profile failed: {e}")

    @staticmethod
    def find_deadlocks(pid: int) -> ToolResult:
        try:
            import psutil
            proc = psutil.Process(pid)
            threads = proc.threads()
            # Check thread states and connections for signs of deadlock
            thread_info = [{"id": t.id, "user_time": t.user_time, "system_time": t.system_time}
                           for t in threads]
            connections = proc.connections()
            # Simple heuristic: threads with identical CPU times may be stuck
            stuck = [t for t in thread_info if t["user_time"] == 0 and t["system_time"] == 0]
            analysis = {
                "pid": pid,
                "total_threads": len(thread_info),
                "potentially_stuck_threads": len(stuck),
                "threads": thread_info,
                "open_connections": len(connections)
            }
            deadlock_suspected = len(stuck) > 1
            msg = f"⚠ Deadlock suspected ({len(stuck)} stuck threads)" if deadlock_suspected else f"✓ No obvious deadlock ({len(thread_info)} threads active)"
            return ToolResult(True, msg, analysis)
        except Exception as e:
            return ToolResult(False, f"✗ find_deadlocks failed: {e}")

    @staticmethod
    def strace_process(pid: int, output: str = None, duration: int = 10) -> ToolResult:
        try:
            if platform.system() != "Linux":
                return ToolResult(False, "✗ strace is Linux-only")
            if not shutil.which("strace"):
                return ToolResult(False, "✗ strace not installed. Run: sudo apt install strace")
            out_file = output or str(Path(tempfile.gettempdir()) / f"strace_{pid}.txt")
            r = subprocess.run(
                ["strace", "-p", str(pid), "-o", out_file, "-c"],
                capture_output=True, text=True, timeout=duration + 5,
                input=None
            )
            if Path(out_file).exists():
                content = Path(out_file).read_text()[:3000]
                return ToolResult(True, f"✓ strace output saved to {out_file}\n{content}", content)
            return ToolResult(False, "✗ strace produced no output")
        except subprocess.TimeoutExpired:
            # This is expected since we let it run for `duration` seconds
            if Path(output or "").exists() or Path(str(Path(tempfile.gettempdir()) / f"strace_{pid}.txt")).exists():
                out_file = output or str(Path(tempfile.gettempdir()) / f"strace_{pid}.txt")
                content = Path(out_file).read_text()[:3000] if Path(out_file).exists() else "No output"
                return ToolResult(True, f"✓ strace captured for {duration}s\n{content}", content)
            return ToolResult(True, f"✓ strace ran for {duration}s (output may be empty if process wasn't active)")
        except Exception as e:
            return ToolResult(False, f"✗ strace_process failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# Tool Registry
# ══════════════════════════════════════════════════════════════════════════════
DEVELOPER_TOOLS = {
    "git":             GitTool,
    "github":          GitHubTool,
    "gitlab":          GitLabTool,
    "docker":          DockerTool,
    "package_manager": PackageManagerTool,
    "vscode":          VSCodeTool,
    "terminal":        TerminalTool,
    "makefile":        MakefileTool,
    "cmake":           CMakeTool,
    "debugger":        DebuggerTool,
}

DEVELOPER_TOOLS_SUMMARY = "\n".join(
    f"- {k}: {v.description}" for k, v in DEVELOPER_TOOLS.items()
)

if __name__ == "__main__":
    print("NPM Agent — Developer CLI Tools loaded successfully.")
    print(f"{len(DEVELOPER_TOOLS)} tool classes available:")
    for name, cls in DEVELOPER_TOOLS.items():
        methods = [m for m in dir(cls) if not m.startswith("_")]
        print(f"  {name:20s} ({len(methods)} methods)")
      
