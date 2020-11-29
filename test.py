import github
import requests
import shutil
import os

key = "#45c0#a820f85aa11d727#f02c382#c91d63be83".replace("#", "e")
g = github.Github(key)


for repo in g.get_user().get_repos():
    print(repo.name)
    # to see all the available attributes and methods
    for run in repo.get_workflow_runs():
        print(run)
        # Wait until this shows completed
        print(run.status)
        # the below value is `success`
        print(run.conclusion)
        print(run.created_at)
        r = requests.get(run.logs_url, auth=('tethysapp', key))
        open('test_'+repo.name+'.zip', 'wb').write(r.content)
        shutil.unpack_archive('test.zip', 'logs/'+repo.name)
        os.remove('test_'+repo.name+'.zip')
