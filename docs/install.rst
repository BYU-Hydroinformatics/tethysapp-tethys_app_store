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


Following that, installing the warehouse is a simple conda install command: 

.. code-block:: shell

	conda install -c tethysapp warehouse



Install from GitHub
********************

.. code-block:: shell

	# Activate tethys environment if not already active
	conda activate tethys

	git clone https://github.com/BYU-Hydroinformatics/tethysapp-tethys_app_store.git
	cd tethysapp-tethys_app_store
	tethys install



Updating Installed Warehouse
****************************

If you installed the warehouse using the Miniconda command, then run the following command to update the warehouse to the latest version: 

.. code-block:: shell

	# Activate Tethys environment if not already active
	conda activate tethys

	conda install -c tethysapp warehouse

In case you installed the warehouse from GitHub, just pull the latest changes: 

.. code-block:: shell

	cd <directory_where_warehouse_is_installed>
	git pull


