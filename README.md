# Tethys Application Warehouse

## Installation

```sh
# If you haven't set this already
tethys settings --set CHANNEL_LAYERS.default.BACKEND channels.layers.InMemoryChannelLayer

conda install -c tethysapp warehouse
```

## Testing

To help out with testing this application on your local installation, please follow these instructions:

-   Please feel free to take any notes or screenshots during the below process that might help me identify issues. You may also submit a copy of the logs you see in your terminal in the google form while reporting.
-   Feel free to reach out to me on Slack if you have any questions.
-   Ensure you have Tethys 3 installed. [Click Here](http://docs.tethysplatform.org/en/stable/installation.html) for installation docs.
-   If you have a locally installed version of `snow-inspector`, remove any existing installation of the app `snow-inspector`
    -   `tethys list` will show you the list of your locally installed applications
    -   You can use `tethys uninstall snow_inspector` to remove the application, if it exists.
-   Clone and install this application. Ensure your tethys environment is active before following the steps below

```sh
git clone https://github.com/BYU-Hydroinformatics/warehouse
cd warehouse
tethys install -d
```

-   Start your Tethys development server : `tethys manage start`
-   Navigate to `localhost:8000/apps/warehouse` on your web browser. You may be asked to log in. The default username and password for tethys installations is `admin` and `pass` respectively.
-   Install the application `snow_inspector` by clicking on it. Select the default version and click `go`
-   Please let the install process complete. Once done it will show a message `Install Complete`.
-   Restart your local tethys instance
    -   Use `ctrl+c` in your terminal to exit from the development server. Use `tethys manage start` to start it up again.
-   Navigate to `localhost:8000/apps/` and you should see a new app `Snow Inspector` installed on your local portal.
-   Click on `Snow Inspector` to navigate the application if you would like to and explore it.
-   Navigate back to the warehouse app `localhost:8000/apps/warehouse`
-   Let's try installing the `servicetest` application. Please follow the above instructions for the `servicetest` app. The idea of the warehouse is to be intuitive so I am deliberately not providing instructions for this step.
-   You will see a couple new screens during the install process. The first one allows you to enter a value for a couple custom settings. You may choose to skip that configuration. The second new screen will allow you to set the services that this application needs. You may wish to explore this and report any issues you see or you can skip that configuration.
-   Finally, restart and go back to the apps page on your tethys portal. You should see a listing for `servicetest` there.

### Reporting

Please report your results using the googleform: https://forms.gle/G1ciYDksX426eviY6

### Cleanup

To uninstall and clear out the above testing files from your local system:

-   Activate your tethys environment if not already.
    -   This can be done by `conda activate tethys` for default installations
-   Run the following commands

```sh
tethys uninstall snow_inspector -f
conda remove -c tethysplatform --override-channels snow_inspector
```

-   You may also choose to remove the warehouse app : `tethys uninstall warehouse -f`

## Compatibility

## Publications

## Future Improvements

## Developers and Funding
