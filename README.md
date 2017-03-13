# OnelineFixMiner
Mine one-line fix commit from git repository.
Modified to fetch repository automatically from git url.
In addition, if no url is provided, fetches all the repositories from wordpress plugins.

## Install
You need [GitPython](https://github.com/gitpython-developers/GitPython).

```
$ sudo pip install gitpython
$ sudo pip install ply==3.4
```
## Usage
```
$ ./mine.py <repository git|http repository url (default:fetch all repositories from wordpress plugins)> <branch name (default:master)>
```
