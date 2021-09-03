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

    var add_aquifer,
        get_shp_attributes,
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
            $("#shp-upload-input").val('');
            $(".attributes").addClass('hidden');
            $("#name_attributes").html('');
            $("#id_attributes").html('');
            $(".add").addClass('hidden');
            addSuccessMessage('Aquifer Upload Complete!');
        }
    };

    init_jquery_vars = function(){
        $shp_input = $("#shp-upload-input");

    };

    init_dropdown = function () {
        $(".name_attributes").select2();
        $(".id_attributes").select2();
    };


    get_shp_attributes = function(){

        var shapefiles = $("#shp-upload-input")[0].files;
        if($shp_input.val() === ""){
            addErrorMessage("Layer Shape File cannot be empty!");
            return false;
        }else{
            reset_alert();
        }

        addInfoMessage("Getting attributes. Please wait...","message");
        var data = new FormData();
        for(var i=0;i < shapefiles.length;i++){
            data.append("shapefile",shapefiles[i]);
        }
        var submit_button = $("#submit-get-attributes");
        var submit_button_html = submit_button.html();
        submit_button.text('Submitting ...');
        var xhr = ajax_update_database_with_file("get-attributes", data); //Submitting the data through the ajax function, see main.js for the helper function.
        xhr.done(function(return_data){ //Reset the form once the data is added successfully
            if("success" in return_data){
                submit_button.html(submit_button_html);
                $(".attributes").removeClass('hidden');
                $("#name_attributes").html('');
                $("#id_attributes").html('');
                $("#name_attributes").val(null).trigger('change.select2');
                $("#id_attributes").val(null).trigger('change.select2');

                var empty_opt = '<option value="" selected disabled>Select Name...</option>';
                var empty_opt_2 = '<option value="" selected disabled>Select ID...</option>';
                $("#name_attributes").append(empty_opt);
                $("#id_attributes").append(empty_opt_2);

                var attributes = return_data["attributes"];
                attributes.forEach(function(attr,i){
                    var name_option = new Option(attr, attr);
                    var id_option = new Option(attr, attr);
                    $("#name_attributes").append(name_option);
                    $("#id_attributes").append(id_option);
                });
                $(".add").removeClass('hidden');
            }else{
                addErrorMessage(return_data['error']);
            }
        });
    };

    $("#submit-get-attributes").click(get_shp_attributes);

    add_aquifer = function(){
        reset_alert();
        var shapefiles = $("#shp-upload-input")[0].files;
        var region_id = $("#region-select option:selected").val();
        var name_attribute = $("#name_attributes option:selected").val();
        var id_attribute = $("#id_attributes option:selected").val();

        addInfoMessage("Adding aquifer. Please wait...","message");
        var data = new FormData();
        data.append("region_id", region_id);
        data.append("name_attribute", name_attribute);
        data.append("id_attribute", id_attribute);
        for(var i=0;i < shapefiles.length;i++){
            data.append("shapefile",shapefiles[i]);
        }
        var submit_button = $("#submit-add-aquifer");
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

    $("#submit-add-aquifer").click(add_aquifer);

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