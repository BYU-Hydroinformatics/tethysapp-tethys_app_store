===================
GitHub Install API
===================

The app store has added the following methods to support installation via GitHub Actions. The app repository will need to have public access for this installation method to work. This method is meant for apps that are being developed and tested in a specific portal. It facilitates direct app installation that can trigger on a push or release event from a GitHub repository. For final operational installations, we recommend publishing the app package to the Tethysapp conda channel using the Tethys App Store interface.

/install/git/
*************

You will need to provide the following information as a POST request. The Branch parameter is optional and will pull the master/main branch if no branch is specified.

.. code-block:: js

    {
        url: "Your GitHub Repository URL",
        branch: "GitHub Branch to be installed",
        develop: True //Optional Parameter. By default the application is NOT installed in develop mode. 
    }


You would also need to provide the following ``Authorization`` Header: ``Token <INSERT YOUR TOKEN HERE>``. The token can be obtained for your user on the user management page (http://[HOST_Portal]/user/[username]/).

This endpoint returns a unique Installation id (``install_id``) that can be used in the other two requests below

/install/git/status?install_id=
*******************************

GET endpoint to get the status report for a specific install_id

/install/git/logs?install_id=
*****************************

GET endpoint to get the logs for a specific install_id

==============
GitHub Actions
==============

The basic workflow for installing `Tethys` applications directly from Github uses three main github actions. the following table includes links to the specific documentation for each of these actions

.. list-table:: Github actions used for installing Tethys applications from Github
   :widths: 25 50 10
   :header-rows: 1

   * - Action
     - Description
     - Home
   * - tethys-app-linter
     - A GitHub Action to check the code integrity of Tethys applications.
     - `Link <https://github.com/marketplace/actions/tethys-app-linter>`_
   * - flake8-check-action
     - A GitHub action to run Flake8 against your code
     - `Link <https://github.com/marketplace/actions/flake8-check-action>`_
   * - http-request-action
     - A GitHub action to create HTTP Requests from GitHub Actions.
     - `Link <https://github.com/marketplace/actions/http-request-action>`_

Github action example
*********************

.. code-block:: YML

    name: tethys-app-installation

    on: [release]

    jobs:
      app-lint:
        runs-on: ubuntu-latest
        name: Tethys App Lint
        steps:
        - name: Checkout
          uses: actions/checkout@v2
        - name: Run tethys-app-linter
          uses: tethysapp/tethys-app-linter@v1
      flake:
        runs-on: ubuntu-latest
        name: Flake8
        steps:
        - name: Checkout
          uses: actions/checkout@v2
        - name: Run flake
          uses: tonybajan/flake8-check-action@v1.0.0
          with:
            select: E,W,F  # check for pep8 and pyflakes errors
            maxlinelength: 120
            repotoken: ${{ secrets.GITHUB_TOKEN }}
      deployment:
        runs-on: ubuntu-latest
        name: Deployment
        needs: lint
        steps:
        - name: Get Variables
          id: vars
          run: echo ::set-output name=short_ref::${GITHUB_REF##*/}
        - name: Deploy Stage
          uses: fjogeleit/http-request-action@master
          with:
            method: 'POST'
            url: 'https://tethys-staging.byu.edu/apps/warehouse/install/git/'
            data: '{"url": "https://github.com/${{ github.repository }}.git", "branch": "${{ steps.vars.outputs.short_ref }}"}'
            customHeaders: '{"Authorization": "Token ${{ secrets.TETHYS_AUTH_TOKEN }}"}'

.. NOTE::

    An authorization token is needed to send a request to a specific Tethys portal. This token can be obtained from the API Key parameter in the user account home page of the Tethys portal. We recommend this token is added to the secrets of the github repo that is triggering this workflow. For more information on how to do this see `How to create secrets on Github <https://docs.github.com/en/actions/reference/encrypted-secrets#creating-encrypted-secrets-for-an-environment>`_

.. NOTE::

    This Installation method is meant for apps that are being developed and continue to change in a regular basis. It makes it possible to trigger an app installation update based on a push or release GitHub event.
