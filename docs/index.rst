.. Tethys App Warehouse documentation master file, created by
   sphinx-quickstart on Thu Sep  3 14:24:30 2020.
  
Welcome to Tethys App Warehouse's documentation!
================================================

The Tethys App Warehouse is similar in concept to the iOS App Store for Apple mobile devices or the Google Play Store for Android mobile devices, but exclusively for Tethys Applications. The Tethys App Warehouse aims to make web applications portable by packaging Tethys Applications and hosting it on Miniconda repositories. The warehouse includes an option for developers to contribute their applications by following a two-step work-flow within the warehouse user interface, while the warehouse takes care of all the heavy lifting of correctly preparing the code and making it available as an easily installable Miniconda package. 


.. warning::
   This documentation as well as application is under development. 


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



Application Submission
========================

Before attempting to submit your application to the warehouse, ensure that your application fulfills the requirements for Tethys App Warehouse: 

- Application is compatible with Tethys 3+
- Application should run on Python 3.7+
- Cleanup old init files if the application was upgraded from an older Tethys 2 compatible version.: https://gist.github.com/rfun/ca38bb487ca1649be8491227adb7ca37


Application Metadata + setup.py
*******************************

The build process uses the setup.py file to pull the metadata for your application. The following fields are pulled from the setup.py and are displayed in the application warehouse: 

- Application name (Same as release package)
- Version
- Description
- Keywords
- Author Name
- Author Email
- URL
- License

It is recommended to fill in the values in your setup.py so that your application has those details visible in the warehouse for easier discovery and filtering. 

Each time you have a new version for your application, it is recommended to update the version number in your setup.py file so that a new package is built and published. 

Steps to Submit
***************

Developers can submit their applications to the warehouse by click on the Add App button as highlighted in the image below: 

.. image:: images/add_button.png
   :width: 600


Upon clicking that button, you will be presented with a modal that asks for the link to the GitHub Repository of your Tethys Application. 

.. image:: images/add_process.png
   :width: 600

- Enter the link to your GitHub Repository 
- If there are multiple branches on your GitHub repository, you will be presented with a list of branches on your GitHub repository, Select the branch that you would like to submit to the application warehouse. The warehouse uses the Master branch in case 
- After selecting the branch the warehouse begins the processing. Currently there isn't a good system to inform the user about the application submitted, but we are working on that. 



.. toctree::
   :maxdepth: 2
   :caption: Contents:

