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
        wellGroup;

    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/

    var delete_well,
        init_all,
        init_events,
        init_jquery_vars,
        init_dropdown,
        init_map,
        init_table,
        reset_form,
        view_well;

    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/
    //Reset the form when the request is made successfully
    reset_form = function(result){
        if("success" in result){
            $("#region-text-input").val('');
            $("#shp-upload-input").val('');
            addSuccessMessage('Well Update Complete!');
        }
    };


    init_jquery_vars = function(){
        $modalUpdate = $("#update-well");
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

        wellGroup = L.layerGroup().addTo(map);
    };


    $('#update-well').on('hide.bs.modal', function () {
        reset_form({"reset": "reset"});
    });

    var viewIcon = function(cell, formatterParams){ //plain text value
        return "<span class='glyphicon glyphicon-sunglasses view-region-tabulator'></span>";
    };

    var deleteIcon = function(cell, formatterParams){ //plain text value
        return "<span class='glyphicon glyphicon-remove'></span>";
    };

    var updateIcon = function(cell, formatterParams){ //plain text value
        return "<span class='glyphicon glyphicon-floppy-disk'></span>";
    };

    delete_well = function(e, cell){
        wellGroup.clearLayers();
        var data = {
            well_id: cell.getRow().getData().id
        };
        //update database
        var xhr = deleteRowData($(this), data);
        if (xhr != null) {
            xhr.done(function (data) {
                if ('success' in data) {
                    addSuccessMessage("Well Successfully Deleted!");
                    cell.getRow().delete();
                }
            });
        }
    };

    function onEachFeature(feature, layer) {
        // does this feature have a property named popupContent?
        if (feature.properties && feature.properties.popupContent) {
            layer.bindPopup(feature.properties.popupContent);
        }
    }

    view_well = function(e, cell){
        var cell_data = cell.getRow().getData();
        var well_id = cell_data.id;
        var defaultParameters = {
            service : 'WFS',
            version : '2.0.0',
            request : 'GetFeature',
            typeName : 'gwlm:well',
            outputFormat : 'text/javascript',
            format_options : 'callback:getJson',
            SrsName : 'EPSG:4326',
            featureID: 'well.'+well_id
        };

        var parameters = L.Util.extend(defaultParameters);
        var URL = $geoserverUrl + L.Util.getParamString(parameters);

        wellGroup.clearLayers();

        var ajax = $.ajax({
            url : URL,
            dataType : 'jsonp',
            jsonpCallback : 'getJson',
            success : function (response) {
                var feature = L.geoJSON(response).addTo(wellGroup);
                map.fitBounds(feature.getBounds());
            }
        });
    };


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
                {title:"View", formatter:viewIcon, align:"center", cellClick:function(e, cell){view_well(e, cell)}},
                // {title:"Edit", formatter:updateIcon, align:"center", cellClick:function(e, cell){update_form(e, cell)}},
                {title:"Delete", formatter:deleteIcon, align:"center", cellClick:function(e, cell){delete_well(e, cell)}},
                {title:"Well Name", field:"well_name", sorter:"string", headerFilter:"select", headerFilterParams:{values:true}},
                // {title:"Well ID", field:"well_id", sorter:"string", headerFilter:"select", headerFilterParams:{values:true}},
                {title:"GSE", field:"gse", sorter:"string"},
                {title:"Attributes", field:"attr_dict", align:"center", sorter:"string"},
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