"""Exercise release orchestration with real local Git and fake Docker/GitHub."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MOCK = '''#!/usr/bin/env python3
import json, os, pathlib, subprocess, sys
args = sys.argv[1:]
command = pathlib.Path(sys.argv[0]).name
entry = {"command": command, "args": args}
if command == "docker" and args[0] == "build":
    entry["version"] = subprocess.check_output(["git", "describe", "--tags", "--always"], text=True).strip()
if command == "gh" and args[:2] == ["release", "create"]:
    entry["notes"] = pathlib.Path(args[args.index("--notes-file") + 1]).read_text()
with open(os.environ["RELEASE_TEST_LOG"], "a") as log:
    log.write(json.dumps(entry) + "\\n")
if os.environ.get("RELEASE_TEST_FAIL") == command + " " + args[0]:
    sys.exit(1)
'''


class ReleaseTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ponylib release ")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.remote = self.base / "origin.git"
        self.bin = self.base / "bin"
        self.bin.mkdir()
        for name in ("docker", "gh"):
            executable = self.bin / name
            executable.write_text(MOCK)
            executable.chmod(0o755)
        self.log = self.base / "commands.jsonl"
        self.env = dict(os.environ, PATH=f"{self.bin}:{os.environ['PATH']}",
                        RELEASE_TEST_LOG=str(self.log), GIT_CONFIG_NOSYSTEM="1",
                        GIT_CONFIG_GLOBAL=os.devnull)
        self.env.pop("RELEASE_TEST_FAIL", None)
        self.git("init", "-b", "release-test")
        self.git("config", "user.name", "Release Test")
        self.git("config", "user.email", "release@example.invalid")
        self.git("init", "--bare", str(self.remote))
        self.git("remote", "add", "origin", str(self.remote))
        for name in ("publish-release.sh", "build-docker.sh"):
            shutil.copy2(ROOT / name, self.repo / name)
        self.compose = self.repo / "docs/docker-compose/docker-compose.yml"
        self.compose.parent.mkdir(parents=True)
        self.compose.write_text("services:\n  app:\n    image: ghcr.io/maizy/ponylib:v2.0.8\n")
        self.git("add", ".")
        self.git("commit", "-m", "Previous release")
        self.git("tag", "v2.0.8")
        self.git("tag", "v99.0.0-rc1")
        self.git("tag", "unrelated")
        (self.repo / "feature.txt").write_text("feature\n")
        self.git("add", ".")
        self.git("commit", "-m", "Add a feature")
        self.head = self.git("rev-parse", "HEAD")
        self.git("push", "origin", "HEAD", "--tags")

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.repo, env=self.env,
                                       text=True, stderr=subprocess.DEVNULL).strip()

    def run_release(self, *args, fail=None):
        env = dict(self.env)
        if fail:
            env["RELEASE_TEST_FAIL"] = fail
        return subprocess.run([str(self.repo / "publish-release.sh"), *args],
                              cwd=self.base, env=env, text=True, capture_output=True)

    def entries(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def test_version_bumps_and_publication(self):
        for option, version in (((), "v2.0.9"), (("--patch",), "v2.0.10"),
                                (("--minor",), "v2.1.0"), (("--major",), "v3.0.0")):
            with self.subTest(option=option):
                head = self.git("rev-parse", "HEAD")
                result = self.run_release(*option)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(self.git("rev-parse", f"{version}^{{commit}}"), head)
                self.assertEqual(self.git("rev-parse", "HEAD^"), head)
                self.assertIn(f"image: ghcr.io/maizy/ponylib:{version}", self.compose.read_text())
                self.assertEqual(self.git("status", "--porcelain"), "")
                self.assertEqual(self.git("--git-dir", str(self.remote), "rev-parse", "refs/heads/release-test"),
                                 self.git("rev-parse", "HEAD"))
                self.assertEqual(self.git("--git-dir", str(self.remote), "rev-parse", f"{version}^{{commit}}"), head)
                entries = self.entries()
                build = [e for e in entries if e["command"] == "docker" and e["args"][0] == "build"][-1]
                self.assertEqual(build["version"], version)
                self.assertIn(f"ghcr.io/maizy/ponylib:{version}", build["args"])
                push = [e for e in entries if e["command"] == "docker" and e["args"][0] == "push"][-1]
                self.assertEqual(push["args"], ["push", f"ghcr.io/maizy/ponylib:{version}"])
                release = entries[-1]
                self.assertEqual(release["args"][:3], ["release", "create", version])
                self.assertIn("--verify-tag", release["args"])
                self.assertIn("maizy/PonyLib", release["args"])
                if version == "v2.0.9":
                    self.assertIn("Changes since v2.0.8", release["notes"])
                    self.assertIn("Add a feature", release["notes"])
                    self.assertNotIn("Previous release", release["notes"])
                    self.assertNotIn("docs: use", release["notes"])

    def test_versions_are_sorted_numerically(self):
        self.git("tag", "v2.0.9")
        self.git("tag", "v2.0.10")
        result = self.run_release()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ponylib:v2.0.11", self.compose.read_text())

    def test_invalid_compose_stops_before_tagging(self):
        self.compose.write_text("services: {}\n")
        self.git("add", ".")
        self.git("commit", "-m", "Invalid compose")
        result = self.run_release()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("v2.0.9", self.git("tag", "--list").splitlines())
        self.assertFalse(any(e["command"] == "docker" and e["args"][0] == "build"
                             for e in self.entries()))

    def test_github_failure_preserves_pushed_tag(self):
        result = self.run_release(fail="gh release")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("failed during GitHub release", result.stderr)
        self.assertEqual(self.git("--git-dir", str(self.remote), "rev-parse", "v2.0.9^{commit}"), self.head)

    def test_invalid_options_do_not_change_repository(self):
        for args in (("--invalid",), ("--minor", "--major")):
            result = self.run_release(*args)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(self.git("rev-parse", "HEAD"), self.head)
            self.assertFalse(self.log.exists())

    def test_dirty_tree_is_rejected(self):
        (self.repo / "untracked.txt").write_text("uncommitted\n")
        result = self.run_release()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Commit or stash", result.stderr)
        self.assertFalse(self.log.exists())

    def test_missing_version_is_rejected(self):
        self.git("tag", "-d", "v2.0.8")
        self.git("push", "origin", ":refs/tags/v2.0.8")
        result = self.run_release()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("No release tag", result.stderr)

    def test_latest_version_on_another_branch_is_rejected(self):
        self.git("checkout", "--orphan", "other-history")
        self.git("commit", "-m", "Unrelated release")
        self.git("tag", "v3.0.0")
        self.git("checkout", "release-test")
        result = self.run_release()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not an ancestor", result.stderr)

    def test_docker_failure_stops_before_compose_commit_and_release(self):
        for fail in ("docker build", "docker push"):
            with self.subTest(fail=fail):
                result = self.run_release(fail=fail)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.git("rev-parse", "HEAD"), self.head)
                self.assertIn("ponylib:v2.0.8", self.compose.read_text())
                self.assertFalse(any(e["args"][:2] == ["release", "create"] for e in self.entries()))
                self.git("tag", "-d", "v2.0.9")

    def test_git_push_failure_does_not_create_github_release(self):
        hook = self.remote / "hooks/pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        result = self.run_release()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("failed during Git push", result.stderr)
        self.assertFalse(any(e["args"][:2] == ["release", "create"] for e in self.entries()))


if __name__ == "__main__":
    unittest.main()
