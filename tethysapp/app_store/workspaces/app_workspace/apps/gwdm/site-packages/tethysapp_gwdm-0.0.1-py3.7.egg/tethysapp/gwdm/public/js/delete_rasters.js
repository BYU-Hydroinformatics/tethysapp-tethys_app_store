/*****************************************************************************
 * FILE:    Delete Wells
 * DATE:    20 AUGUST 2020
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
    var public_interface;

    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/

    var delete_rasters,
        get_wms_datasets,
        init_all,
        init_events,
        init_jquery_vars,
        reset_form;

    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/
    //Reset the form when the request is made succesfully
    reset_form = function(result){
        if("success" in result){
            addSuccessMessage('Raster Successfully Deleted!');
            $("#aquifer-select").empty().trigger('change');
            $("#variable-select").empty().trigger('change');        }
    };

    init_jquery_vars = function(){
    };

    delete_rasters = function(){
        reset_alert();
        var region = $("#region-select option:selected").val();
        var aquifer = $("#aquifer-select option:selected").toArray().map(item => item.text).join();
        var variable = $("#variable-select option:selected").toArray().map(item => item.value).join();
        var raster = $("#select-interpolation option:selected").toArray().map(item => item.value).join();
        if(aquifer === ""){
            addErrorMessage("Aquifer cannot be empty! Please select an Aquifer.");
            return false;
        }else{
            reset_alert();
        }
        if(variable === ""){
            addErrorMessage("Variable cannot be empty! Please select a Variable.");
            return false;
        }else{
            reset_alert();
        }
        if(raster === ""){
            addErrorMessage("Raster cannot be empty! Please select a Raster.");
            return false;
        }else{
            reset_alert();
        }
        addInfoMessage("Deleting Rasters. Please wait...","message");


        var submit_data = {'region': region, 'aquifer': aquifer, 'variable': variable, 'raster': raster};
        var submit_button = $("#submit-delete-rasters");
        var submit_button_html = submit_button.html();
        submit_button.text('Deleting Rasters ...');
        var xhr = ajax_update_database("submit", submit_data); //Submitting the data through the ajax function, see main.js for the helper function.
        xhr.done(function(return_data){ //Reset the form once the data is added successfully
            if("success" in return_data){
                submit_button.html(submit_button_html);
                reset_form(return_data);
            }else{
                submit_button.html(submit_button_html);
                addErrorMessage(return_data['error']);
            }
        });

    };

    $("#submit-delete-rasters").click(delete_rasters);

    get_wms_datasets = function(aquifer_name, variable_id, region_id){
        var data = {"aquifer_name": aquifer_name, "variable_id": variable_id, "region_id": region_id};
        if(aquifer_name !== 'all' || variable_id !== 'all'){
            var xhr = ajax_update_database("get-wms-datasets", data);
            xhr.done(function(return_data) {
                if ("success" in return_data) {
                    $("#select-interpolation").html('');
                    $("#select-interpolation").val(null).trigger('change.select2');
                    $("#select-interpolation").select2({'multiple': true,  placeholder: "Select a Raster(s)"});
                    // $("#select-interpolation").prop("selected", false);
                    var empty_opt = '<option value="" selected disabled>Select item...</option>';
                    // $("#select-interpolation").val('').trigger('change');
                    var wms_options = return_data['wms_files'];
                    var all_opt = new Option('All Rasters', 'all');
                    $("#select-interpolation").append(all_opt);
                    wms_options.forEach(function(attr,i){
                        var wms_option = new Option(attr[1], attr[1]);
                        $("#select-interpolation").append(wms_option);
                    });
                }
            });
        }

    };

    init_all = function(){
        init_jquery_vars();
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
        var var_empty_opt = '<option value="" selected disabled>Select item...</option>';
        var all_var_opt = new Option('All Variables', 'all');
        $("#variable-select").prepend(all_var_opt);
        $("#variable-select").prepend(var_empty_opt);
        $('#variable-select').select2('val', '');

        $("#region-select").change(function(){
            var region = $("#region-select option:selected").val();
            var xhr = ajax_update_database("get-aquifers", {'id': region}); //Submitting the data through the ajax function, see main.js for the helper function.
            xhr.done(function(return_data){ //Reset the form once the data is added successfully
                if("success" in return_data){
                    var options = return_data["aquifers_list"];
                    var var_options = return_data["variables_list"];
                    $("#aquifer-select").html('');
                    // $("#variable-select").html('');
                    $("#aquifer-select").val(null).trigger('change.select2');
                    // $("#variable-select").val(null).trigger('change.select2');
                    // $("#variable-select").select2({'multiple': true,  placeholder: "Select a Variable(s)"});
                    $("#aquifer-select").select2({'multiple': false,  placeholder: "Select an Aquifer(s)"});
                    var empty_opt = '<option value="" selected disabled>Select item...</option>';
                    // var var_empty_opt = '<option value="" selected disabled>Select item...</option>';
                    var all_opt = new Option('All Aquifers', 'all');
                    // var all_var_opt = new Option('All Variables', 'all');
                    $("#aquifer-select").append(empty_opt);
                    $("#aquifer-select").append(all_opt);
                    // $("#variable-select").append(var_empty_opt);
                    // $("#variable-select").append(all_var_opt);
                    options.forEach(function(attr,i){
                        var aquifer_option = new Option(attr[0], attr[1]);
                        $("#aquifer-select").append(aquifer_option);
                    });
                    // var_options.forEach(function(attr, i){
                    //     var var_option = new Option(attr[0], attr[1]);
                    //     $("#variable-select").append(var_option);
                    // });

                }else{
                    addErrorMessage(return_data['error']);
                }
            });
        }).change();

        $("#variable-select").on('select2:select select2:unselecting', function(){
            var selected = $(this).val();

            if(selected != null)
            {
                if(selected.indexOf('all')>=0){
                    $(this).val('all').select2();
                }
            }
        });

        $("#select-interpolation").on('select2:select select2:unselecting', function(){
            var selected = $(this).val();

            if(selected != null)
            {
                if(selected.indexOf('all')>=0){
                    $(this).val('all').select2();
                }
            }
        });

        $("#aquifer-select").change(function(){
            var region = $("#region-select option:selected").val();
            var variable_id = $("#variable-select option:selected").val();
            var aquifer_name = $("#aquifer-select option:selected").text();
            if(typeof variable_id !== 'undefined'){
                get_wms_datasets(aquifer_name, variable_id, region);

            }
        });

        $("#variable-select").change(function(){
            var region = $("#region-select option:selected").val();
            var aquifer_id = $("#aquifer-select option:selected").val();
            var variable_id = $("#variable-select option:selected").val();
            var aquifer_name = $("#aquifer-select option:selected").text();
            if(typeof aquifer_id !== 'undefined'){
                get_wms_datasets(aquifer_name, variable_id, region);
            }
        });

    });

    return public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.