/*****************************************************************************
 * FILE:    GRACE ADD GEOSERVER
 * DATE:    18 MAY 2017
 * AUTHOR: Sarva Pulla
 * COPYRIGHT: (c) Brigham Young University 2017
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var GRACE_ADD_GEOSERVER = (function() {
    // Wrap the library in a package function
    "use strict"; // And enable strict mode for this library

    /************************************************************************
     *                      MODULE LEVEL / GLOBAL VARIABLES
     *************************************************************************/
    var public_interface;				// Object returned by the module



    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/

    var add_thredds_server,init_jquery,reset_alert,reset_form;

    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/

    init_jquery = function(){
    };

    //Reset the alerts if everything is going well
    reset_alert = function(){
        $("#message").addClass('hidden');
        $("#message").empty()
            .addClass('hidden')
            .removeClass('alert-success')
            .removeClass('alert-info')
            .removeClass('alert-warning')
            .removeClass('alert-danger');
    };

    //Reset the form when the request is made succesfully
    reset_form = function(result){
        if("success" in result){
            $("#thredds-name-input").val('');
            $("#thredds-url-input").val('');
            $("#thredds-username-input").val('');
            $("#thredds-password-input").val('');
            addSuccessMessage('Thredds Server Upload Complete!');
        }
    };

    add_thredds_server = function(){
        reset_alert();
        var thredds_server_name = $("#thredds-name-input").val();
        var thredds_server_url = $("#thredds-url-input").val();

        var thredds_server_username = $("#thredds-username-input").val();
        var thredds_server_password = $("#thredds-password-input").val();

        if(thredds_server_name == ""){
            addErrorMessage("Thredds Server Name cannot be empty!");
            return false;
        }else{
            reset_alert();
        }
        if(thredds_server_url == ""){
            addErrorMessage("Thredds Server Url cannot be empty!");
            return false;
        }else{
            reset_alert();
        }
        if(thredds_server_username == ""){
            addErrorMessage("Thredds Server Username cannot be empty!");
            return false;
        }else{
            reset_alert();
        }
        if(thredds_server_password == ""){
            addErrorMessage("Thredds Server Password cannot be empty!");
            return false;
        }else{
            reset_alert();
        }

        if(thredds_server_url.includes('/thredds') == false){
            addErrorMessage("Thredds Server should have /thredds after the IP Address");
            return false;
        }else{
            reset_alert();
        }

        if (thredds_server_url.substr(-1) !== "/") {
            thredds_server_url = thredds_server_url.concat("/");
        }
        var data = {"thredds_server_name":thredds_server_name,"thredds_server_url":thredds_server_url,"thredds_server_username":thredds_server_username,"thredds_server_password":thredds_server_password};

        var xhr = ajax_update_database("submit",data);
        xhr.done(function(return_data){
            if("success" in return_data){
                reset_form(return_data);
            }else if("error" in return_data){
                addErrorMessage(return_data["error"]);
            }
        });



    };
    $("#submit-add-thredds-server").click(add_thredds_server);

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
        init_jquery();

    });

    return public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.
