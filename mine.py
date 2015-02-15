#!/usr/bin/env python
import git
import sys

def is_oneline_fix(commit):
    if len(commit.parents) != 1:
        # ignore initial commit or merge commits
        return False
    t = commit.stats.total
    return t['files'] == 1 and t['insertions'] == 1 and t['deletions'] == 1

def diff_parent(commit):
    parent = commit.parents[0]
    print parent.diff(commit, create_patch=True)[0].diff

def main(argv):
    path = argv[1] if len(argv) > 1 else "."
    branch = argv[2] if len(argv) > 2 else "master"
    repo = git.Repo(path)
    for c in repo.iter_commits(branch):
        if is_oneline_fix(c):
            print "=" * 48
            print "Commit: " + c.hexsha
            print "Summary: " + c.summary
            print diff_parent(c)

if __name__ == '__main__':
    main(sys.argv)
