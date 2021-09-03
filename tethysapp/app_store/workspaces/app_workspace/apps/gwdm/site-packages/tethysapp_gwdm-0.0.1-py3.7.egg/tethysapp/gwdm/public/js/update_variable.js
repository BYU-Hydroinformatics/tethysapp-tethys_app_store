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
    var $modalUpdate,
        public_interface;

    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/

    var delete_variable,
        update_form,
        init_all,
        init_events,
        init_jquery_vars,
        init_dropdown,
        init_table,
        reset_form,
        submit_update_variable,
        view_variable;



    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/
    //Reset the form when the request is made successfully
    reset_form = function(result){
        if("success" in result){
            $("#variable-text-input").val('');
            $("#units-text-input").val('');
            $("#desc-text-input").val('');
            addSuccessMessage('Variable Update Complete!');
        }
    };


    init_jquery_vars = function(){
        $modalUpdate = $("#update-modal");
    };

    $('#update-modal').on('hide.bs.modal', function () {
        reset_form({"reset": "reset"});
    });


    var deleteIcon = function(cell, formatterParams){ //plain text value
        return "<span class='glyphicon glyphicon-remove'></span>";
    };

    var updateIcon = function(cell, formatterParams){ //plain text value
        return "<span class='glyphicon glyphicon-floppy-disk'></span>";
    };

    delete_variable = function(e, cell){
        var data = {
            variable_id: cell.getRow().getData().id
        };
        //update database
        var xhr = deleteRowData($(this), data);
        if (xhr != null) {
            xhr.done(function (data) {
                if ('success' in data) {
                    addSuccessMessage("Variable Successfully Deleted!");
                    cell.getRow().delete();
                }
            });
        }
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
        var variable_id = cell_data.id;
        var variable_name = cell_data.variable_name;
        var variable_units = cell_data.variable_units;
        var variable_description = cell_data.variable_description;

        $("#id-input").val(variable_id);
        $("#variable-text-input").val(variable_name);
        $("#units-text-input").val(variable_units);
        $("#desc-text-input").val(variable_description);
    };

    submit_update_variable = function(){
        var variable_id = $("#id-input").val();
        var variable_name = $("#variable-text-input").val();
        var variable_units = $("#units-text-input").val();
        var variable_description = $("#desc-text-input").val();

        var data = new FormData();
        data.append("variable_id", variable_id);
        data.append("variable_name", variable_name);
        data.append("variable_units", variable_units);
        data.append("variable_description", variable_description)

        var xhr = ajax_update_database_with_file("update", data);
        xhr.done(function(return_data){
            if("success" in return_data){
                reset_form(return_data);
                addSuccessMessage("Variable Update Successful!");
                init_table();
            }else if("error" in return_data){
                addErrorMessage(return_data["error"]);
            }
        });

    };

    $(".submit-update-variable").click(submit_update_variable);


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
                {title:"Edit", formatter:updateIcon, align:"center", cellClick:function(e, cell){update_form(e, cell)}},
                {title:"Delete", formatter:deleteIcon, align:"center", cellClick:function(e, cell){delete_variable(e, cell)}},
                {title:"Variable Name", field:"variable_name", sorter:"string", headerFilter:"select", headerFilterParams:{values:true}},
                {title:"Variable Units", field:"variable_units", sorter:"string", headerFilter:"select", headerFilterParams:{values:true}},
                {title:"Variable Description", field:"variable_description", sorter:"string", headerFilter:"select", headerFilterParams:{values:true}}
            ]
        });
    };

    init_all = function(){
        init_jquery_vars();
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