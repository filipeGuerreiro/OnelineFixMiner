#!/usr/bin/env python
import git
import sys
import os
from pygithub3 import Github
import getpass
import requests
from requests.auth import HTTPBasicAuth
import shutil

DIR_NAME = "fetched_repos/"

def is_oneline_fix(commit):
    if len(commit.parents) != 1:
        # ignore initial commit or merge commits
        return False
    t = commit.stats.total
    return t['files'] == 1 and t['insertions'] == 1 and t['deletions'] == 1

def diff_parent(commit):
    parent = commit.parents[0]
    diff = parent.diff(commit, create_patch=True)[0]
    #print dir(diff)
    return diff.diff

def get_all_repos(user, password):
    repo_urls = []
    page = 1
    while True:
        url = 'https://api.github.com/orgs/wp-plugins/repos?per_page=100&page={0}'
        r = requests.get(url.format(page), auth = HTTPBasicAuth(user, password))
        if r.status_code == 200:
            rdata = r.json()
            for repo in rdata:
                repo_urls.append(repo['clone_url'])
            if (len(rdata) >= 100):
                page = page + 1
		print('{0} repos so far'.format(len(repo_urls)))
            else:
                print('Found {0} repos.'.format(len(repo_urls)))
                break
        else:
            print(r)
            return repo_urls
    return repo_urls

def main(argv):    
    inputUrl = argv[1] if len(argv) > 1 else ""
    branch = argv[2] if len(argv) > 2 else "master"

    if not inputUrl:
        print "Fetching all repositories from wp-plugins" 
        user = raw_input('Insert your github username: ')
        password = getpass.getpass("Insert your password: ")
        repo_urls = get_all_repos(user, password)
    else:
        repo_urls = [inputUrl]

    for remoteUrl in repo_urls:
        name = remoteUrl.split("/")[-1]
        if not os.path.exists(DIR_NAME):
            os.mkdir(DIR_NAME)   
        if os.path.exists(DIR_NAME + name):
            shutil.rmtree(DIR_NAME + name)
            os.mkdir(DIR_NAME + name)
        repo = git.Repo.init(DIR_NAME + name)
        origin = repo.create_remote('origin', remoteUrl)
        origin.fetch()
        origin.pull(origin.refs[0].remote_head)

        for c in repo.iter_commits(branch):
            if is_oneline_fix(c):
                print "=" * 48
                print "Commit: " + c.hexsha
                print "Summary: " + c.summary
                diff = diff_parent(c)
                with open(DIR_NAME + name +".out", "a") as output:
                    output.write(diff)

if __name__ == '__main__':
    main(sys.argv)
