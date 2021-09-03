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
        $shp_input,
        $measurementsModal;


    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/

    var add_measurements,
        get_shp_attributes,
        init_all,
        init_jquery_vars,
        init_dropdown,
        reset_dropdown,
        reset_form;



    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/
    //Reset the form when the request is made succesfully
    reset_form = function(result){
        if("success" in result){
            $("#shp-upload-input").val('');
            $(".attributes").addClass('hidden');
            $(".add").addClass('hidden');
            $("#id_attributes").val('');
            $("#time_attributes").val('');
            $("#value_attributes").val('');
            $("#format-text-input").val('');
            $("#aquifer_attributes").val('');
            reset_dropdown();
            addSuccessMessage('Measurements Upload Complete!');
        }
    };

    init_jquery_vars = function(){
        $shp_input = $("#shp-upload-input");
        $measurementsModal = $("#measurements-modal");
    };

    reset_dropdown = function(){
        $("#id_attributes").html('');
        $("#time_attributes").html('');
        $("#value_attributes").html('');
        $("#aquifer_attributes").html('');
        $("#id_attributes").val(null).trigger('change.select2');
        $("#time_attributes").val(null).trigger('change.select2');
        $("#value_attributes").val(null).trigger('change.select2');
        $("#aquifer_attributes").val(null).trigger('change.select2');
    };

    init_dropdown = function () {
        $(".id_attributes").select2();
        $(".aquifer_attributes").select2();
        $(".time_attributes").select2();
        $(".value_attributes").select2();
        $(".meta_attributes").select2();
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
                $measurementsModal.modal('show');
                var attributes = return_data["attributes"];
                reset_dropdown();
                var empty_opt = '<option value="" selected disabled>Select item...</option>';
                $("#id_attributes").append(empty_opt);
                $("#time_attributes").append(empty_opt);
                $("#value_attributes").append(empty_opt);
                $("#aquifer_attributes").append(empty_opt);

                attributes.forEach(function(attr,i){
                    var aquifer_option = new Option(attr, attr);
                    var id_option = new Option(attr, attr);
                    var time_option = new Option(attr, attr);
                    var value_option = new Option(attr, attr);

                    $("#time_attributes").append(time_option);
                    $("#value_attributes").append(value_option);
                    $("#id_attributes").append(id_option);
                    $("#aquifer_attributes").append(aquifer_option);
                });
                $(".add").removeClass('hidden');
            }else{
                addErrorMessage(return_data['error']);
            }
        });
    };

    $("#submit-get-attributes").click(get_shp_attributes);

    add_measurements = function(){
        var shapefiles = $("#shp-upload-input")[0].files;
        if($shp_input.val() === ""){
            addErrorMessage("Layer Shape File cannot be empty!");
            return false;
        }else{
            reset_alert();
        }

        var id =  $("#id_attributes option:selected").val();
        var time = $("#time_attributes option:selected").val();
        var value = $("#value_attributes option:selected").val();
        var variable_id = $("#variable-select option:selected").val();
        var region_id = $("#region-select option:selected").val();
        var time_format = $("#format-text-input").val();
        var aquifer_id = $("#aquifer-select option:selected").val();
        var aquifer_col = $("#aquifer_attributes option:selected").val();
        addInfoMessage("Adding measurements. Please wait...","message");

        var data = new FormData();
        for(var i=0;i < shapefiles.length;i++){
            data.append("shapefile",shapefiles[i]);
        }
        data.append("time", time);
        data.append("value", value);
        data.append("id", id);
        data.append("variable_id", variable_id);
        data.append("date_format", time_format);
        data.append("region_id", region_id);
        data.append("aquifer_id", aquifer_id);
        data.append("aquifer_col", aquifer_col);

        var submit_button = $("#submit-add-measurements");
        var submit_button_html = submit_button.html();
        submit_button.text('Submitting ...');
        var xhr = ajax_update_database_with_file("submit", data); //Submitting the data through the ajax function, see main.js for the helper function.
        xhr.done(function(return_data){ //Reset the form once the data is added successfully
            if("success" in return_data){
                submit_button.html(submit_button_html);
                reset_form(return_data);
                console.log(return_data);
            }else{
                addErrorMessage(return_data['error']);
            }
        });
    };

    $(".submit-add-measurements").click(add_measurements);



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
        window.onbeforeunload = null;
        $('#variable-select').select2('val', '');

        $("#region-select").change(function(){
            var region = $("#region-select option:selected").val();
            var xhr = ajax_update_database("get-aquifers", {'id': region}); //Submitting the data through the ajax function, see main.js for the helper function.
            xhr.done(function(return_data){ //Reset the form once the data is added successfully
                if("success" in return_data){
                    var options = return_data["aquifers_list"];
                    $("#aquifer-select").html('');
                    var empty_opt = '<option value="" selected disabled>Select item...</option>';
                    $("#aquifer-select").append(empty_opt);
                    options.forEach(function(attr,i){
                        var aquifer_option = new Option(attr[0], attr[1]);
                        $("#aquifer-select").append(aquifer_option);
                    });
                }else{
                    addErrorMessage(return_data['error']);
                }
            });
        }).change();

        $("#format-text-input").focusout(function(){
            var time_format = $("#format-text-input").val();
            var xhr = ajax_update_database("check-date-format", {'time_format': time_format});
            xhr.done(function(return_data){ //Reset the form once the data is added successfully
                if("success" in return_data){
                    var is_valid = return_data['is_valid'];
                    if(is_valid===true){
                        $('.submit-add-measurements').removeClass('hidden');
                    }else{
                        $('.submit-add-measurements').addClass('hidden');
                    }

                }else{
                    addErrorMessage(return_data['is_valid']);
                }
            });
        });
    });

    return public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.