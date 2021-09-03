/*****************************************************************************
 * FILE:    Add New Layer
 * DATE:    22 AUGUST 2019
 * AUTHOR: Sarva Pulla
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var LIBRARY_OBJECT = (function() {
    // Wrap the library in a package function
    "use strict"; // And enable strict mode for this library

    /************************************************************************
     *                      MODULE LEVEL / GLOBAL VARIABLES
     *************************************************************************/
    var $geoserverUrl,
        map,
        $modalUpdate,
        public_interface,				// Object returned by the module
        aquiferGroup;

    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/

    var delete_aquifer,
        update_form,
        init_all,
        init_events,
        init_jquery_vars,
        init_dropdown,
        init_map,
        init_table,
        reset_form,
        submit_update_aquifer,
        view_aquifer;



    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/
    //Reset the form when the request is made succesfully
    reset_form = function(result){
        if("success" in result){
            $("#aquifer-text-input").val('');
            $("#shp-upload-input").val('');
            addSuccessMessage('Aquifer Update Complete!');
        }
    };

    init_jquery_vars = function(){
        $modalUpdate = $("#update-modal");
        $geoserverUrl = $("#geoserver-text-input").val();
    };

    init_map = function(){
        map = L.map('map',{
            zoom: 3,
            center: [0, 0],
            // crs: L.CRS.EPSG3857
        });

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            // maxZoom: 10,
            attribution:
                '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        aquiferGroup = L.layerGroup().addTo(map);
    };


    $('#update-modal').on('hide.bs.modal', function () {
        reset_form({"reset": "reset"});
    });

    var viewIcon = function(cell, formatterParams){ //plain text value
        return "<span class='glyphicon glyphicon-sunglasses view-aquifer-tabulator'></span>";
    };

    var deleteIcon = function(cell, formatterParams){ //plain text value
        return "<span class='glyphicon glyphicon-remove'></span>";
    };

    var updateIcon = function(cell, formatterParams){ //plain text value
        return "<span class='glyphicon glyphicon-floppy-disk'></span>";
    };

    delete_aquifer = function(e, cell){
        aquiferGroup.clearLayers();
        var data = {
            aquifer_id: cell.getRow().getData().id
        };
        //update database
        var xhr = deleteRowData($(this), data);
        if (xhr != null) {
            xhr.done(function (data) {
                if ('success' in data) {
                    addSuccessMessage("Aquifer Successfully Deleted!");
                    cell.getRow().delete();
                }
            });
        }
    };


    view_aquifer = function(e, cell){
        var cell_data = cell.getRow().getData();
        var aquifer_id = cell_data.id;
        var defaultParameters = {
            service : 'WFS',
            version : '2.0.0',
            request : 'GetFeature',
            typeName : 'gwdm:aquifer',
            outputFormat : 'text/javascript',
            format_options : 'callback:getJson',
            SrsName : 'EPSG:4326',
            featureID: 'aquifer.'+aquifer_id
        };

        var parameters = L.Util.extend(defaultParameters);
        var URL = $geoserverUrl + L.Util.getParamString(parameters);

        aquiferGroup.clearLayers();

        var ajax = $.ajax({
            url : URL,
            dataType : 'jsonp',
            jsonpCallback : 'getJson',
            success : function (response) {
                var feature = L.geoJSON(response).addTo(aquiferGroup);
                map.fitBounds(feature.getBounds());
            }
        });
    };

    update_form = function(e, cell){
        $modalUpdate.modal('show');

        //scroll back to top
        window.scrollTo(0,0);
        // clear messages
        $('#message').addClass('hidden');
        $('#message').empty()
            .addClass('hidden')
            .removeClass('alert-success')
            .removeClass('alert-info')
            .removeClass('alert-warning')
            .removeClass('alert-danger');


        var cell_data = cell.getRow().getData();
        var aquifer_id = cell_data.id;
        var aquifer_name = cell_data.aquifer_name;
        // var aquifer_name_id = cell_data.aquifer_id;

        $("#id-input").val(aquifer_id);
        $("#aquifer-text-input").val(aquifer_name);
        // $("#aquifer-id-input").val(aquifer_name_id);

    };

    submit_update_aquifer = function(){
        aquiferGroup.clearLayers();
        var aquifer_id = $("#id-input").val();
        var aquifer_name = $("#aquifer-text-input").val();
        var aquifer_name_id = $("#aquifer-id-input").val();

        var data = new FormData();
        data.append("aquifer_id", aquifer_id);
        data.append("aquifer_name", aquifer_name);
        data.append("aquifer_name_id", aquifer_name_id);

        var xhr = ajax_update_database_with_file("update", data);
        xhr.done(function(return_data){
            if("success" in return_data){
                // reset_form(return_data)
                addSuccessMessage("Aquifer Update Successful!");
                init_table();
            }else if("error" in return_data){
                addErrorMessage(return_data["error"]);
            }
        });

    };

    $(".submit-update-aquifer").click(submit_update_aquifer);


    init_dropdown = function () {
    };

    init_table = function(){
        var table = new Tabulator("#tabulator-table", {
            height:"311px",
            responsiveLayout:true, // enable responsive layouts
            layout:"fitColumns",
            ajaxURL:"tabulator",
            ajaxProgressiveLoad:"load",
            paginationSize:10,
            placeholder:"No Data Set",
            selectable:1,
            selectablePersistence:false,
            columns:[
                {title:"ID", field:"id", sorter:"number", align:"center"},
                {title:"View", formatter:viewIcon, align:"center", cellClick:function(e, cell){view_aquifer(e, cell)}},
                {title:"Edit", formatter:updateIcon, align:"center", cellClick:function(e, cell){update_form(e, cell)}},
                {title:"Delete", formatter:deleteIcon, align:"center", cellClick:function(e, cell){delete_aquifer(e, cell)}},
                {title:"Aquifer  Name", field:"aquifer_name", sorter:"string", headerFilter:"select", headerFilterParams:{values:true}},
                {title:"Aquifer  ID", field:"aquifer_id", sorter:"string", headerFilter:"select", headerFilterParams:{values:true}}
            ]
        });
    };

    init_all = function(){
        init_jquery_vars();
        init_map();
        init_dropdown();
        init_table();
    };

    /************************************************************************
     *                        DEFINE PUBLIC INTERFACE
     *************************************************************************/
    /*
     * Library object that contains public facing functions of the package.
     * This is the object that is returned by the library wrapper function.
     * See below.
     * NOTE: The functions in the public interface have access to the private
     * functions of the library because of JavaScript function scope.
     */
    public_interface = {

    };

    /************************************************************************
     *                  INITIALIZATION / CONSTRUCTOR
     *************************************************************************/

    // Initialization: jQuery function that gets called when
    // the DOM tree finishes loading
    $(function() {
        init_all();
    });

    return public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.