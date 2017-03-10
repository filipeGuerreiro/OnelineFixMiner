# OnelineFixMiner
Mine one-line fix commit from git repository.
Modified to fetch repository automatically from git url.
In addition, if no url is provided, fetches all the repositories from wordpress plugins.

## Install
You need [GitPython](https://github.com/gitpython-developers/GitPython).

```
$ sudo pip install gitpython
```
## Usage
```
$ ./mine.py <repository remote url (default:fetch all repositories from wordpress plugins)> <branch name (default:master)>
```
