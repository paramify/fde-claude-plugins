#!/usr/bin/env python3
"""PreToolUse hook: block a git push that creates a branch on a paramify GitHub repo unless it's named fde-<n>."""
import json
import os
import re
import shlex
import subprocess
import sys

ISSUE_BRANCH = re.compile(r"^fde-[0-9]+$")
PARAMIFY_URL = re.compile(r"github\.com[:/]paramify/")
ALWAYS_ALLOWED = {"main", "master", "added-validators"}
PUNCTUATION = ";&|()<>\n"
PREFIXES = {"!", "{", "}", "do", "then", "else", "elif", "if", "while", "until", "time", "command", "exec", "env", "nohup"}
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
GIT_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env"}


def git(repo, *args):
    try:
        r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def unresolvable(word):
    return any(c in word for c in "$`*")


def segments(command):
    lex = shlex.shlex(command.replace("\\\n", " "), posix=True, punctuation_chars=PUNCTUATION)
    lex.whitespace = " \t\r"
    lex.whitespace_split = True
    seg = []
    for tok in lex:
        if tok and set(tok) <= set(PUNCTUATION) and not set(tok) & set("<>"):
            if seg:
                yield seg
            seg = []
        else:
            seg.append(tok)
    if seg:
        yield seg


def strip_redirects(words):
    out, skip = [], False
    for w in words:
        if skip:
            skip = False
        elif w and set(w) <= set("<>&|"):
            # Drop the operator, its target, and an fd number before it.
            if out and out[-1].isdigit():
                out.pop()
            skip = True
        else:
            out.append(w)
    return out


def push_problems(command, cwd):
    problems = []
    for words in segments(command):
        words = strip_redirects(words)
        while words and (words[0] in PREFIXES or ASSIGNMENT.match(words[0])):
            words = words[1:]
        if not words:
            continue
        name = os.path.basename(words[0])
        if name in ("cd", "pushd"):
            target = words[1] if len(words) > 1 else "~"
            if cwd is None or unresolvable(target) or target == "-":
                cwd = None
            else:
                cwd = os.path.normpath(os.path.join(cwd, os.path.expanduser(target)))
        elif name in ("bash", "sh", "zsh") and "-c" in words[1:-1]:
            problems += push_problems(words[words.index("-c") + 1], cwd)
        elif name == "git" and cwd is not None:
            problems += check_git(words[1:], cwd)
    return problems


def check_git(args, cwd):
    repo, i = cwd, 0
    while i < len(args) and args[i].startswith("-"):
        opt = args[i]
        if opt in GIT_OPTS_WITH_VALUE:
            if opt == "-C" and i + 1 < len(args):
                if unresolvable(args[i + 1]):
                    return []
                repo = os.path.join(repo, os.path.expanduser(args[i + 1]))
            i += 2
        else:
            i += 1
    if i >= len(args) or args[i] != "push":
        return []
    return check_push(args[i + 1:], repo)


def check_push(args, repo):
    if any("`" in a for a in args):
        return []
    remote, refspecs, every_branch, tags = None, [], False, False
    positional_only = False
    it = iter(args)
    for a in it:
        if positional_only or not a.startswith("-") or a == "-":
            if remote is None:
                remote = a
            else:
                refspecs.append(a)
        elif a == "--":
            positional_only = True
        elif a.startswith("--"):
            opt = a.split("=", 1)[0]
            if opt in ("--delete", "--dry-run"):
                return []
            if opt in ("--all", "--branches", "--mirror"):
                every_branch = True
            elif opt == "--tags":
                tags = True
            elif opt == "--repo":
                remote = a.split("=", 1)[1] if "=" in a else next(it, None)
            elif opt in ("--push-option", "--receive-pack", "--exec") and "=" not in a:
                next(it, None)
        else:
            for j, flag in enumerate(a[1:]):
                if flag in "dn":
                    return []
                if flag == "o":
                    if j == len(a) - 2:
                        next(it, None)
                    break

    if tags and not refspecs and not every_branch:
        return []
    current = git(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    if remote is None:
        remote = (
            (current and git(repo, "config", f"branch.{current}.pushRemote"))
            or git(repo, "config", "remote.pushDefault")
            or (current and git(repo, "config", f"branch.{current}.remote"))
            or "origin"
        )
    if unresolvable(remote):
        return []
    remote_name, url = remote, git(repo, "remote", "get-url", "--push", remote)
    if url is None:
        # A URL rather than a remote name: find the remote it belongs to, for its tracking refs.
        url, remote_name = remote, None
        for name in (git(repo, "remote") or "").split():
            if git(repo, "remote", "get-url", "--push", name) == url:
                remote_name = name
    if not PARAMIFY_URL.search(url) or remote_name is None:
        return []

    if every_branch:
        branches = (git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads/") or "").split()
    elif refspecs:
        branches = [b for b in (dest_branch(s, repo, current) for s in refspecs) if b]
    else:
        branches = [default_dest(repo, current, remote)] if current else []

    return [
        (b, remote_name)
        for b in branches
        if b
        and b not in ALWAYS_ALLOWED
        and not ISSUE_BRANCH.match(b)
        and git(repo, "rev-parse", "--verify", "--quiet", f"refs/remotes/{remote_name}/{b}") is None
    ]


def default_dest(repo, current, remote):
    if git(repo, "config", f"remote.{remote}.push"):
        return None
    mode = git(repo, "config", "push.default") or "simple"
    if mode in ("matching", "nothing"):
        return None
    merge = git(repo, "config", f"branch.{current}.merge") or ""
    if mode in ("upstream", "tracking") and merge.startswith("refs/heads/"):
        return merge[len("refs/heads/"):]
    return current


def dest_branch(spec, repo, current):
    """The branch a refspec writes to on the remote, or None for tags, deletions and refspecs we can't resolve."""
    spec = spec.lstrip("+")
    if unresolvable(spec) or spec.startswith(":"):
        return None
    if ":" in spec:
        src, dst = spec.split(":", 1)
        dst = dst or src
    else:
        src = dst = spec
        if spec in ("HEAD", "@"):
            return current
    if dst in ("HEAD", "@"):
        return None
    if dst.startswith("refs/heads/"):
        return dst[len("refs/heads/"):]
    if dst.startswith("refs/") or src.startswith("refs/tags/"):
        return None
    if git(repo, "show-ref", "--verify", "--quiet", f"refs/tags/{src}") is not None and \
            git(repo, "show-ref", "--verify", "--quiet", f"refs/heads/{src}") is None:
        return None
    return dst


def main():
    try:
        event = json.load(sys.stdin)
        if event.get("tool_name") != "Bash":
            return 0
        command = (event.get("tool_input") or {}).get("command") or ""
        if "push" not in command:
            return 0
        problems = push_problems(command, event.get("cwd") or os.getcwd())
    except Exception:
        return 0
    if not problems:
        return 0
    for branch, remote in problems:
        print(
            f"Blocked: this push would create the branch '{branch}' on '{remote}', a paramify GitHub repo. "
            "New branches there are named for their Linear issue: the issue ID alone, lowercase, like fde-123 "
            "(fde-<n>). Rename it with `git branch -m fde-<n>` and push again. Don't use Linear's copied "
            f"branch name; it carries the issue title. If '{branch}' already exists on the remote, "
            f"run `git fetch {remote}` and push again.",
            file=sys.stderr,
        )
    return 2


if __name__ == "__main__":
    sys.exit(main())
