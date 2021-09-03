from tethys_sdk.base import TethysAppBase, url_map_maker


class HistoricalValidationToolMadeiraRiver(TethysAppBase):
    """
    Tethys app class for Historical Validation Tool Colombia.
    """

    name = 'Hydroviewer Madeira'
    index = 'hydroviewer_madeira_river:home'
    icon = 'hydroviewer_madeira_river/images/byu_logo.png'
    package = 'hydroviewer_madeira_river'
    root_url = 'hydroviewer-madeira-river'
    color = '#002255'
    description = 'This app evaluates the accuracy for the historical streamflow values obtained from Streamflow Prediction Tool in Madeira River Basin.'
    tags = 'Hydrology'
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='hydroviewer-madeira-river',
                controller='hydroviewer_madeira_river.controllers.home'
            ),
            UrlMap(
                name='get_discharge_data',
                url='get-discharge-data',
                controller='hydroviewer_madeira_river.controllers.get_discharge_data'
            ),
            UrlMap(
                name='get_simulated_data',
                url='get-simulated-data',
                controller='hydroviewer_madeira_river.controllers.get_simulated_data'
            ),
            UrlMap(
                name='get_simulated_bc_data',
                url='get-simulated-bc-data',
                controller='hydroviewer_madeira_river.controllers.get_simulated_bc_data'
            ),
            UrlMap(
                name='get_hydrographs',
                url='get-hydrographs',
                controller='hydroviewer_madeira_river.controllers.get_hydrographs'
            ),
            UrlMap(
                name='get_dailyAverages',
                url='get-dailyAverages',
                controller='hydroviewer_madeira_river.controllers.get_dailyAverages'
            ),
            UrlMap(
                name='get_monthlyAverages',
                url='get-monthlyAverages',
                controller='hydroviewer_madeira_river.controllers.get_monthlyAverages'
            ),
            UrlMap(
                name='get_scatterPlot',
                url='get-scatterPlot',
                controller='hydroviewer_madeira_river.controllers.get_scatterPlot'
            ),
            UrlMap(
                name='get_scatterPlotLogScale',
                url='get-scatterPlotLogScale',
                controller='hydroviewer_madeira_river.controllers.get_scatterPlotLogScale'
            ),
            UrlMap(
                name='get_volumeAnalysis',
                url='get-volumeAnalysis',
                controller='hydroviewer_madeira_river.controllers.get_volumeAnalysis'
            ),
            UrlMap(
                name='volume_table_ajax',
                url='volume-table-ajax',
                controller='hydroviewer_madeira_river.controllers.volume_table_ajax'
            ),
            UrlMap(
                name='make_table_ajax',
                url='make-table-ajax',
                controller='hydroviewer_madeira_river.controllers.make_table_ajax'
            ),
            UrlMap(
                name='get-time-series',
                url='get-time-series',
                controller='hydroviewer_madeira_river.controllers.get_time_series'),
            UrlMap(
                name='get-time-series-bc',
                url='get-time-series-bc',
                controller='hydroviewer_madeira_river.controllers.get_time_series_bc'),
            UrlMap(
                name='get_observed_discharge_csv',
                url='get-observed-discharge-csv',
                controller='hydroviewer_madeira_river.controllers.get_observed_discharge_csv'
            ),
            UrlMap(
                name='get_simulated_discharge_csv',
                url='get-simulated-discharge-csv',
                controller='hydroviewer_madeira_river.controllers.get_simulated_discharge_csv'
            ),
            UrlMap(
                name='get_simulated_bc_discharge_csv',
                url='get-simulated-bc-discharge-csv',
                controller='hydroviewer_madeira_river.controllers.get_simulated_bc_discharge_csv'
            ),
            UrlMap(
                name='get_forecast_data_csv',
                url='get-forecast-data-csv',
                controller='hydroviewer_madeira_river.controllers.get_forecast_data_csv'
            ),
            UrlMap(
                name='get_forecast_bc_data_csv',
                url='get-forecast-bc-data-csv',
                controller='hydroviewer_madeira_river.controllers.get_forecast_bc_data_csv'
            ),
        )

        return url_maps
