===================
GitHub Install API
===================

The warehouse has added the following methods to support installation via GitHub Actions. The repository will need to have public access. 

/install/git/
*************************************

You will need to provide the following information as a POST request. The Branch parameter is optional and will pull the master/main branch if no branch is specified. 

.. code-block:: JSON

    {
        url: "Your GitHub Repository URL",
        branch: "GitHub Branch to be installed"
    }


You would also need to provide the following ``Authorization`` Header: ``Token <INSERT YOUR TOKEN HERE>``. The token can be obtained for your user on the user management page (http://[HOST_Portal]/user/[username]/).

This endpoint returns a unique Installation id (``install_id``) that can be used in the other two requests below

/install/git/status?install_id=
********************

GET endpoint to get the status report for a specific install_id

/install/git/logs?install_id=
********************

GET endpoint to get the logs for a specific install_id


