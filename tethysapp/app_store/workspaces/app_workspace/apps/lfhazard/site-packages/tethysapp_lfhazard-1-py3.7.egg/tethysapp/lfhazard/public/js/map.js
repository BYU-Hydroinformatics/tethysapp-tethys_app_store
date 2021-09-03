/**
 * Elements that make up the popup.
 */
var LS;
var LT_Nreq;
var LT_CSR;
var SSD_Cetin;
var SSD_IY;
var SSD_RandS;
var SSD_BandT;
var map;
var overlay;
var allow_popup;
var select;
var container = document.getElementById('popup');
var content = document.getElementById('popup-content');
var closer = document.getElementById('popup-closer');
var myState;
var states;
var state_extent = {
    "Utah": [-12696318.964051722, 4438824.352878017, -12138396.254597204, 5161215.111001225],
    "Alaska": [-21368124.13117759, 6457400.14953169, -14010601.536559664, 11310234.20130096],
    "Idaho": [-13051435.550005142, 5159191.507771076, -12361314.3189422, 6275056.926533954],
    "Montana": [-12918628.795493595, 5521047.083236762, -11581585.046900151, 6275098.365819148],
    "Oregon": [-13865115.895666974, 5159751.14213368, -12964659.45666714, 5823885.541506248],
    "South_Carolina": [-9278840.450458946, 3767854.0832061665, -8743154.087620595, 4193193.0101464884],
    "Connecticut": [-8207338.524260876, 5010155.8629135955, -7991291.70537736, 5168561.425406045]
};
var CSRvalue;
var Nvalue;
var LogDvalue;
var RnSvalue;
var BnTvalue;
var Cetinvalue;
var InYvalue;
var returnPeriod_global;
var state_global;
var modelYear_global;
var point_value;
var row_counter = 0;

function update() {
    var returnPeriod = $('#select_return_period').val();
    var state = $('#select_state').val();
    var modelYear = document.getElementById('select_year').value;
    returnPeriod_global = returnPeriod;
    state_global = state;
    modelYear_global = modelYear;

    var format = 'image/png';

    LS = new ol.layer.Tile({
        visible: false,
        source: new ol.source.TileWMS({
            url: 'http://tethys.byu.edu:8181/geoserver/lfhazard/wms',
            params: {
                'FORMAT': format,
                'VERSION': '1.1.1',
                tiled: true,
                LAYERS: 'lfhazard:Kriging_LS-' + returnPeriod + '_' + state + modelYear,
                STYLES: '',
            }
        })
    });

    LT_Nreq = new ol.layer.Tile({
        visible: false,
        source: new ol.source.TileWMS({
            url: 'http://tethys.byu.edu:8181/geoserver/lfhazard/wms',
            params: {
                'FORMAT': format,
                'VERSION': '1.1.1',
                tiled: true,
                LAYERS: 'lfhazard:Kriging_LT-' + returnPeriod + '_' + state + '_PB_Nreq_Cetin' + modelYear,
                STYLES: '',
            }
        })
    });

    LT_CSR = new ol.layer.Tile({
        visible: false,
        source: new ol.source.TileWMS({
            url: 'http://tethys.byu.edu:8181/geoserver/lfhazard/wms',
            params: {
                'FORMAT': format,
                'VERSION': '1.1.1',
                tiled: true,
                LAYERS: 'lfhazard:Kriging_LT-' + returnPeriod + '_' + state + '_PB_CSR_' + modelYear,
                STYLES: '',
            }
        })
    });

    SSD_Cetin = new ol.layer.Tile({
        visible: false,
        source: new ol.source.TileWMS({
            url: 'http://tethys.byu.edu:8181/geoserver/lfhazard/wms',
            params: {
                'FORMAT': format,
                'VERSION': '1.1.1',
                tiled: true,
                LAYERS: 'lfhazard:Kriging_SSD-' + returnPeriod + '_' + state + '_Cetin_percent' + modelYear,
                STYLES: '',
            }
        })
    });

    SSD_IY = new ol.layer.Tile({
        visible: false,
        source: new ol.source.TileWMS({
            url: 'http://tethys.byu.edu:8181/geoserver/lfhazard/wms',
            params: {
                'FORMAT': format,
                'VERSION': '1.1.1',
                tiled: true,
                LAYERS: 'lfhazard:Kriging_SSD-' + returnPeriod + '_' + state + '_IandY_percent' + modelYear,
                STYLES: '',
            }
        })
    });

    SSD_RandS = new ol.layer.Tile({
        visible: false,
        source: new ol.source.TileWMS({
            url: 'http://tethys.byu.edu:8181/geoserver/lfhazard/wms',
            params: {
                'FORMAT': format,
                'VERSION': '1.1.1',
                tiled: true,
                LAYERS: 'lfhazard:Kriging_SSD-' + returnPeriod + '_' + state + '_PB_Seismic_Slope_Disp_RandS' + modelYear,
                STYLES: '',
            }
        })
    });

    SSD_BandT = new ol.layer.Tile({
        visible: false,
        source: new ol.source.TileWMS({
            url: 'http://tethys.byu.edu:8181/geoserver/lfhazard/wms',
            params: {
                'FORMAT': format,
                'VERSION': '1.1.1',
                tiled: true,
                LAYERS: 'Kriging_SSD-' + returnPeriod + '_' + state + '_PB_Seismic_Slope_Disp_BandT' + modelYear,
                STYLES: '',
            }
        })
    });
}

// ************************************
// This function is the button 
// ************************************
function submitButton() {
    var lat = document.getElementById('lat-input').value;
    var lon = document.getElementById('lon-input').value;

    var coordinate = [Number(lat), Number(lon)];
    // console.log("Submit click 1: " + coordinate);
    // console.log("Type of coordinate: " + typeof coordiante);

    var newcoor = ol.proj.transform([Number(lat), Number(lon)], 'EPSG:4326', 'EPSG:3857');
    // console.log("Submit click 2: " + newcoor); //This changes lat and long into EPSG:3857

    if (checkstate(newcoor, states) == true) {
        getPopup(newcoor);
    } else {
        alert("Please submit coordinates within selected State boundaries");
    }

}

// ************************************
// This is the new popup builder
// ************************************
function newgetPopup(coordinate, LogDvalue, Nvalue, CSRvalue, RnSvalue, BnTvalue, Cetinvalue, InYvalue, state) {
    var view = map.getView();
    var viewResolution = view.getResolution();

    var dec = ol.proj.transform(coordinate, 'EPSG:3857', 'EPSG:4326');
    var declon = parseFloat(dec[0]).toFixed(5);
    var declat = parseFloat(dec[1]).toFixed(5);

    content.innerHTML = '<p><b>Location:</b><br>' + declon + ', ' + declat + '</p>';
    content.innerHTML += '<p><i><b>CSR(%)<sup>ref</sup></b>:  ' + (parseFloat(CSRvalue).toFixed(2)) + '</i></p>';
    content.innerHTML += '<p><i><b>N<sub>req</sub><sup>ref</sup></b>:  ' + (parseFloat(Nvalue).toFixed(2)) + '</i></p>';
    content.innerHTML += '<p><i><b>&epsilon;<sub>v,Cetin</sub>(%)<sup>ref</sup></b>:  ' + (parseFloat(RnSvalue).toFixed(2)) + '</i></p>';
    content.innerHTML += '<p><i><b>&epsilon;<sub>v,I&Y%</sub>(%)<sup>ref</sup></b>:  ' + (parseFloat(BnTvalue).toFixed(2)) + '</i></p>';
    if (state == 'Alaska') {
        content.innerHTML += '<p><i><b>Log D<sub>h</sub><sup>ref</sup></b> (lateral spread is based on USGS 2002 data):  ' + (parseFloat(LogDvalue).toFixed(4)) + '</i></p>';
    } else {
        content.innerHTML += '<p><i><b>Log D<sub>h</sub><sup>ref</sup></b>:  ' + (parseFloat(LogDvalue).toFixed(4)) + '</i></p>';
    }
    content.innerHTML += '<p><i><b>D<sub>R&S</sub><sup>ref</sup></b>:  ' + (parseFloat(Cetinvalue).toFixed(2)) + '</i></p>';
    content.innerHTML += '<p><i><b>D<sub>B&T</sub><sup>ref</sup></b>:  ' + (parseFloat(InYvalue).toFixed(2)) + '</i></p>';
    content.innerHTML += '<button id="Add_values" onclick="Add_values(' + declon + ',' + declat + ',' + LogDvalue + ',' + Nvalue + ',' + CSRvalue + ',' + Cetinvalue + ',' + InYvalue + ',' + RnSvalue + ',' + BnTvalue + ')">Add</button>';

    overlay.setPosition(coordinate);
}

function Add_values(lon, lat, logDvalue, Nvalue, CSRvalue, Cetinvalue, InYvalue, RnSvalue, BnTvalue) {
    var table = document.getElementById("myTable");
    row_counter = row_counter + 1;
    // console.log(row_counter);
    var row = table.insertRow(1);
    var cell0 = row.insertCell(0);
    var cell1 = row.insertCell(1);
    var cell2 = row.insertCell(2);
    var cell3 = row.insertCell(3);
    var cell4 = row.insertCell(4);
    var cell5 = row.insertCell(5);
    var cell6 = row.insertCell(6);
    var cell7 = row.insertCell(7);
    var cell8 = row.insertCell(8);
    var cell9 = row.insertCell(9);
    var cell10 = row.insertCell(10);
    var cell11 = row.insertCell(11);
    cell0.innerHTML = modelYear_global;
    cell1.innerHTML = returnPeriod_global;
    cell2.innerHTML = lon;
    cell3.innerHTML = lat;
    cell4.innerHTML = (parseFloat(CSRvalue).toFixed(2));
    cell5.innerHTML = (parseFloat(Nvalue).toFixed(2));
    cell6.innerHTML = (parseFloat(RnSvalue).toFixed(2));
    cell7.innerHTML = (parseFloat(BnTvalue).toFixed(2));
    cell8.innerHTML = (parseFloat(logDvalue).toFixed(4));
    cell9.innerHTML = (parseFloat(Cetinvalue).toFixed(2));
    cell10.innerHTML = (parseFloat(InYvalue).toFixed(2));
    cell11.innerHTML = '<button id="Delete_row" onclick="Delete_row(this)">Delete Row</button>';
}

function Delete_row(r) {
    var i = r.parentNode.parentNode.rowIndex;
    document.getElementById("myTable").deleteRow(i);
    row_counter = row_counter - 1;
}

function Download_data() {
    let tabledata = [];
    var rows = document.querySelectorAll("table tr");

    for (var i = 0; i < rows.length; i++) {
        var row = [], cols = rows[i].querySelectorAll("td, th");

        for (var j = 0; j < cols.length; j++) {
            if (cols[j].innerText === 'Delete Row' || cols[j].innerText === 'Download Data') {
                continue
            }
            row.push(cols[j].innerText);
        }

        tabledata.push(row.join(","));
    }
    let csv = "data:text/csv;charset=utf-8," + tabledata.join("\n");
    let link = document.createElement('a');
    link.setAttribute('href', encodeURI(csv));
    link.setAttribute('target', '_blank');
    link.setAttribute('download',  'liquifaction_parameters.csv');
    document.body.appendChild(link);
    link.click();
    $("#a").remove();
}

// ************************************
// This makes the pup with all the information
// ************************************
function getPopup(coordinate) {
    update();

    // var view = map.getView();
    // var viewResolution = view.getResolution();

    // // var hdms = ol.coordinate.toStringHDMS(ol.proj.transform(
    // //   coordinate, 'EPSG:3857', 'EPSG:4326'));

    var dec = ol.proj.transform(coordinate, 'EPSG:3857', 'EPSG:4326');
    var declon = parseFloat(dec[0]).toFixed(5);
    var declat = parseFloat(dec[1]).toFixed(5);
    // console.log ("This are the coordinates: ");
    // console.log (declon);
    // console.log (declat);
    // console.log ("This are the model year: "+ modelYear_global);
    // console.log ("This are the state: "+ state_global);
    // console.log ("This are the return period: "+ returnPeriod_global);
    query_csv(declon, declat, modelYear_global, state_global, returnPeriod_global);
}

// Function query_csv sends parameters to the controllers.py
function query_csv(lon, lat, year, state, returnPeriod) {
    // console.log ("query_csv works")
    var csrf_token = getCookie('csrftoken');

    var data = {lon: lon, lat: lat, year: year, state: state, returnPeriod: returnPeriod};
    $.ajax({
        type: 'POST',
        url: '/apps/lfhazard/query-csv/',
        headers: {'X-CSRFToken': csrf_token},
        dataType: 'json',
        data: JSON.stringify(data),
        success: function (data) {
            if (data.status == "success") {
                // console.log ("got data")
                point_value = data.point_value;
                // console.log(point_value);
                // console.log(point_value[0]);
                // console.log("These are the lon and lat: "+ lon + " & "+ lat);
                var newcoor = ol.proj.transform([Number(lon), Number(lat)], 'EPSG:4326', 'EPSG:3857');
                // console.log("These are the changed coordinates : " + newcoor); //This changes lat and long into EPSG:3857
                // console.log("Connected to map.js")
                //newgetPopup(newcoor, LogDvalue, Nvalue, CSR value, Cetin percent, I&Y, R&S, B&T)
                newgetPopup(newcoor, point_value[0], point_value[1], point_value[2], point_value[3], point_value[4], point_value[5], point_value[6], state);

            } else {
                // alert("value error");

            }

        },
        error: function (jqXHR, textStatus, errorThrown) {

            // alert("ajax error");

        }
    });
}

function checkstate(pnt, state_layer) {
    // checkstate takes the coordinates and state layer and checks
    // where the
    var check = state_layer.getSource().getFeaturesAtCoordinate(pnt);
    if (check.length === 0) {
        return false;
    } else {
        return true;
    }
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


$(document).ready(function () {
    var returnPeriod = $('#select_return_period').val();
    var state = $('#select_state').val();
    var modelYear = document.getElementById('select_year').value;
    var onclickcoor;

    /**
     * Create an overlay to anchor the popup to the map.
     */
    overlay = new ol.Overlay(/** @type {olx.OverlayOptions} */ ({
        element: container,
        autoPan: true,
        autoPanAnimation: {
            duration: 250
        }
    }));


    /**
     * Add a click handler to hide the popup.
     * @return {boolean} Don't follow the href.
     */
    closer.onclick = function () {
        overlay.setPosition(undefined);
        closer.blur();
        return false;
    };


    /**
     * Create the map.
     */

    var basemap = new ol.layer.Tile({
        source: new ol.source.OSM()
    });

    states = new ol.layer.Vector({
        source: new ol.source.Vector({
            url: '/static/lfhazard/kml/' + state + '.kml',
            format: new ol.format.KML()
        })
    });

    var bOptions = {
        "Utah": [2008, 2014],
        "Alaska": [2007],
        "Idaho": [2008, 2014],
        "Montana": [2008, 2014],
        "South_Carolina": [2008, 2014],
        "Connecticut": [2008, 2014],
        "Oregon": [2014]
    };

    var select_state = document.getElementById('select_state');
    var select_year = document.getElementById('select_year');

    //on change is a good event for this because you are guarenteed the value is different
    $('#select_state').change(function () {
        map.removeLayer(map.getLayers().item(1)); //This is what removes the state layer
        var state = $('#select_state').val();
        console.log("state selected: " + state);
        states = new ol.layer.Vector({
            source: new ol.source.Vector({
                url: '/static/lfhazard/kml/' + state + '.kml',
                format: new ol.format.KML()
            })
        });
        map.addLayer(states);
        map.updateSize();
        update();
        myState = map.getLayers().item(1).getSource().getExtent();
        var ex = states.getSource().getExtent()
        map.getView().fit(state_extent[state], map.getSize());
        //This part changes the Year option
        //clear out select_year
        select_year.length = 0;
        //get the selected value from A
        var _val = this.options[this.selectedIndex].value;
        //loop through bOption at the selected value
        for (var i in bOptions[_val]) {
            //create option tag
            var op = document.createElement('option');
            //set its value
            op.value = bOptions[_val][i];
            //set the display label
            op.text = bOptions[_val][i];
            //append it to select_year
            select_year.appendChild(op);
        }
    });

    $('#select_year').change(function () {
        select_year = document.getElementById('select_year');
        getPopup(onclickcoor);
    });

    $('#select_return_period').change(function () {
        // console.log('Return Period changed');
        getPopup(onclickcoor);
    });

    map = new ol.Map({
        layers: [basemap, states],
        overlays: [overlay],
        target: 'map',
        view: new ol.View({
            center: [-11000000, 4600000], //This sets the center of map to center of states
            zoom: 4
        })
    });

    // here is where it checks if its in the state
    select = new ol.interaction.Select({
        multi: true // multi is used in this example if hitTolerance > 0
    });

    map.on('singleclick', function (evt) {
        if (returnPeriod != "" && state != "" && modelYear != "") {
            if (checkstate(evt.coordinate, states)) {
                getPopup(evt.coordinate);
            } else {
                alert("Please click within selected State boundaries");
            }
        } else {
            alert("No parameters provided");
        }
    });

});