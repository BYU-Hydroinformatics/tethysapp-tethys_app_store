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
    
    #Activate tethys environment if not already active
    t

    git clone https://github.com/BYU-Hydroinformatics/warehouse.git
    cd warehouse
    tethys install

