import json
import os
import subprocess
import sys
import tempfile
import unittest

HOOK = os.path.join(os.path.dirname(__file__), "..", "hooks", "branch_name_guard.py")


class BranchNameGuardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.env = {
            **os.environ,
            "HOME": cls.tmp.name,
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
        }
        cls.repo = os.path.join(cls.tmp.name, "repo")
        cls.other = os.path.join(cls.tmp.name, "elsewhere")
        os.makedirs(cls.other)
        cls.git("init", "-q", "-b", "main", cls.repo, cwd=cls.tmp.name)
        for args in [
            ("config", "user.email", "t@example.com"),
            ("config", "user.name", "t"),
            ("commit", "-q", "--allow-empty", "-m", "init"),
            ("remote", "add", "origin", "https://github.com/paramify/fetchers-test.git"),
            ("remote", "add", "ssh", "git@github.com:paramify/fetchers-test.git"),
            ("remote", "add", "fork", "https://github.com/someone/fetchers-test.git"),
            ("update-ref", "refs/remotes/origin/main", "HEAD"),
            ("update-ref", "refs/remotes/origin/feat/existing", "HEAD"),
            ("branch", "feat/existing"),
            ("branch", "feat/new"),
            ("branch", "fde-123"),
            ("tag", "v1.0"),
        ]:
            cls.git(*args)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @classmethod
    def git(cls, *args, cwd=None):
        subprocess.run(["git", *args], cwd=cwd or cls.repo, env=cls.env, check=True, capture_output=True)

    def checkout(self, branch):
        self.git("symbolic-ref", "HEAD", f"refs/heads/{branch}")
        self.addCleanup(self.git, "symbolic-ref", "HEAD", "refs/heads/main")

    def run_hook(self, command, cwd=None, tool="Bash"):
        event = {"hook_event_name": "PreToolUse", "tool_name": tool, "cwd": cwd or self.repo,
                 "tool_input": {"command": command}}
        return subprocess.run([sys.executable, "-I", HOOK], input=json.dumps(event), env=self.env,
                              capture_output=True, text=True)

    def assertBlocked(self, command, **kw):
        r = self.run_hook(command, **kw)
        self.assertEqual(r.returncode, 2, f"expected block: {command!r}")
        self.assertIn("fde-<n>", r.stderr)
        return r

    def assertAllowed(self, command, **kw):
        r = self.run_hook(command, **kw)
        self.assertEqual(r.returncode, 0, f"expected allow: {command!r}\n{r.stderr}")

    def test_bare_push_resolves_current_branch(self):
        self.checkout("feat/new")
        self.assertBlocked("git push")
        self.assertBlocked("git push origin HEAD")
        self.assertBlocked("git push -u origin HEAD")

    def test_bare_push_on_issue_branch(self):
        self.checkout("fde-123")
        self.assertAllowed("git push")
        self.assertAllowed("git push -u origin HEAD")

    def test_bare_push_on_existing_branch(self):
        self.checkout("feat/existing")
        self.assertAllowed("git push")

    def test_detached_head(self):
        self.git("checkout", "-q", "--detach")
        self.addCleanup(self.git, "checkout", "-q", "main")
        self.assertAllowed("git push")

    def test_named_branch(self):
        self.assertBlocked("git push origin feat/new")
        self.assertBlocked("git push -u origin feat/new")
        self.assertBlocked("git push --set-upstream origin feat/new")
        self.assertBlocked("git push --force origin +feat/new")
        self.assertAllowed("git push -u origin fde-123")
        self.assertAllowed("git push origin feat/existing")

    def test_src_dst(self):
        self.assertBlocked("git push origin fde-123:feat/new")
        self.assertBlocked("git push origin HEAD:refs/heads/feat/new")
        self.assertBlocked("git push origin feat/new:refs/heads/feat/brand-new")
        self.assertAllowed("git push origin feat/new:fde-9")
        self.assertAllowed("git push origin feat/new:refs/heads/fde-9")
        self.assertAllowed("git push origin feat/new:feat/existing")

    def test_names_that_are_not_the_id_alone(self):
        self.assertBlocked("git push origin HEAD:FDE-123")
        self.assertBlocked("git push origin HEAD:fde-123-add-thing")
        self.assertBlocked("git push origin HEAD:connordalton/fde-777-extend-azure-fetchers")

    def test_main_master_added_validators(self):
        for b in ("main", "master", "added-validators"):
            self.assertAllowed(f"git push origin HEAD:{b}")
            self.assertAllowed(f"git push origin HEAD:refs/heads/{b}")

    def test_tags(self):
        self.checkout("feat/new")
        self.assertAllowed("git push origin v1.0")
        self.assertAllowed("git push origin refs/tags/v1.0")
        self.assertAllowed("git push origin v1.0:refs/tags/v1.0")
        self.assertAllowed("git push --tags")
        self.assertAllowed("git push origin --tags")

    def test_deletions(self):
        self.assertAllowed("git push origin :feat/new")
        self.assertAllowed("git push origin --delete feat/new")
        self.assertAllowed("git push -d origin feat/new")

    def test_dry_run(self):
        self.assertAllowed("git push --dry-run origin feat/new")
        self.assertAllowed("git push -n origin feat/new")

    def test_unresolvable_refspecs(self):
        self.assertAllowed('git push origin "${B}:refs/heads/${B}"')
        self.assertAllowed("git push origin $BRANCH")
        self.assertAllowed("git push origin `git branch --show-current`")
        self.assertAllowed("git push origin 'refs/heads/*:refs/heads/*'")

    def test_remotes(self):
        self.assertAllowed("git push fork feat/new")
        self.assertBlocked("git push ssh feat/new")
        self.assertBlocked("git push https://github.com/paramify/fetchers-test.git feat/new")
        self.assertAllowed("git push https://github.com/someone/fetchers-test.git feat/new")

    def test_every_branch(self):
        self.assertBlocked("git push --all origin")

    def test_repo_from_cd_or_dash_c(self):
        self.assertAllowed("git push origin feat/new", cwd=self.other)
        self.assertBlocked(f"cd {self.repo} && git push origin feat/new", cwd=self.other)
        self.assertBlocked(f"git -C {self.repo} push origin feat/new", cwd=self.other)
        self.assertBlocked(f"cd {self.tmp.name} && git -C repo push origin feat/new", cwd=self.other)

    def test_compound_commands(self):
        self.assertBlocked('git add -A && git commit -m "wip; git push" && git push -u origin feat/new')
        self.assertBlocked("git status\ngit push origin feat/new 2>&1 | tail -3")
        self.assertBlocked("GIT_TRACE=0 git push origin feat/new")
        self.assertBlocked("bash -c 'git push origin feat/new'")
        self.assertAllowed('git commit -m "git push origin feat/new"')

    def test_push_default_upstream(self):
        self.checkout("feat/new")
        self.git("config", "branch.feat/new.remote", "origin")
        self.git("config", "branch.feat/new.merge", "refs/heads/feat/existing")
        self.git("config", "push.default", "upstream")
        self.addCleanup(self.git, "config", "--unset", "push.default")
        self.addCleanup(self.git, "config", "--remove-section", "branch.feat/new")
        self.assertAllowed("git push")

    def test_not_a_push(self):
        self.assertAllowed("git status")
        self.assertAllowed("echo push")
        self.assertAllowed("git push origin feat/new", tool="Write")

    def test_bad_input_fails_open(self):
        r = subprocess.run([sys.executable, "-I", HOOK], input="not json", env=self.env,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertAllowed("git push origin 'feat/new")

    def test_message(self):
        r = self.assertBlocked("git push -u origin feat/new")
        self.assertIn("'feat/new'", r.stderr)
        self.assertIn("fde-123", r.stderr)
        self.assertIn("git fetch origin", r.stderr)


if __name__ == "__main__":
    unittest.main()
