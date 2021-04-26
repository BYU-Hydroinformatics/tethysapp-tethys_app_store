======================
Application Submission
======================

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

.. image:: _static/images/add_button.png
   :width: 600


Upon clicking that button, you will be presented with a modal that asks for the link to the GitHub Repository of your Tethys Application. It also instructs to put in an email address which is notified once the build is completed successfully and the application is available on the warehouse.

.. image:: _static/images/add_step_1.png
   :width: 600

- Enter Notification email address (Mostly this will be your own or the developer's email address)
- Enter the link to your GitHub Repository 
- If there are multiple branches on your GitHub repository, you will be presented with a list of branches on your GitHub repository, Select the branch that you would like to submit to the application warehouse. The warehouse uses the Master branch in case 
- After selecting the branch the warehouse begins the processing. Once the build is done, an email will be sent to the address provided.


.. note::
   After your application is successfully built, you will need to tell the warehouse to refresh your local list of applications. To do this click on the refresh button as shown in the image below.

.. image:: _static/images/refresh_button.png
	:width: 600


