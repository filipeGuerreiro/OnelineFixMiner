#!/usr/bin/env python
from pygithub3 import Github
from requests.auth import HTTPBasicAuth
from slimit import ast
from slimit.parser import Parser
from slimit.visitors import nodevisitor
import git
import sys
import os
import getpass
import requests
import shutil
import re
 

DIR_NAME = "fetched_repos/"
FILE1 = "async_comm_list"
FILE2 = "dom_manip_list"
FILE3 = "event_hand_list"


def main(argv):    
    inputUrl = argv[1] if len(argv) > 1 else ""
    branch = argv[2] if len(argv) > 2 else "master"

    if not inputUrl:
        print "Fetching all repositories from wp-plugins" 
        user = raw_input('Insert your github username: ')
        password = getpass.getpass("Insert your password: ")
        repo_urls = get_all_wp_plugin_repos(user, password)
    else:
        repo_urls = [inputUrl]

    for remoteUrl in repo_urls:
        name = remoteUrl.split("/")[-1]
        if not os.path.exists(DIR_NAME):
            os.mkdir(DIR_NAME)   
        if os.path.exists(DIR_NAME + name):
        	repo = git.Repo(DIR_NAME + name)
        else:
        	repo = git.Repo.init(DIR_NAME + name)
        	origin = repo.create_remote('origin', remoteUrl)
        	origin.fetch()
        	origin.pull(origin.refs[0].remote_head)
        	
        content1 = [line.strip() for line in open(FILE1)]
        content2 = [line.strip() for line in open(FILE2)]
        content3 = [line.strip() for line in open(FILE3)]  
        keyword_list = content1 + content2 + content3

        for c in repo.iter_commits(branch):
            if is_oneline_fix(c):
                diff = diff_parent(c)
                if not diff:
                	continue 
                line = get_diff_line(diff)
                if not line:
                	continue
                if is_ajax_code_heuristic(line, keyword_list):
                	print "=" * 48
                	print "Commit: " + c.hexsha
                	print "Summary: " + c.summary
                	print diff
                	with open(DIR_NAME + name +".out", "a") as output:
                		output.write(diff)
                		

def is_oneline_fix(commit):
    if len(commit.parents) != 1:
        # ignore initial commit or merge commits
        return False
    t = commit.stats.total
    return t['files'] == 1 and t['insertions'] == 1 and t['deletions'] == 1
    

def diff_parent(commit):
    parent = commit.parents[0]
    diff = parent.diff(commit, create_patch=True)[0]
    file_type = diff.a_path.split('.')[-1]
    if file_type == "js" or file_type == "php":
   		return str(diff)
    else:
    	return False
    	
    
def get_diff_line(text):
	pattern = r'^\-.*$(^|\r|\n|\r\n)\+.*$'
	result = re.search(pattern, text, flags = re.MULTILINE)
	if not result:
		return False
	return result.group().split('+')[1]
	

def is_ajax_code_heuristic(line_code, keyword_list):
	parser = Parser()
	if any(word in line_code for word in keyword_list):
		return True
	else:
		return False
		

def get_all_wp_plugin_repos(user, password):
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
    

if __name__ == '__main__':
    main(sys.argv)
