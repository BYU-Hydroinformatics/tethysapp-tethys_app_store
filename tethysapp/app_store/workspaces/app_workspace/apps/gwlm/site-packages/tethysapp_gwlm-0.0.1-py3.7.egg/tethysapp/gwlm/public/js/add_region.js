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
    var public_interface,				// Object returned by the module
        $shp_input;


    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/

    var add_region,
        init_all,
        init_jquery_vars,
        init_dropdown,
        reset_form;



    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/
    //Reset the form when the request is made succesfully
    reset_form = function(result){
        if("success" in result){
            $("#region-text-input").val('');
            $("#shp-upload-input").val('');
            addSuccessMessage('Region Upload Complete!');
        }
    };

    init_jquery_vars = function(){
        $shp_input = $("#shp-upload-input");

    };

    init_dropdown = function () {
    };

    add_region = function(){
        reset_alert();
        var region = $("#region-text-input").val();
        var shapefiles = $("#shp-upload-input")[0].files;

        if(region === ""){
            addErrorMessage("Region name cannot be empty!");
            return false;
        }else{
            reset_alert();
        }
        addInfoMessage("Adding Region. Please wait...","message");
        var data = new FormData();
        data.append("region", region);
        for(var i=0;i < shapefiles.length;i++){
            data.append("shapefile",shapefiles[i]);
        }
        var submit_button = $("#submit-add-region");
        var submit_button_html = submit_button.html();
        submit_button.text('Submitting ...');
        var xhr = ajax_update_database_with_file("submit",data); //Submitting the data through the ajax function, see main.js for the helper function.
        xhr.done(function(return_data){ //Reset the form once the data is added successfully
            if("success" in return_data){
                submit_button.html(submit_button_html);
                reset_form(return_data);
            }else{
                submit_button.html(submit_button_html);
            }
        });
    };

    $("#submit-add-region").click(add_region);

    init_all = function(){
        init_jquery_vars();
        init_dropdown();
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