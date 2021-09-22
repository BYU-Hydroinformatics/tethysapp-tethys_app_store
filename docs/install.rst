============
Installation
============

This application can be installed on your local Tethys portal in the following ways: 

Install using Miniconda (Recommended)
*************************************

While using Miniconda install, we need to ensure that the Tethys portal is setup to allow for communication over websockets by setting up an in-memory channel layer:

.. code-block:: shell

	# If you haven't set this already
	tethys settings --set CHANNEL_LAYERS.default.BACKEND channels.layers.InMemoryChannelLayer


Following that, installing the app store is a simple conda install command: 

.. code-block:: shell

	conda install -c tethysapp app_store



Install from GitHub
********************

.. code-block:: shell

	# Activate tethys environment if not already active
	conda activate tethys

	git clone https://github.com/BYU-Hydroinformatics/tethysapp-tethys_app_store.git
	cd tethysapp-tethys_app_store
	tethys install



Updating Installed App Store
****************************

If you installed the app store using the Miniconda command, then run the following command to update the app store to the latest version: 

.. code-block:: shell

	# Activate Tethys environment if not already active
	conda activate tethys

	conda install -c tethysapp app_store

In case you installed the app store from GitHub, just pull the latest changes: 

.. code-block:: shell

	cd <directory_where_app_store_is_installed>
	git pull


Migrating from Warehouse to App Store
****************************

In September, 2021 this package went through a name change and all future updates are published as `app-store` and not `warehouse`. If you have an existing version of the `Tethys App Warehouse` installed on your system, please follow the following steps to update it to the `Tethys App Store`. These steps assume you had installed the warehouse using Miniconda. 

For GitHub installs, please follow the standard uninstall and install new app procedures. 

.. code-block:: shell

	# Activate Tethys environment if not already active
	conda activate tethys

	tethys uninstall warehouse

	conda remove -c tethysplatform --override-channels warehouse

	conda install -c tethysapp app_store

	# Restart your Tethys Instance (If Running in production)

	sudo supervisorctl restart all







