
# from tethysapp.app_store.app import AppStore as app_store
from tethysapp.app_store.submission_handlers import pull_git_repo
# from tethysapp.app_store.utilities import decrypt
# from dotenv import load_dotenv,dotenv_values

# from tethys_sdk.testing import TethysTestCase

# from tethysapp.app_store.helpers import send_notification
from unittest import mock  # because unittest's mock works great with pytest
# import shutil
import os
# from django.test import Client
# from django.test import TestCase
import github

import pytest
# import django 
# django.setup()
github_repos = [
    "https://github.com/BYU-Hydroinformatics/tethysapp-hydrafloods.git", #hydrafloods app
    "https://github.com/BYU-Hydroinformatics/Water-Data-Explorer.git" # water_data_explorer app
]


# load_dotenv(dotenv_path=os.path.join(os.getcwd(),"app_store/tests/.env"))
# config = dotenv_values()

stores = [
    {
       "default": True,
       "conda_labels": [
         "main",
         "dev"
       ],
       "github_token": "gAAAAABj-CqGQzM2cZga_ISIPgyOFcR-uxHxtfqnqSs96XN210wAP4dPgKHWueKphMu3cXqMaIOpx49VzEblsJVkwhgUbphZ9WaSIKqEmqk2Bi_mf_hLgDX4EnvIpKqs5iDxOqo25vXi",
       "conda_channel": "tethysapp",
       "github_organization": "tethysapp"
     },
    {
      "default": False,
      "conda_labels": [
        "main",
        "dev"
      ],
      "github_token": "gAAAAABj_jTAaNDK1OAxfswFwQwpoYDd4NZzVgpV1H4ol2Zh2zrg9hPXtGHkKPfjHBRayw9wEkb3ByJwbOgk3Xj7iPJl_QC_VPxtoRuPIESl_jYuohoGlBbIdaU9tEH347Wqp9-7fg4i",
      "conda_channel": "elkingio",
      "github_organization": "lost-melancholic-tribe"
    }
]


class TestSubmissionHandlers:


    # @pytest.mark.parametrize("mock_os_exits_results",[False,False,False,True])
    # @mock.patch("tethysapp.app_store.submission_handlers.os.path.exists", autospec=True)
    @pytest.mark.django_db
    @pytest.mark.parametrize("github_url",github_repos)
    @pytest.mark.parametrize("active_store",stores)
    @mock.patch("tethysapp.app_store.submission_handlers.send_notification")
    def test_pull_git_repo(self,mock_send_notification, active_store,github_url):
        fake_app_workspace_path = '/home/gio/tethysdev/applications/tethysapp-tethys_app_store/tethysapp/app_store/tests/fake_app_workspace'
        mock_send_notification.return_value = "Fake notification sent"
        
        app_workspace = mock.MagicMock()
        app_workspace.path = fake_app_workspace_path
        # def side_os_exists_effect(args):
        #     return mock_os_exits_results
        
        # mock_exists.side_effect = side_os_exists_effect

        channel_layer = mock.MagicMock()

        ## get the branches manually to use assert ##
        g = github.Github()
        repo_name = github_url.split("/")[-1].replace(".git", "")
        user = github_url.split("/")[-2]
        github_object_api = github.Github()
        repo = github_object_api.get_repo(f'{user}/{repo_name}')
        branches = list(repo.get_branches())
        list_branch = []
        for branch in branches:
            list_branch.append(branch.name)

        ## get the github dir path
        app_name = github_url.split("/")[-1].replace(".git", "")
        fake_app_path  = os.path.join(fake_app_workspace_path,"gitsubmission",active_store['conda_channel'],app_name)
        get_data_json = {
            "data": {
                "branches": list_branch,
                "github_dir": fake_app_path,
                "conda_channel": active_store['conda_channel'],
                "github_token": active_store['github_token'],
                "conda_labels": active_store['conda_labels'],
                "github_organization": active_store['github_organization']
            },
            "jsHelperFunction": "showBranches",
            "helper": "addModalHelper"
        }

        pull_git_repo(github_url,active_store, channel_layer, app_workspace)

        mock_send_notification.assert_called_with(get_data_json,channel_layer)


