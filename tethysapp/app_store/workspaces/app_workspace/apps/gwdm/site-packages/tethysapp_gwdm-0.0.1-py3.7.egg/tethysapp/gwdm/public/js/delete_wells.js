/*****************************************************************************
 * FILE:    Delete Wells
 * DATE:    29 JULY 2020
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

    var delete_wells,
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
            addSuccessMessage('Wells Successfully Deleted!');
            $("#aquifer-select").empty().trigger('change');
        }
    };

    init_jquery_vars = function(){
    };

    delete_wells = function(){
        reset_alert();
        var region = $("#region-select option:selected").val();
        var aquifer = $("#aquifer-select option:selected").toArray().map(item => item.value).join();

        if(aquifer === ""){
            addErrorMessage("Aquifer cannot be empty! Please select an Aquifer.");
            return false;
        }else{
            reset_alert();
        }

        addInfoMessage("Deleting Wells. Please wait...","message");


        var submit_data = {'region': region, 'aquifer': aquifer}
        var submit_button = $("#submit-delete-wells");
        var submit_button_html = submit_button.html();
        submit_button.text('Deleting Wells ...');
        var xhr = ajax_update_database("submit", submit_data); //Submitting the data through the ajax function, see main.js for the helper function.
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


    };

    $("#submit-delete-wells").click(delete_wells);

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
        $("#region-select").change(function(){
            var region = $("#region-select option:selected").val();
            var xhr = ajax_update_database("get-aquifers", {'id': region}); //Submitting the data through the ajax function, see main.js for the helper function.
            xhr.done(function(return_data){ //Reset the form once the data is added successfully
                if("success" in return_data){
                    var options = return_data["aquifers_list"];
                    var var_options = return_data["variables_list"];
                    $("#aquifer-select").html('');
                    $("#aquifer-select").val(null).trigger('change.select2');
                    $("#aquifer-select").select2({'multiple': true,  placeholder: "Select an Aquifer(s)"});
                    // var empty_opt = '<option value="" selected disabled>Select item...</option>';
                    // var var_empty_opt = '<option value="" selected disabled>Select item...</option>';
                    var all_opt = new Option('All Aquifers', 'all');
                    // $("#aquifer-select").append(empty_opt);
                    $("#aquifer-select").append(all_opt);
                    // $("#variable-select").append(var_empty_opt);
                    options.forEach(function(attr,i){
                        var aquifer_option = new Option(attr[0], attr[1]);
                        $("#aquifer-select").append(aquifer_option);
                    });

                }else{
                    addErrorMessage(return_data['error']);
                }
            });
        }).change();

        $("#aquifer-select").on('select2:select select2:unselecting', function(){
            var selected = $(this).val();

            if(selected != null)
            {
                if(selected.indexOf('all')>=0){
                    $(this).val('all').select2();
                }
            }
        });

    });

    return public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.