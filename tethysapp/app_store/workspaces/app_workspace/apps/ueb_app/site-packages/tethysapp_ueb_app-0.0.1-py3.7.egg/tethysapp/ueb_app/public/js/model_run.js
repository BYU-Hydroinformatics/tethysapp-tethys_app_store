var allRectangles = [];
var allMarkers = [];
var map; // global variable
var drawingManager;

$(document).ready(function() {

    // Hide the metadata section and model run btn when user changes the selection
    $('#resource_list').change(function(){
        $('#submit-model-run-btn').hide();
        $('#load-metadata-response').hide();
        $('#load-metadata-fail').hide();
        $('#submit-response').hide();
        $('#user-form').submit();
    })

    // ajax call function to submit the form for metadata loading or run model service
    var user_form= $('#user-form');

    user_form.submit(function(){

        $('#submit-model-run-btn').hide();
        $(this).attr('action','model_run_submit_execution/');


        $.ajax({
            type: user_form.attr('method'),
            url: user_form.attr('action'),
            data: user_form.serialize(),

            success: function(result) {
                console.log(result);
                json_response = JSON.parse(result);
                console.log(json_response);
//                    alert('happy');
                $('#submit-response').show()
                if (json_response.status == 'Error'){
                    document.getElementById("submit-response").style.backgroundColor = '#ffebe6';
                }
                else {
                    document.getElementById("submit-response").style.backgroundColor = '#eafaea';
                }

                $('#response-status').text(json_response.status)
                $('#response-result').text(json_response.result);
            },

            error: function() {
//                    alert('sad');
                $('#submit-response').show();
                document.getElementById("submit-response").style.backgroundColor = '#ffebe6';
                $('#response-status').text('Error');
                $('#response-result').text('Failed to run the web service. Please try it again.');
            },

            complete: function(){
//                    alert('complete');
//                    $('#wait').modal('hide');
            }
        });
        return false;

    }); // end of user submit function

});  // end of the main function

function initMap() {
var mapDiv = document.getElementById('map');
map = new google.maps.Map(mapDiv, {
    center: {lat: 37.09024, lng: -95.712891},
    zoom: 4,
});

map.setMapTypeId('terrain');

// draw the bounding box and outlet point based on the metadata
if ($('#north-lat').text() != 'None' && $('#south-lat').text() != 'None' &&
    $('#east-lon').text() != 'None' && $('#west-lon').text() != 'None'){
    var bounds = {
            north: parseFloat($('#north-lat').text()),
            south: parseFloat($('#south-lat').text()),
            east: parseFloat($('#east-lon').text()),
            west: parseFloat($('#west-lon').text())
        };
    drawRectangleOnTextChange(bounds);
}

if ($('#outlet-x').length == 1 && $('#outlet-y').length == 1){
    var myLatLng = {lat: parseFloat($("#outlet-y").text()), lng: parseFloat($("#outlet-x").text())};
    drawMarkerOnTextChange(myLatLng);
}

} // end of initmap function


function drawMarkerOnTextChange(myLatLng){

    // Delete previous drawings
    for (var i = 0; i < allMarkers.length; i++) {
            allMarkers[i].setMap(null);
     };

    // Bounds validation
    var badInput = false;

    if (myLatLng.lat > 90 || myLatLng.lat < -90) {
        $("#outlet_y").val('');
        badInput = true;
    }

    if (myLatLng.lng > 180 || myLatLng.lng < -180) {
        $("#outlet_x").val('');
        badInput = true;
    }

    if (badInput || isNaN(myLatLng.lat) || isNaN(myLatLng.lng)) {
        return;
    }

    // Define the marker
    var marker = new google.maps.Marker({
        position: myLatLng,
        map: map
    });
    map.setCenter(marker.getPosition());

    allMarkers.push(marker);

} // end of drawMarkerOnTextChange


function drawRectangleOnTextChange(bounds){
    // Delete previous drawings
    for (var i = 0; i < allRectangles.length; i++) {
            allRectangles[i].setMap(null);
     };

    // Bounds validation
    var badInput = false;

    // North
    if (bounds.north > 90 || bounds.north < -90) {
        badInput = true;
    }

    // East
    if (bounds.east > 180 || bounds.east < -180) {
        badInput = true;
    }

    // South
    if (bounds.south < -90 || bounds.south > 90) {
        badInput = true;
    }

    // West
    if (bounds.west < -180 || bounds.west > 180) {
        badInput = true;
    }

    if (badInput || isNaN(bounds.north) || isNaN(bounds.south) || isNaN(bounds.east) || isNaN(bounds.west)) {
        return;
    }

    // Define the rectangle and set its editable property to true.
    var rectangle = new google.maps.Rectangle({
        bounds: bounds,
        editable: false,
        draggable: false,
    });
    rectangle.setMap(map);

    var southWest = new google.maps.LatLng(bounds.south,bounds.west);
    var northEast = new google.maps.LatLng(bounds.north,bounds.east);
    var bounds = new google.maps.LatLngBounds(southWest,northEast);
    map.fitBounds(bounds);

    allRectangles.push(rectangle);
}


