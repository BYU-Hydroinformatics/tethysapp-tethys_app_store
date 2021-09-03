/*****************************************************************************
 * FILE:    Interpolation JS
 * DATE:    17 APRIL 2020
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

    var form_validator,
        init_all,
        init_jquery_vars,
        init_dropdown,
        reset_form,
        submit_interpolation;



    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/

    //Reset the form when the request is made succesfully
    reset_form = function(result){
        if("success" in result){
            addSuccessMessage('Interpolation Complete!');
        }
    };

    init_jquery_vars = function(){

    };

    init_dropdown = function () {
    };

    form_validator = function(element, message){
        if(element === ""){
            console.log(element, message);
            addErrorMessage(message);
            return false;
        }else{
            reset_alert();
        }
    };

    submit_interpolation = function(){
        reset_alert();
        var region = $("#region-select option:selected").val();
        var aquifer = $("#aquifer-select option:selected").val();
        var variable = $("#variable-select option:selected").val();
        var porosity = $("#select-porosity").val();
        var spatial_interpolation = $("#select-spatial-interpolation option:selected").val();
        var temporal_interpolation = $("#select-temporal-interpolation option:selected").val();
        // var interpolation_options = $("#interpolation_options option:selected").val();
        var search_radius = $("#select-search-radius option:selected").val();
        var ndmin = $("#select-ndmin option:selected").val();
        var ndmax = $("#select-ndmax option:selected").val();
        var start_date = $("#start-date option:selected").val();
        var end_date = $("#end-date option:selected").val();
        var resolution = $("#resolution option:selected").val();
        var min_ratio = $("#min-ratio option:selected").val();
        var time_tolerance = $("#time-tolerance option:selected").val();
        var frequency = $("#frequency option:selected").val();
        var default_val = $("#default option:selected").val();
        var min_samples = $("#min-samples option:selected").val();
        var seasonal = $("#seasonal option:selected").val();
        var gap = $("#gap-size-input").val();
        var spacing = $("#spacing-input").val();
        var pad = $("#pad-input").val();

        // form_validator(region, "Region cannot be empty!");
        // if(region === ""){
        //     addErrorMessage("Region Cannot Be empty");
        //     return false;
        // }else{
        //     reset_alert();
        // }
        // if(aquifer === ""){
        //     addErrorMessage("Aquifer Cannot Be empty");
        //     return false;
        // }else{
        //     reset_alert();
        // }
        // if(variable === ""){
        //     addErrorMessage("Variable Cannot Be empty");
        //     return false;
        // }else{
        //     reset_alert();
        // }
        // form_validator(aquifer, "Aquifer cannot be empty!");
        // form_validator(variable, "Variable cannot be empty!");
        // form_validator(porosity, "Porosity cannot be empty!");
        // form_validator(spatial_interpolation, "Spatial Interpolation cannot be empty!");
        // form_validator(temporal_interpolation, "Temporal Interpolation cannot be empty!");
        // form_validator(interpolation_options, "Interpolation options cannot be empty!");

        addInfoMessage("Interpolation in Progress. Please wait...","message");
        var data = new FormData();
        data.append("region", region);
        data.append("aquifer", aquifer);
        data.append("variable", variable);
        data.append("porosity", porosity);
        data.append("spatial_interpolation", spatial_interpolation);
        data.append("temporal_interpolation", temporal_interpolation);
        // data.append("interpolation_options", interpolation_options);
        data.append("search_radius", search_radius);
        data.append("ndmin", ndmin);
        data.append("ndmax", ndmax);
        data.append("start_date", start_date);
        data.append("end_date", end_date);
        data.append("resolution", resolution);
        data.append("min_ratio", min_ratio);
        data.append("time_tolerance", time_tolerance);
        data.append("frequency", frequency);
        data.append("default", default_val);
        data.append("min_samples", min_samples);
        data.append("seasonal", seasonal);
        data.append("from_wizard", true);
        data.append("gap_size", gap);
        data.append("spacing", spacing);
        data.append("pad", pad);


        var submit_button = $("#submit");
        var submit_button_html = submit_button.html();
        submit_button.text('Submitting ...');
        var xhr = ajax_update_database_with_file("submit",data); //Submitting the data through the ajax function, see main.js for the helper function.
        xhr.done(function(return_data){ //Reset the form once the data is added successfully
            if("success" in return_data){
                submit_button.html(submit_button_html);
                reset_form(return_data);
                console.log(return_data);
            }else{
                submit_button.html(submit_button_html);
                addErrorMessage(return_data['error']);
                console.log(return_data['error'])
            }
        });
        // xhr.fail(function(xhr, status, error){
        //     console.log(xhr.responseText);
        //     addErrorMessage(xhr.responseText);
        //     submit_button.html(submit_button_html)
        // });
    };

    $("#submit").click(submit_interpolation);

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
        $("#region-select").change(function(){
            var region = $("#region-select option:selected").val();
            var xhr = ajax_update_database("get-aquifers", {'id': region}); //Submitting the data through the ajax function, see main.js for the helper function.
            xhr.done(function(return_data){ //Reset the form once the data is added successfully
                if("success" in return_data){
                    var options = return_data["aquifers_list"];
                    var var_options = return_data["variables_list"];
                    $("#aquifer-select").html('');
                    $("#variable-select").html('');
                    var empty_opt = '<option value="" selected disabled>Select item...</option>';
                    var var_empty_opt = '<option value="" selected disabled>Select item...</option>';
                    var all_opt = new Option('All Aquifers', 'all');
                    $("#aquifer-select").append(empty_opt);
                    $("#aquifer-select").append(all_opt);
                    $("#variable-select").append(var_empty_opt);
                    options.forEach(function(attr,i){
                        var aquifer_option = new Option(attr[0], attr[1]);
                        $("#aquifer-select").append(aquifer_option);
                    });
                    var_options.forEach(function(attr, i){
                        var var_option = new Option(attr[0], attr[1]);
                        $("#variable-select").append(var_option);
                    });
                    $('#variable-select').select2('val', '');

                }else{
                    addErrorMessage(return_data['error']);
                }
            });
        }).change();
    });

    return public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.