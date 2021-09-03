var get_ts;
var mychart;
//var gemo_data =$("#point-lat-lon").val();
var date_value = new Date($("#select_layer").find('option:selected').val());
var point_grp = L.layerGroup();

$map_element= $('#map');
thredds_wms=$map_element.attr('thredds_wms');


L.TimeDimension.Layer.WMS.TimeSeries = L.TimeDimension.Layer.WMS.extend({

        initialize: function(layer, options) {
            L.TimeDimension.Layer.WMS.prototype.initialize.call(this, layer, options);
        },
});

L.timeDimension.layer.wms.timeseries = function(layer, options) {
    return new L.TimeDimension.Layer.WMS.TimeSeries(layer, options);
};

var map = L.map('map', {
    crs: L.CRS.EPSG3857,
    attributionControl: true,
    attributionControlOptions:{
        position:'bottomright'},
    zoom: 2,
    maxBounds: L.latLngBounds(L.latLng(-90.0,-210.0), L.latLng(90.0,210.0)),
    fullscreenControl: true,
    timeDimension: true,
    timeDimensionOptions:{
    
			 times:"2002-04-16T00:00:00.000Z,2002-05-10T00:00:00.000Z,2002-08-16T12:00:00.000Z,2002-09-16T00:00:00.000Z,2002-10-16T12:00:00.000Z,2002-11-16T00:00:00.000Z,2002-12-16T12:00:00.000Z,2003-01-16T12:00:00.000Z,2003-02-15T00:00:00.000Z,2003-03-16T12:00:00.000Z,2003-04-16T00:00:00.000Z,2003-05-11T12:00:00.000Z,2003-07-16T12:00:00.000Z,2003-08-16T12:00:00.000Z,2003-09-16T00:00:00.000Z,2003-10-16T12:00:00.000Z,2003-11-16T00:00:00.000Z,2003-12-16T12:00:00.000Z,2004-01-07T12:00:00.000Z,2004-02-17T00:00:00.000Z,2004-03-16T12:00:00.000Z,2004-04-16T00:00:00.000Z,2004-05-16T12:00:00.000Z,2004-06-16T00:00:00.000Z,2004-07-16T12:00:00.000Z,2004-08-16T12:00:00.000Z,2004-09-16T00:00:00.000Z,2004-10-16T12:00:00.000Z,2004-11-16T00:00:00.000Z,2004-12-16T12:00:00.000Z,2005-01-16T12:00:00.000Z,2005-02-15T00:00:00.000Z,2005-03-16T12:00:00.000Z,2005-04-16T00:00:00.000Z,2005-05-16T12:00:00.000Z,2005-06-16T00:00:00.000Z,2005-07-16T12:00:00.000Z,2005-08-16T12:00:00.000Z,2005-09-16T00:00:00.000Z,2005-10-16T12:00:00.000Z,2005-11-16T00:00:00.000Z,2005-12-16T12:00:00.000Z,2006-01-16T12:00:00.000Z,2006-02-15T00:00:00.000Z,2006-03-16T12:00:00.000Z,2006-04-16T00:00:00.000Z,2006-05-16T12:00:00.000Z,2006-06-16T00:00:00.000Z,2006-07-16T12:00:00.000Z,2006-08-16T12:00:00.000Z,2006-09-16T00:00:00.000Z,2006-10-16T12:00:00.000Z,2006-11-16T00:00:00.000Z,2006-12-16T12:00:00.000Z,2007-01-16T12:00:00.000Z,2007-02-15T00:00:00.000Z,2007-03-16T12:00:00.000Z,2007-04-16T00:00:00.000Z,2007-05-16T12:00:00.000Z,2007-06-16T00:00:00.000Z,2007-07-16T12:00:00.000Z,2007-08-16T12:00:00.000Z,2007-09-16T00:00:00.000Z,2007-10-16T12:00:00.000Z,2007-11-16T00:00:00.000Z,2007-12-16T12:00:00.000Z,2008-01-16T12:00:00.000Z,2008-02-15T12:00:00.000Z,2008-03-16T12:00:00.000Z,2008-04-16T00:00:00.000Z,2008-05-16T12:00:00.000Z,2008-06-16T00:00:00.000Z,2008-07-16T12:00:00.000Z,2008-08-16T12:00:00.000Z,2008-09-16T00:00:00.000Z,2008-10-16T12:00:00.000Z,2008-11-16T00:00:00.000Z,2008-12-16T12:00:00.000Z,2009-01-16T12:00:00.000Z,2009-02-15T00:00:00.000Z,2009-03-16T12:00:00.000Z,2009-04-16T00:00:00.000Z,2009-05-16T12:00:00.000Z,2009-06-16T00:00:00.000Z,2009-07-16T12:00:00.000Z,2009-08-16T12:00:00.000Z,2009-09-16T00:00:00.000Z,2009-10-16T12:00:00.000Z,2009-11-16T00:00:00.000Z,2009-12-16T12:00:00.000Z,2010-01-16T12:00:00.000Z,2010-02-15T00:00:00.000Z,2010-03-16T12:00:00.000Z,2010-04-16T00:00:00.000Z,2010-05-16T12:00:00.000Z,2010-06-16T00:00:00.000Z,2010-07-16T12:00:00.000Z,2010-08-16T12:00:00.000Z,2010-09-16T00:00:00.000Z,2010-10-16T12:00:00.000Z,2010-11-16T00:00:00.000Z,2010-12-16T12:00:00.000Z,2011-02-18T12:00:00.000Z,2011-03-16T12:00:00.000Z,2011-04-16T00:00:00.000Z,2011-05-16T12:00:00.000Z,2011-07-19T12:00:00.000Z,2011-08-16T12:00:00.000Z,2011-09-16T00:00:00.000Z,2011-10-16T12:00:00.000Z,2011-11-01T12:00:00.000Z,2012-01-02T00:00:00.000Z,2012-01-16T12:00:00.000Z,2012-02-15T12:00:00.000Z,2012-03-16T12:00:00.000Z,2012-04-10T12:00:00.000Z,2012-06-16T00:00:00.000Z,2012-07-16T12:00:00.000Z,2012-08-16T12:00:00.000Z,2012-09-13T00:00:00.000Z,2012-11-20T00:00:00.000Z,2012-12-16T12:00:00.000Z,2013-01-16T12:00:00.000Z,2013-02-14T00:00:00.000Z,2013-04-21T12:00:00.000Z,2013-05-16T12:00:00.000Z,2013-06-16T00:00:00.000Z,2013-07-16T12:00:00.000Z,2013-10-16T12:00:00.000Z,2013-11-16T00:00:00.000Z,2013-12-16T12:00:00.000Z,2014-01-09T12:00:00.000Z,2014-03-17T12:00:00.000Z,2014-04-16T00:00:00.000Z,2014-05-16T12:00:00.000Z,2014-06-13T00:00:00.000Z,2014-08-16T12:00:00.000Z,2014-09-16T00:00:00.000Z,2014-10-16T12:00:00.000Z,2014-11-17T00:00:00.000Z,2015-01-22T12:00:00.000Z,2015-02-15T00:00:00.000Z,2015-03-16T12:00:00.000Z,2015-04-16T00:00:00.000Z,2015-04-27T00:00:00.000Z,2015-07-15T12:00:00.000Z,2015-08-16T12:00:00.000Z,2015-09-14T12:00:00.000Z,2015-12-23T00:00:00.000Z,2016-01-16T12:00:00.000Z,2016-02-14T00:00:00.000Z,2016-03-16T12:00:00.000Z,2016-05-20T12:00:00.000Z,2016-06-16T00:00:00.000Z,2016-07-15T12:00:00.000Z,2016-08-21T12:00:00.000Z,2018-06-16T00:00:00.000Z,2018-07-10T00:00:00.000Z,2018-10-31T12:00:00.000Z,2018-11-16T00:00:00.000Z,2018-12-16T12:00:00.000Z,2019-01-16T12:00:00.000Z,2019-02-14T00:00:00.000Z,2019-03-16T12:00:00.000Z,2019-04-16T00:00:00.000Z,2019-05-16T12:00:00.000Z,2019-06-16T00:00:00.000Z",
             currentTime: Date.parse("2002-04-16T00:00:00.000Z"),
    },
    timeDimensionControl: true,
    timeDimensionControlOptions:{
                position: 'bottomleft',
                playerOptions:{
                        loop:true,
                        startover:true,
                },
                limitSliders:true,
                timeSliderDragUpdate: true,
                loopButton:true,
    },
    center: [15.0, 10.0],
});

//var attribution_control = L.control.attribution({
//        position: 'bottomright'}
//        );
//var src=testWMS+"?REQUEST=GetLegendGraphic&LAYER=lwe_thickness&PALETTE="+type+"&COLORSCALERANGE="+colormin+","+colormax;
//        var div = L.DomUtil.create('div', 'info legend');
//        div.innerHTML +=
//            '<img src="' + src + '" alt="legend" style="width:80%; float:right;">';
//        return div;
//attribution_control.onAdd= function(map) {
//    var attrdiv = L.DomUtil.create('div', 'attribute');
//        attrdiv.innerHTML +=
//            '<div style="width:50%; float:right;">'+attribution_control;
////            Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012';
//        return attrdiv;
//    };
//map.addControl(attribution_control);



var Esri_WorldStreetMap = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri 2012 <a href="https://leaflet-extras.github.io/leaflet-providers/preview/">See Here</a>'
});


var Esri_WorldImagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri 2012 <a href="https://leaflet-extras.github.io/leaflet-providers/preview/">See Here</a>'
});

var Stamen_TonerHybrid = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/toner-hybrid/{z}/{x}/{y}{r}.{ext}', {
	attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
	subdomains: 'abcd',
	minZoom: 0,
	maxZoom: 20,
	ext: 'png'
});


var baseLayers = {
		"ESRI_World_Imagery": Esri_WorldImagery,
		"ESRI World Street Map": Esri_WorldStreetMap,
	};


var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

var drawControlFull = new L.Control.Draw({
            edit: {
                featureGroup: drawnItems,
                edit: false,
            },
            draw: {
                polyline: false,
                circlemarker:false,
                rectangle:false,
                circle:false,
                polygon:false,
            },
});

map.addControl(drawControlFull);

map.on("draw:drawstart ", function (e) {
        drawnItems.clearLayers();
});

map.on("draw:created", function (e) {
        var layer = e.layer;
        layer.addTo(drawnItems);

        var feature = drawnItems.toGeoJSON();
        var type = feature.features[0].geometry.type;
        int_type = type;

        var coords = feature["features"][0]["geometry"]["coordinates"];
        var geom_data = $("#point-lat-lon").val(JSON.stringify(coords));
        get_ts();
});

map.on("draw:edited", function (e) {
        var feature = drawnItems.toGeoJSON();
        var type = feature.features[0].geometry.type;
        int_type = type;

        var coords = feature["features"][0]["geometry"]["coordinates"];
        var geom_data = $("#point-lat-lon").val(JSON.stringify(coords));
        get_ts();
});

map.on('fullscreenchange', function() {
    if (map.isFullscreen()) {
        map.setView(0.0,15.0)}
    else {
        map.setView(0.0,15.0)}});

var signal_process = $("#select_signal_process").find('option:selected').val();
var storage_type = $("#select_storage_type").find('option:selected').val();
//var testWMS="http://127.0.0.1:7000/thredds/wms/testAll/grace/GRC_"+signal_process+"_"+storage_type+".nc"
var testWMS = thredds_wms+"wms/testAll/grace/GRC_"+signal_process+"_"+storage_type+".nc";

var testLayer = L.tileLayer.wms(testWMS, {
    layers: 'grace',
    layers:'lwe_thickness',
    format: 'image/png',
    transparent: true,
    opacity:0.7,
    styles: 'boxfill/grace',
    colorscalerange:'-50,50',
});

var testTimeLayer = L.timeDimension.layer.wms.timeseries(testLayer, {
//	proxy: proxy,
	updateTimeDimension: true,
    name: "Liquid Water Equivalent Thickness",
    units: "cm",
    enableNewMarkers: true
});


var testLegend = L.control({
    position: 'topright'
    });


var layer_control = L.control.layers(baseLayers).addTo(map);
baseLayers.ESRI_World_Imagery.addTo(map);



function updateWMS(){
    map.removeLayer(Stamen_TonerHybrid);
    layer_control.removeLayer(Stamen_TonerHybrid);
    map.removeLayer(testTimeLayer);
    layer_control.removeLayer(testTimeLayer);

    var type=$("#select_legend").find('option:selected').val();
    var signal_process = $("#select_signal_process").find('option:selected').val();
    var storage_type = $("#select_storage_type").find('option:selected').val();
    var storage_name = $("#select_storage_type").find('option:selected').text();
//    var testWMS="http://127.0.0.1:7000/thredds/wms/testAll/grace/GRC_"+signal_process+"_"+storage_type+".nc"
    var testWMS = thredds_wms+"wms/testAll/grace/GRC_"+signal_process+"_"+storage_type+".nc";

    var date_value = new Date($("#select_layer").find('option:selected').val());
    var colormin = $("#col_min").val();
    var colormax = $("#col_max").val();
    var opac = $("#opacity_val").val();
    teststyle='boxfill/'+type;

    testLayer = L.tileLayer.wms(testWMS, {
        layers:'lwe_thickness',
        format: 'image/png',
        transparent: true,
        opacity:opac,
        styles: teststyle,
        colorscalerange:colormin+','+colormax,
        attribution: '<a href="https://www.pik-potsdam.de/">PIK</a>'
    });

    testTimeLayer = L.timeDimension.layer.wms.timeseries(testLayer, {
	    //proxy: proxy,
	    updateTimeDimension: true,
    	name: "Liquid Water Equivalent Thickness (cm)",
    	units: "cm",
    	enableNewMarkers: true,
    });

    layer_control.addOverlay(testTimeLayer, storage_name);

    layer_control.addOverlay(Stamen_TonerHybrid, 'Borders and Labels');

    testTimeLayer.addTo(map);
    Stamen_TonerHybrid.addTo(map);

    testLegend.onAdd= function(map) {

        var src=testWMS+"?REQUEST=GetLegendGraphic&LAYER=lwe_thickness&PALETTE="+type+"&COLORSCALERANGE="+colormin+","+colormax;
        var div = L.DomUtil.create('div', 'info legend');
        div.innerHTML +=
            '<img src="' + src + '" alt="legend" style="width:80%; float:right;">';
        return div;
    };

    testLegend.addTo(map);
    map.timeDimension.setCurrentTime(date_value);
};

function getInstructions() {
    var x = document.getElementById("ts-instructions");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
};


get_ts = function(){
        if($("#point-lat-lon").val() == ""){
            $('.error').html('<b>No feature selected. Please create a feature using the map interaction dropdown. Plot cannot be generated without a feature.</b>');
            return false;
        }else{
            $('.error').html('');
        }

        var storage_type = $("#select_storage_type option:selected").val();
        var signal_process = ($("#select_signal_process option:selected").val());
        var storage_name = $("#select_storage_type option:selected").text();
        var signal_name = ($("#select_signal_process option:selected").text());

        var geom_data = $("#point-lat-lon").val();
        geom_data = geom_data.replace("[","");
        geom_data = geom_data.replace("]","");

        var $loading = $('#view-file-loading');
        $loading.removeClass('hidden');
        $("#plotter").addClass('hidden');
        var xhr = ajax_update_database("get-plot-global",{"storage_type":storage_type,"signal_process":signal_process,"storage_name":storage_name, "signal_name":signal_name, "geom_data":geom_data});
        xhr.done(function(result) {
            if("success" in result) {

                $('.error').html('');
                mychart=Highcharts.stockChart('plotter', {
                    legend: {
                        enabled:true
                    },
                    chart: {
                        zoomType: 'x'
                    },
                    rangeSelector: {
                        selected: testTimeLayer._defaultRangeSelector,
                        buttons: [{

                            type: 'all',
                            text: 'All'
                        }]
                    },
                    title: {
                        text: " Water Storage Anomaly values at " + result.location,
                        style: {
                            fontSize: '14px'
                        }
                    },
                    xAxis: {
//                        type: 'datetime',
//                        labels: {
//                            format: '{value: %d %b %Y}',
//                             rotation: 45,
//                             align: 'left'
//                        },
                        plotLines: [{
                            color: 'red',
                            dashStyle: 'solid',
                            value: new Date(map.timeDimension.getCurrentTime()),
                            width: 2,
                            id: 'pbCurrentTime'
                        }],
                        title: {
                            text: 'Date'
                        }
                    },
                    yAxis: {
                        title: {
                            text: "Storage Volume",
                        }

                    },
                    exporting: {
                        enabled: true
                    },
                    series: [{
                        data:result.values,
                        name: signal_name+' '+storage_name,
                        type: 'area',
                        visible: true,
                        tooltip: {
                            valueDecimals: 2,
                            valueSuffix: ' Liquid Water Eqv. Thickness (cm)',
                            xDateFormat: '%A, %b %e, %Y',
                            headerFormat: '<span style="font-size: 12px; font-weight:bold;">{point.key} (Click to visualize the map on this time)</span><br/>'
                        }
                    },
                    {
                        data:result.integr_values,
                        name: signal_name + storage_name + ' Depletion Curve',
                        type: 'area',
                        visible: false,
                        tooltip: {
                            valueDecimals: 2,
                            valueSuffix: ' Change in Volume since April 16, 2002 (Acre-ft)',
                            xDateFormat: '%A, %b %e, %Y',
                            headerFormat: '<span style="font-size: 12px; font-weight:bold;">{point.key} (Click to visualize the map on this time)</span><br/>'
                        }
                    },
                    ],
                    lang: {
                        noData:'There is no data to display.  Please select a point where data exists.'
                    },
                    noData: {
                        style: {
                            fontWeight: 'bold',
                            fontSize: '15px',
                            color: '#303030'
                        }
                    },

                    plotOptions: {
                        series: {
                            cursor: 'pointer',
                            point: {
                                events: {
                                    click: (function(event) {
                                        var day = new Date(event.point.x);
                                        map.timeDimension.setCurrentTime(day.getTime());
                                    }).bind(this)
                                }
                            }
                        }
                    }
                });
                updateChart = function () {



                if (!mychart){
                    return;
                }
                var tot_series = mychart.series[0];
                var sw_series = mychart.series[1];
                var soil_series = mychart.series[2];
                var gw_series = mychart.series[3];

                var storage_type = $("#select_storage_type option:selected").val();


                if (storage_type = "tot"){
                    tot_series.show() }
                else if (storage_type = "sw"){
                    sw_series.show() }
                else if (storage_type = "soil"){
                    soil_series.show() }
                else if (storage_type = "gw"){
                    gw_series.show() }
                };
            //    updateChart();



                map.timeDimension.on('timeload', (function() {
                    if (!mychart){
                    return;
                    }
                    mychart.xAxis[0].removePlotBand("pbCurrentTime");
                    mychart.xAxis[0].addPlotLine({
                        color: 'red',
                        dashStyle: 'solid',
                        value: new Date(map.timeDimension.getCurrentTime()),
                        width: 2,
                        id: 'pbCurrentTime'
                    });
                }));
//                updateChart();
                $loading.addClass('hidden');
                $("#plotter").removeClass('hidden');
            }
            else {
                $(".error").append('<h3>Error Processing Request.</h3>');
                $loading.addClass('hidden');
                $("#plotter").removeClass('hidden');
            }
        });

    };

// updateChart = function () {
//                    if (!mychart){
//                    return;
//                    }
//
//                    tot_series.hide();
//                    sw_series.hide();
//                    soil_series.hide();
//                    gw_series.hide();
//
//                    var storage_type = $("#select_storage_type option:selected").val();
//                    var signal_process = ($("#select_signal_process option:selected").val());
//                    var storage_name = $("#select_storage_type option:selected").text();
//                    var signal_name = ($("#select_signal_process option:selected").text());
//
//                    var tot_series = mychart.series[0];
//                    var sw_series = mychart.series[1];
//                    var soil_series = mychart.series[2];
//                    var gw_series = mychart.series[3];
//
//                    if (storage_type = "tot"){
//                        var active_series = tot_series }
//                    else if (storage_type = "sw"){
//                        var active_series = sw_series }
//                    else if (storage_type = "soil"){
//                        var active_series = soil_series }
//                    else if (storage_type = "gw"){
//                        var active_series = gw_series }
//
//                    active_series.show();
//
//                    };

function getSignalGuide (){
    $("#signal-modal").modal('show');

};

function getStorageGuide (){
    $("#storage-modal").modal('show');

};


$(function(){
    updateWMS();

    $("#select_signal_process").change(function(){
        updateWMS();
        get_ts();
    }).change();

    $("#select_storage_type").change(function(){
        updateWMS();
        get_ts();
//        updateChart();
    }).change;

    $("#select_layer").change(function(){
        updateWMS();
    }).change();

    $("#select_legend").change(function(){
        updateWMS();
    }).change;


});



