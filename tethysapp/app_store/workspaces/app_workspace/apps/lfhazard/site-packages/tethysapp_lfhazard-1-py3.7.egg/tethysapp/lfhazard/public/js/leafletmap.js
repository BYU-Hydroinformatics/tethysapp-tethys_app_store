let csrftoken = Cookies.get('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
function getStateBoundaries() {
    $.ajax({
        type: 'GET',
        async: true,
        data: {state: $("#select_state").val()},
        url: URL_getGeoJson,
        success: function (json) {
            state.clearLayers();
            state.addData(json);
            map.flyToBounds(state.getBounds());
        },
    })
}
const map = L.map("map", {center: [40 , -100], zoom: 4 , zoomControl: true, preferCanvas: false});
const osm = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
let state = L.geoJSON(false, {fillOpacity: 0}).addTo(map);
getStateBoundaries()

let latlon = L.control({position: 'bottomleft'});
latlon.onAdd = function () {
    let div = L.DomUtil.create('div', 'well well-sm');
    div.innerHTML = '<div id="mouse-position" style="text-align: center"></div>';
    return div;
};
latlon.addTo(map);
map.on("mousemove", function (event) {
    $("#mouse-position").html('Lat: ' + event.latlng.lat.toFixed(5) + ', Lon: ' + event.latlng.lng.toFixed(5));
});

$("#select_state").change(function() {getStateBoundaries()});
$("#select_model").change(function() {
    let sy = $("#select_year");
    let ss = $("#select_state");
    if (this.value === 'cpt') {
        $("#spt-table").hide()
        $("#cpt-table").show()
        sy.empty();
        ss.empty();
        sy.append('<option value="2014" selected>2014</option>');
        ss.append('<option value="Connecticut">Connecticut</option>');
        ss.append('<option value="Oregon">Oregon</option>');
        ss.append('<option value="South_Carolina">South Carolina</option>');
        ss.append('<option value="Utah" selected>Utah</option>');
    } else {
        $("#spt-table").show()
        $("#cpt-table").hide()
        sy.empty();
        ss.empty();
        sy.append('<option value="2008">2008</option>');
        sy.append('<option value="2014">2014</option>');
        ss.append('<option value="Alaska">Alaska</option>');
        ss.append('<option value="Connecticut">Connecticut</option>');
        ss.append('<option value="Idaho">Idaho</option>');
        ss.append('<option value="Montana">Montana</option>');
        ss.append('<option value="Oregon">Oregon</option>');
        ss.append('<option value="South_Carolina">South Carolina</option>');
        ss.append('<option value="Utah" selected>Utah</option>');
    }
    getStateBoundaries();
})
function submitButton() {
    query_csv(parseFloat($("#lon-input").val()), parseFloat($("#lat-input").val()), $("#select_year").val(), $("#select_state").val(), $("#select_return_period").val(), $("#select_model").val())
}
function query_csv(lon, lat, year, state, returnPeriod, model) {
    let data = {lon: lon, lat: lat, year: year, state: state, returnPeriod: returnPeriod, model: model};

    $.ajax({
        type: 'GET',
        url: URL_querycsv,
        dataType: 'json',
        data: data,
        success: function (results) {
            let point_value = results.point_value;
            if (model === 'spt'){
                addSptTableRow(lon.toFixed(4), lat.toFixed(4), point_value[0], point_value[1], point_value[2], point_value[3], point_value[4], point_value[5], point_value[6])
            } else {
                addCptTableRow(lon.toFixed(4), lat.toFixed(4), point_value[0], point_value[1], point_value[2], point_value[3], point_value[4], point_value[5], point_value[6])
            }
        },
    });
}
map.on('click', (function(event) {
    query_csv(event.latlng['lng'], event.latlng['lat'], $("#select_year").val(), $("#select_state").val(), $("#select_return_period").val(), $("#select_model").val())
}))

let spt_row_counter = 0
let cpt_row_counter = 0
function addSptTableRow(lon, lat, logDvalue, Nvalue, CSRvalue, Cetinvalue, InYvalue, RnSvalue, BnTvalue) {
    spt_row_counter = spt_row_counter + 1;
    let table = document.getElementById("spt-table");
    let row = table.insertRow(1);
    let cell0 = row.insertCell(0);
    let cell1 = row.insertCell(1);
    let cell2 = row.insertCell(2);
    let cell3 = row.insertCell(3);
    let cell4 = row.insertCell(4);
    let cell5 = row.insertCell(5);
    let cell6 = row.insertCell(6);
    let cell7 = row.insertCell(7);
    let cell8 = row.insertCell(8);
    let cell9 = row.insertCell(9);
    let cell10 = row.insertCell(10);
    let cell11 = row.insertCell(11);
    cell0.innerHTML = $("#select_year").val();
    cell1.innerHTML = $("#select_return_period").val();
    cell2.innerHTML = lon;
    cell3.innerHTML = lat;
    cell4.innerHTML = (parseFloat(CSRvalue).toFixed(2));
    cell5.innerHTML = (parseFloat(Nvalue).toFixed(2));
    cell6.innerHTML = (parseFloat(Cetinvalue).toFixed(2));
    cell7.innerHTML = (parseFloat(InYvalue).toFixed(2));
    cell8.innerHTML = (parseFloat(logDvalue).toFixed(2));
    cell9.innerHTML = (parseFloat(RnSvalue).toFixed(2));
    cell10.innerHTML = (parseFloat(BnTvalue).toFixed(2));
    cell11.innerHTML = '<button onclick="deleteTableRow(this)">Delete Row</button>';
}
function addCptTableRow(lon, lat, csr, qreq, ev_ku_ref, ev_bi_ref, gv_ku_max, gv_bi_max) {
    cpt_row_counter = cpt_row_counter + 1;
    let table = document.getElementById("cpt-table");
    let row = table.insertRow(1);
    let cell0 = row.insertCell(0);
    let cell1 = row.insertCell(1);
    let cell2 = row.insertCell(2);
    let cell3 = row.insertCell(3);
    let cell4 = row.insertCell(4);
    let cell5 = row.insertCell(5);
    let cell6 = row.insertCell(6);
    let cell7 = row.insertCell(7);
    let cell8 = row.insertCell(8);
    let cell9 = row.insertCell(9);
    let cell10 = row.insertCell(10);
    cell0.innerHTML = $("#select_year").val();
    cell1.innerHTML = $("#select_return_period").val();
    cell2.innerHTML = lon;
    cell3.innerHTML = lat;
    cell4.innerHTML = (parseFloat(csr).toFixed(3));
    cell5.innerHTML = (parseFloat(qreq).toFixed(3));
    cell6.innerHTML = (parseFloat(ev_ku_ref).toFixed(3));
    cell7.innerHTML = (parseFloat(ev_bi_ref).toFixed(3));
    cell8.innerHTML = (parseFloat(gv_ku_max).toFixed(3));
    cell9.innerHTML = (parseFloat(gv_bi_max).toFixed(3));

    



    cell10.innerHTML = '<button onclick="deleteTableRow(this)">Delete Row</button>';
}

function deleteTableRow(r) {
    if ($("#select_model").val() === 'spt') {
        document.getElementById("spt-table").deleteRow(r.parentNode.parentNode.rowIndex);
        spt_row_counter = spt_row_counter - 1;
    } else {
        document.getElementById("cpt-table").deleteRow(r.parentNode.parentNode.rowIndex);
        cpt_row_counter = cpt_row_counter - 1;
    }
}

function downloadTableData() {
    let tabledata = [];
    let rows;
    if ($("#select_model").val() === 'spt') {
        rows = document.getElementById("spt-table").querySelectorAll("tr");
    } else {
        rows = document.getElementById("cpt-table").querySelectorAll("tr");
    }

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
