var init_vars
var point_grp = L.layerGroup();
var get_ts;
var mychart;

L.TimeDimension.Layer.WMS.TimeSeries = L.TimeDimension.Layer.WMS.extend({

        initialize: function(layer, options) {
            L.TimeDimension.Layer.WMS.prototype.initialize.call(this, layer, options);
        },
});

L.timeDimension.layer.wms.timeseries = function(layer, options) {
    return new L.TimeDimension.Layer.WMS.TimeSeries(layer, options);
};

init_vars = function(){
        $region_element= $('#region');
        bbox =  $region_element.attr('data-bbox');
        bbox = JSON.parse(bbox);
        map_center = $region_element.attr('data-map-center');
        map_center = JSON.parse(map_center);
        wms_url = $region_element.attr('data-wms-url');
        region_name =$region_element.attr('lower_name');
        region_name_upper=$region_element.attr('upper-name');
        thredds_wms=$region_element.attr('thredds_wms');
        regioncenter = map_center;
        region_area = $region_element.attr('region-area');
};

init_vars()
var region =region_name;
var regioncenter = map_center;

//add a map to the html div "map" with time dimension capabilities. Times are currently hard coded, but will need to be changed as new GRACE data comes
var map = L.map('map', {
    crs: L.CRS.EPSG3857,
    zoom: 4,
//    drawControl: true,
    fullscreenControl: true,
    timeDimension: true,
    timeDimensionOptions:{

			 times:"2002-04-16T00:00:00.000Z,2002-05-10T00:00:00.000Z,2002-08-16T12:00:00.000Z,2002-09-16T00:00:00.000Z,2002-10-16T12:00:00.000Z,2002-11-16T00:00:00.000Z,2002-12-16T12:00:00.000Z,2003-01-16T12:00:00.000Z,2003-02-15T00:00:00.000Z,2003-03-16T12:00:00.000Z,2003-04-16T00:00:00.000Z,2003-05-11T12:00:00.000Z,2003-07-16T12:00:00.000Z,2003-08-16T12:00:00.000Z,2003-09-16T00:00:00.000Z,2003-10-16T12:00:00.000Z,2003-11-16T00:00:00.000Z,2003-12-16T12:00:00.000Z,2004-01-07T12:00:00.000Z,2004-02-17T00:00:00.000Z,2004-03-16T12:00:00.000Z,2004-04-16T00:00:00.000Z,2004-05-16T12:00:00.000Z,2004-06-16T00:00:00.000Z,2004-07-16T12:00:00.000Z,2004-08-16T12:00:00.000Z,2004-09-16T00:00:00.000Z,2004-10-16T12:00:00.000Z,2004-11-16T00:00:00.000Z,2004-12-16T12:00:00.000Z,2005-01-16T12:00:00.000Z,2005-02-15T00:00:00.000Z,2005-03-16T12:00:00.000Z,2005-04-16T00:00:00.000Z,2005-05-16T12:00:00.000Z,2005-06-16T00:00:00.000Z,2005-07-16T12:00:00.000Z,2005-08-16T12:00:00.000Z,2005-09-16T00:00:00.000Z,2005-10-16T12:00:00.000Z,2005-11-16T00:00:00.000Z,2005-12-16T12:00:00.000Z,2006-01-16T12:00:00.000Z,2006-02-15T00:00:00.000Z,2006-03-16T12:00:00.000Z,2006-04-16T00:00:00.000Z,2006-05-16T12:00:00.000Z,2006-06-16T00:00:00.000Z,2006-07-16T12:00:00.000Z,2006-08-16T12:00:00.000Z,2006-09-16T00:00:00.000Z,2006-10-16T12:00:00.000Z,2006-11-16T00:00:00.000Z,2006-12-16T12:00:00.000Z,2007-01-16T12:00:00.000Z,2007-02-15T00:00:00.000Z,2007-03-16T12:00:00.000Z,2007-04-16T00:00:00.000Z,2007-05-16T12:00:00.000Z,2007-06-16T00:00:00.000Z,2007-07-16T12:00:00.000Z,2007-08-16T12:00:00.000Z,2007-09-16T00:00:00.000Z,2007-10-16T12:00:00.000Z,2007-11-16T00:00:00.000Z,2007-12-16T12:00:00.000Z,2008-01-16T12:00:00.000Z,2008-02-15T12:00:00.000Z,2008-03-16T12:00:00.000Z,2008-04-16T00:00:00.000Z,2008-05-16T12:00:00.000Z,2008-06-16T00:00:00.000Z,2008-07-16T12:00:00.000Z,2008-08-16T12:00:00.000Z,2008-09-16T00:00:00.000Z,2008-10-16T12:00:00.000Z,2008-11-16T00:00:00.000Z,2008-12-16T12:00:00.000Z,2009-01-16T12:00:00.000Z,2009-02-15T00:00:00.000Z,2009-03-16T12:00:00.000Z,2009-04-16T00:00:00.000Z,2009-05-16T12:00:00.000Z,2009-06-16T00:00:00.000Z,2009-07-16T12:00:00.000Z,2009-08-16T12:00:00.000Z,2009-09-16T00:00:00.000Z,2009-10-16T12:00:00.000Z,2009-11-16T00:00:00.000Z,2009-12-16T12:00:00.000Z,2010-01-16T12:00:00.000Z,2010-02-15T00:00:00.000Z,2010-03-16T12:00:00.000Z,2010-04-16T00:00:00.000Z,2010-05-16T12:00:00.000Z,2010-06-16T00:00:00.000Z,2010-07-16T12:00:00.000Z,2010-08-16T12:00:00.000Z,2010-09-16T00:00:00.000Z,2010-10-16T12:00:00.000Z,2010-11-16T00:00:00.000Z,2010-12-16T12:00:00.000Z,2011-02-18T12:00:00.000Z,2011-03-16T12:00:00.000Z,2011-04-16T00:00:00.000Z,2011-05-16T12:00:00.000Z,2011-07-19T12:00:00.000Z,2011-08-16T12:00:00.000Z,2011-09-16T00:00:00.000Z,2011-10-16T12:00:00.000Z,2011-11-01T12:00:00.000Z,2012-01-02T00:00:00.000Z,2012-01-16T12:00:00.000Z,2012-02-15T12:00:00.000Z,2012-03-16T12:00:00.000Z,2012-04-10T12:00:00.000Z,2012-06-16T00:00:00.000Z,2012-07-16T12:00:00.000Z,2012-08-16T12:00:00.000Z,2012-09-13T00:00:00.000Z,2012-11-20T00:00:00.000Z,2012-12-16T12:00:00.000Z,2013-01-16T12:00:00.000Z,2013-02-14T00:00:00.000Z,2013-04-21T12:00:00.000Z,2013-05-16T12:00:00.000Z,2013-06-16T00:00:00.000Z,2013-07-16T12:00:00.000Z,2013-10-16T12:00:00.000Z,2013-11-16T00:00:00.000Z,2013-12-16T12:00:00.000Z,2014-01-09T12:00:00.000Z,2014-03-17T12:00:00.000Z,2014-04-16T00:00:00.000Z,2014-05-16T12:00:00.000Z,2014-06-13T00:00:00.000Z,2014-08-16T12:00:00.000Z,2014-09-16T00:00:00.000Z,2014-10-16T12:00:00.000Z,2014-11-17T00:00:00.000Z,2015-01-22T12:00:00.000Z,2015-02-15T00:00:00.000Z,2015-03-16T12:00:00.000Z,2015-04-16T00:00:00.000Z,2015-04-27T00:00:00.000Z,2015-07-15T12:00:00.000Z,2015-08-16T12:00:00.000Z,2015-09-14T12:00:00.000Z,2015-12-23T00:00:00.000Z,2016-01-16T12:00:00.000Z,2016-02-14T00:00:00.000Z,2016-03-16T12:00:00.000Z,2016-05-20T12:00:00.000Z,2016-06-16T00:00:00.000Z,2016-07-15T12:00:00.000Z,2016-08-21T12:00:00.000Z,2018-06-16T00:00:00.000Z,2018-07-10T00:00:00.000Z,2018-10-31T12:00:00.000Z,2018-11-16T00:00:00.000Z,2018-12-16T12:00:00.000Z,2019-01-16T12:00:00.000Z,2019-02-14T00:00:00.000Z,2019-03-16T12:00:00.000Z,2019-04-16T00:00:00.000Z,2019-05-16T12:00:00.000Z,2019-06-16T00:00:00.000Z",             currentTime: Date.parse("2002-04-16T00:00:00.000Z"),
    },
    timeDimensionControl: true,
    timeDimensionControlOptions:{
                playerOptions:{
                        loop:true,
                        startover:true,
                },
                limitSliders:true,
                timeSliderDragUpdate: true,
                loopButton:true,
    },
    center: regioncenter,
});



//add the background imagery

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

var layer_control = L.control.layers(baseLayers).addTo(map);
baseLayers.ESRI_World_Imagery.addTo(map);

var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

var drawControlFull = new L.Control.Draw({
            edit: {
                featureGroup: drawnItems,
                edit: false
            },
            draw: {
                polyline: false,
                circlemarker: false,
                rectangle:false,
                circle:false,
		marker: true,
                polygon:false,
		
            }
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
//        $("#point-lat-lon").val(coords);
        var geom_data = $("#point-lat-lon").val(JSON.stringify(coords));
        get_ts();

});


var signal_process = $("#select_signal_process").find('option:selected').val();
var storage_type = $("#select_storage_type").find('option:selected').val();
//var testWMS = "http://127.0.0.1:7000/thredds/wms/testAll/grace/"+region+"/"+region+"_"+signal_process+"_"+storage_type+".nc";
var testWMS = thredds_wms+"wms/testAll/grace/"+region+"/"+region+"_"+signal_process+"_"+storage_type+".nc";
var colormin = $("#col_min").val();
var colormax = $("#col_max").val();
var opac = $("#opacity_val").val();

var testLayer = L.tileLayer.wms(testWMS, {
    layers:'lwe_thickness',
    format: 'image/png',
    transparent: true,
    opacity:0.7,
    style: 'boxfill/sst_36',
    colorscalerange:'-25,25',
    numcolorbands: 1500,
    attribution: '<a href="https://www.pik-potsdam.de/">PIK</a>'
});

var testTimeLayer = L.timeDimension.layer.wms.timeseries(testLayer, {
	updateTimeDimension: true,
    name: "Liquid Water Equivalent Thickness",
    units: "cm",
    enableNewMarkers: true
});

var testconstyle='contour/sst_36';
var testContourLayer = L.tileLayer.wms(testWMS, {
        //layers: 'grace',
        layers:'lwe_thickness',
        format: 'image/png',
        transparent: true,
        opacity:0.7,
        numcontours: 10,
        styles: testconstyle,
        colorscalerange:colormin+','+colormax,
        attribution: '<a href="https://www.pik-potsdam.de/">PIK</a>'
    });
var testTimeConLayer = L.timeDimension.layer.wms.timeseries(testContourLayer, {
	    //proxy: proxy,
	    updateTimeDimension: true,
    	name: "Liquid Water Equivalent Thickness",
    	units: "cm",
    	enableNewMarkers: true
    });

var testLegend = L.control({
    position: 'topright'
    });



//initialize a variable named zonalchart that tracks whether the zonal average timeseries has been added to the map
var zonalchart=0;


//The addGraph function displays the time series for the regional Average
function addGraph(){
    var signal_process = $("#select_signal_process").find('option:selected').val();
    var storage_type = $("#select_storage_type").find('option:selected').val();
    var signal_name = $("#select_signal_process").find('option:selected').text();
    var storage_name = $("#select_storage_type").find('option:selected').text();

    mychart=Highcharts.stockChart('regchart', {
            legend: {
                    enabled: true
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

            xAxis: {
                    plotLines: [{
                        color: 'red',
                        dashStyle: 'solid',
                        value: new Date(map.timeDimension.getCurrentTime()),
                        width: 2,
                        id: 'pbCurrentTime'
                    }],
		    title: {
			text: 'Date'
		    },
            },
            yAxis: {
                    title: {
                        text: "Storage Volume",
                    }

            },

            title: {
                text: region_name_upper+ ' Regional Average Water Storage Anomaly'
            },

            series: [],

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
    });//end of High Charts stuff

    testTimeLayer._timeDimension.on('timeload', (function() {
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
            }).bind(this));


//for loop to go through all 4 types of data,load the data, and display it on the highcharts time series
//for (var chartnumber=0;chartnumber<4;chartnumber++)
//{
    var color;
    var depletion_color
    var charttype;
    var seriesname;
    charttype="Total";
    color="#053372";
    depletion_color="#222222";

    seriesname= signal_name+' '+storage_name;

//    else if (chartnumber==1){
//        charttype="SW";
//        color="#2f7ed8";
//        seriesname="Surface Water Storage";
//    }
//    else if (chartnumber==2){
//        charttype="SM";
//        color="#2f7ed8";
//        seriesname="Soil Moisture Storage";
//    }
//    else if (chartnumber==3){
//        charttype="jpl_gw"
//        color="#2f7ed8";
//        seriesname="Groundwater Storage";
//    };

//    charturl="http://127.0.0.1:7000/thredds/dodsC/testAll/grace/" + region +"/"+region+"_"+signal_process+"_"+storage_type+"_ts.nc.ascii?";
    charturl=thredds_wms +"dodsC/testAll/grace/"+ region +"/"+region+"_"+signal_process+"_"+storage_type+"_ts.nc.ascii?";

    //get the data from the charturl for the time and lwe_thickness attributes
      var xhttp = new XMLHttpRequest();
      xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var mystring=this.responseText;
            var stringvariable=this.responseText;
            var variable="lwe_thickness"
            length=variable.length;
            var pos=stringvariable.lastIndexOf(variable);
            pos=pos+6+length;
            //the variable pos marks the starting position in stringvariable of the lwe_thickness data
            //the variable pos2 marks the ending position in stringvariable of the lwe_thickness data
            var pos2=stringvariable.lastIndexOf("time");
            pos2=pos2-1;
            //stringvariable is now a string of the lwe_thickness data
            stringvariable=stringvariable.slice(pos,(pos2));
            //variablearray takes the string and turns it into an array of lwe_thickness values
            var variablearray = JSON.parse("[" + stringvariable + "]");
          //pos2 is now the starting position of the time data
          pos2=pos2+11;
          //timestring is now a string of the time data
          var timestring=mystring.slice(pos2);
          //timearray takes the string and turns it into an array of time data values
          var timearray=JSON.parse("["+timestring+"]");

          //time conversion: convert time in timearray from days since 2002 to a date
          var oneday=24*60*60*1000;
          var UTCconversion=7*60*60*1000;
          var startdate= new Date(2002,0,01).getTime();
          var length = timearray.length;
          for (var i=0; i<length; i++){
            timearray[i]=startdate+timearray[i]*oneday-UTCconversion;
            timearray[i]=new Date(timearray[i]).getTime();
          }
          //end time conversion

                    var data = new Array(length);
                    var depletion_data = new Array(length);
                    var this_time = new Date();
                    var this_data = null;
                    var this_depletion_data = null;
                    var first_data = variablearray[0];
                    for (var i = 0; i < length; i++) {
                        this_time = timearray[i];
                        this_data = variablearray[i];
                        this_depletion_data = (variablearray[i] - first_data);
                        this_depletion_data = (this_depletion_data * 0.00000075) * region_area
                        if (isNaN(this_data))
                            this_data = null;
                        if (isNaN(this_depletion_data))
                            this_depletion_data = null;
                        data[i] = [this_time,this_data];
                        depletion_data[i] = [this_time,this_depletion_data];
                        }


    //add Series to the HighCharts chart
    myseries=
    {
        name: seriesname,
        data: data,
        type: 'area',
        color:color,
        tooltip: {
            valueDecimals: 2,
            valueSuffix: ' Liquid Water Eqv. Thickness (cm)',
            xDateFormat: '%A, %b %e, %Y',
            headerFormat: '<span style="font-size: 12px; font-weight:bold;">{point.key} (Click to visualize the map on this time)</span><br/>'
        }
    };
    mychart.addSeries(myseries);

    depletion_curve=
    {
        name: seriesname + " Depletion Curve",
        data: depletion_data,
        type: 'area',
        color:depletion_color,
        tooltip: {
            valueDecimals: 2,
            valueSuffix: ' Change in Volume since April 16, 2002 (Acre-ft)',
            xDateFormat: '%A, %b %e, %Y',
            headerFormat: '<span style="font-size: 12px; font-weight:bold;">{point.key} (Click to visualize the map on this time)</span><br/>'
        },
        visible:false
    };
    mychart.addSeries(depletion_curve);
           }//for the if statement
      }; // for the onreadystatechange
      xhttp.open("GET", charturl, false);
      xhttp.send();
//    }
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
        var region_dis_name = ($("#region-select option:selected").text());


        var geom_data = $("#point-lat-lon").val();
        geom_data = geom_data.replace("[","");
        geom_data = geom_data.replace("]","");

        var $loading = $('#view-file-loading');
        $loading.removeClass('hidden');
        $("#plotter").addClass('hidden');
        var xhr = ajax_update_database("get-plot-reg-pt",{"region_dis_name":region_dis_name, "storage_type":storage_type,"signal_process":signal_process,"storage_name":storage_name, "signal_name":signal_name, "geom_data":geom_data});
        xhr.done(function(result) {
            if("success" in result) {

                $('.error').html('');
                myotherchart=Highcharts.stockChart('plotter', {
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
//			color: '#2f7ed8',
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

                map.timeDimension.on('timeload', (function() {
                    if (!myotherchart){
                    return;
                    }
                    myotherchart.xAxis[0].removePlotBand("pbCurrentTime");
                    myotherchart.xAxis[0].addPlotLine({
                        color: 'red',
                        dashStyle: 'solid',
                        value: new Date(map.timeDimension.getCurrentTime()),
                        width: 2,
                        id: 'pbCurrentTime'
                    });
                }));

                $loading.addClass('hidden');
                $("#plotter").removeClass('hidden');
            }
            else {
                $(".error").append('<h3>Error Processing Request.</h3>');
                $("#plotter").removeClass('hidden');
            }
        });

    };

function updateWMS(){
    map.removeLayer(Stamen_TonerHybrid);
    map.removeLayer(testTimeLayer);
    map.removeLayer(testTimeConLayer);
    layer_control.removeLayer(Stamen_TonerHybrid);
    layer_control.removeLayer(testTimeLayer);
    layer_control.removeLayer(testTimeConLayer);
    var type=$("#select_legend").find('option:selected').val();
    var signal_process = $("#select_signal_process").find('option:selected').val();
    var storage_type = $("#select_storage_type").find('option:selected').val();
    var storage_name = $("#select_storage_type").find('option:selected').text();
//    var testWMS = "http://127.0.0.1:7000/thredds/wms/testAll/grace/"+region+"/"+region+"_"+signal_process+"_"+storage_type+".nc";
    var testWMS = thredds_wms+"wms/testAll/grace/"+region+"/"+region+"_"+signal_process+"_"+storage_type+".nc";

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

    testconstyle='contour/'+type;
    testContourLayer = L.tileLayer.wms(testWMS, {
        layers:'lwe_thickness',
        format: 'image/png',
        transparent: true,
        opacity:0.7,
        numcontours: 20,
        crossOrigin: true,
        crs: L.CRS.EPSG4326,
        styles: testconstyle,
        colorscalerange:colormin+','+colormax,
        attribution: '<a href="https://www.pik-potsdam.de/">PIK</a>'
    });
    testTimeConLayer = L.timeDimension.layer.wms.timeseries(testContourLayer, {
	    updateTimeDimension: true,
    	name: "Liquid Water Equivalent Thickness",
    	units: "cm",
    	enableNewMarkers: true
    });
    testTimeLayer = L.timeDimension.layer.wms.timeseries(testLayer, {
	    updateTimeDimension: true,
    	name: "Liquid Water Equivalent Thickness",
    	units: "cm",
    	enableNewMarkers: true
    });

    layer_control.addOverlay(testTimeLayer, storage_name);
    layer_control.addOverlay(testTimeConLayer, 'Contours');


    testTimeLayer.addTo(map);
    testTimeConLayer.addTo(map);
    //add the legend to the map based on the type variable
    testLegend.onAdd= function(map) {
        var src=testWMS+"?REQUEST=GetLegendGraphic&LAYER=lwe_thickness&PALETTE="+type+"&COLORSCALERANGE="+colormin+","+colormax;
        var div = L.DomUtil.create('div', 'info legend');
        div.innerHTML +=
            '<img src="' + src + '" alt="legend">';
        return div;
    };
    testLegend.addTo(map);
    map.timeDimension.setCurrentTime(date_value);

    layer_control.addOverlay(Stamen_TonerHybrid, 'Borders and Labels');
//    Stamen_TonerHybrid.addTo(map);

};

function getInstructions() {
    var x = document.getElementById("ts-instructions");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
};



$(function(){
    init_vars();
    updateWMS();

    $("#select_signal_process").change(function(){
        updateWMS();
        addGraph();
        get_ts();
    }).change();

    $("#select_storage_type").change(function(){
        updateWMS();
        addGraph();
        get_ts();
    }).change;

    $("#select_layer").change(function(){
        updateWMS();
    }).change();

    $("#select_legend").change(function(){
        updateWMS();
    }).change();
});
