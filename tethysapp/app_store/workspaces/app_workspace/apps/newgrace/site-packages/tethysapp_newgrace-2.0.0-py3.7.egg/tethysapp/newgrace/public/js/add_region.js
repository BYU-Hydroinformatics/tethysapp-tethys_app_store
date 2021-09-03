/*****************************************************************************
 * FILE:    GRACE ADD REGION
 * DATE:    17 MAY 2017
 * AUTHOR: Sarva Pulla
 * COPYRIGHT: (c) Brigham Young University 2017
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var GRACE_ADD_REGION = (function() {
    // Wrap the library in a package function
    "use strict"; // And enable strict mode for this library

    /************************************************************************
     *                      MODULE LEVEL / GLOBAL VARIABLES
     *************************************************************************/
    var $region_input,
        $shp_input,
        $thredds_select,
        public_interface;				// Object returned by the module



    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/

    var add_region,
        init_jquery,
        reset_alert,
        reset_form,
        show_progress_modal,
        hide_progress_modal,
        progress,
        initial_sub_process,
        jpl_tot_process,
        jpl_gw_process,
        csr_tot_process,
        csr_gw_process,
        gfz_tot_process,
        gfz_gw_process,
        avg_tot_process,
        avg_gw_process,
        sw_process,
        soil_process,
        cleanup_process,
        update_db_process;


    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/

    init_jquery = function(){
        $shp_input = $("#shp-upload-input");
        $thredds_select = $("#thredds-select option:selected");
        $region_input = $("#region-name-input");
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
            $("#region-name-input").val('');
            $("#shp-upload-input").val('');
            addSuccessMessage('Region Upload Complete!');
        }
    };

    show_progress_modal = function(){
        $("#progress-modal").modal('show')
    };

    hide_progress_modal = function(){
        $("#progress-modal").modal('hide')
    };

    progress = function(value) {
        $("#progressbar").progressbar();
        var tick_function = function() {
            $("#progressbar").progressbar("option", "value", value);
            if (value < 100) {
                window.setTimeout(tick_function, 100000);
            }
        };
        window.setTimeout(tick_function, 100000);
    };


    initial_sub_process = function(data) {
        var sub_init = ajax_update_database_with_file("initial",data); //Submitting the data through the ajax function, see main.js for the helper function.
        sub_init.done(function(return_data){ //Reset the form once the data is added successfully
            if("initial" in return_data){
                addInfoMessage("Processing JPL Total Storage....................Overall Job Status: 0% (Aprox. 20 minutes remaining)","message");
                var percentval = 0;
                progress(percentval);
                jpl_tot_process(data);
//                update_db_process(data);
            };
        });
    };

    jpl_tot_process = function(data) {
        var sub_jpl_tot = ajax_update_database_with_file("jpl-tot",data); //Submitting the data through the ajax function, see main.js for the helper function.
        sub_jpl_tot.done(function(return_data){ //Reset the form once the data is added successfully
            if("jpl-tot" in return_data){
                addInfoMessage("Processing JPL Groundwater Storage....................Overall Job Status: 10% (Aprox. 18 minutes remaining)","message");
                var percentval = 10;
                progress(percentval);
                jpl_gw_process(data);
            }
        });
    };

    jpl_gw_process = function(data) {
        var sub_jpl_gw = ajax_update_database_with_file("jpl-gw",data); //Submitting the data through the ajax function, see main.js for the helper function.
        sub_jpl_gw.done(function(return_data){ //Reset the form once the data is added successfully
            if("jpl-gw" in return_data){
                addInfoMessage("Processing CSR Total Storage....................Overall Job Status: 20% (Aprox. 16 minutes remaining)","message");
                var percentval = 20;
                progress(percentval);
                csr_tot_process(data);
            }
        });
    };

    csr_tot_process = function(data) {
        var sub_csr_tot = ajax_update_database_with_file("csr-tot",data); //Submitting the data through the ajax function, see main.js for the helper function.
        sub_csr_tot.done(function(return_data){ //Reset the form once the data is added successfully
            if("csr-tot" in return_data){
                addInfoMessage("Processing CSR Groundwater Storage....................Overall Job Status: 30% (Aprox. 14 minutes remaining)","message");
                var percentval = 30;
                progress(percentval);
                csr_gw_process(data);
            }
        });
    };

    csr_gw_process = function(data) {
        var sub_csr_gw = ajax_update_database_with_file("csr-gw",data); //Submitting the data through the ajax function, see main.js for the helper function.
        sub_csr_gw.done(function(return_data){ //Reset the form once the data is added successfully
            if("csr-gw" in return_data){
                addInfoMessage("Processing GFZ Total Storage....................Overall Job Status: 40% (Aprox. 12 minutes remaining)","message");
                var percentval = 40;
                progress(percentval);
                gfz_tot_process(data);
            }
        });
    };

    gfz_tot_process = function(data) {
        var sub_gfz_tot = ajax_update_database_with_file("gfz-tot",data); //Submitting the data through the ajax function, see main.js for the helper function.
        sub_gfz_tot.done(function(return_data){ //Reset the form once the data is added successfully
            if("gfz-tot" in return_data){
                addInfoMessage("Processing GFZ Groundwater Storage....................Overall Job Status: 50% (Aprox. 10 minutes remaining)","message");
                var percentval = 50;
                progress(percentval);
                gfz_gw_process(data);
            }
        });
        };

    gfz_gw_process = function(data) {
        var sub_gfz_gw = ajax_update_database_with_file("gfz-gw",data); //Submitting the data through the ajax function, see main.js for the helper function.
        sub_gfz_gw.done(function(return_data){ //Reset the form once the data is added successfully
            if("gfz-gw" in return_data){
                addInfoMessage("Processing AVG Total Storage....................Overall Job Status: 60% (Aprox. 8 minutes remaining)","message");
                var percentval = 60;
                progress(percentval);
                avg_tot_process(data);
            }
        });
    };

    avg_tot_process = function(data) {
        var sub_avg_tot = ajax_update_database_with_file("avg-tot",data); //Submitting the data through the ajax function, see main.js for the helper function.
        sub_avg_tot.done(function(return_data){ //Reset the form once the data is added successfully
            if("avg-tot" in return_data){
                addInfoMessage("Processing AVG Groundwater Storage....................Overall Job Status: 70% (Aprox. 6 minutes remaining)","message");
                var percentval = 70;
                progress(percentval);
                avg_gw_process(data);
            }
        });
    };

    avg_gw_process = function(data) {
        var sub_avg_gw = ajax_update_database_with_file("avg-gw",data); //Submitting the data through the ajax function, see main.js for the helper function.
        sub_avg_gw.done(function(return_data){ //Reset the form once the data is added successfully
            if("avg-gw" in return_data){
                addInfoMessage("Processing Surface Water Storage....................Overall Job Status: 80% (Aprox. 4 minutes remaining)","message");
                var percentval = 80;
                progress(percentval);
                sw_process(data);
            }
        });
    };

    sw_process = function(data) {
        var sub_sw = ajax_update_database_with_file("sw",data); //Submitting the data through the ajax function, see main.js for the helper function.
        sub_sw.done(function(return_data){ //Reset the form once the data is added successfully
            if("sw" in return_data){
                addInfoMessage("Processing Soil Moisture Storage....................Overall Job Status: 90% (Aprox. 2 minutes remaining)","message");
                var percentval = 90;
                progress(percentval);
                soil_process(data);
            }
        });
    };
    soil_process = function(data) {
        var sub_soil = ajax_update_database_with_file("soil",data); //Submitting the data through the ajax function, see main.js for the helper function.
        sub_soil.done(function(return_data){ //Reset the form once the data is added successfully
            if("soil" in return_data){
                addInfoMessage("Copying/Moving Files....................Overall Job Status: 95% (Less than a minute remaining)","message");
                var percentval = 95;
                progress(percentval);
                cleanup_process(data);
            }
        });
    };
    cleanup_process = function(data) {
        var sub_file_cleanup = ajax_update_database_with_file("cleanup",data); //Submitting the data through the ajax function, see main.js for the helper function.
        sub_file_cleanup.done(function(return_data){ //Reset the form once the data is added successfully
            if("cleanup" in return_data){
                addInfoMessage("Updating Database....................Overall Job Status: 99% (Less than a minute remaining)","message");
                var percentval = 99;
                progress(percentval);
                update_db_process(data);
            }
        });
    };

    update_db_process = function(data) {
        var sub_update = ajax_update_database_with_file("update",data); //Submitting the data through the ajax function, see main.js for the helper function.
        sub_update.done(function(return_data){ //Reset the form once the data is added successfully
            if("success" in return_data){
                submit_button.html(submit_button_html);
                reset_form(return_data);
            }
        });
    };


    add_region = function(){
        reset_alert(); //Reset the alerts
//        progress();
        var region_name = $region_input.val();
        var thredds = $("#thredds-select option:selected").val();
        var shapefiles = $("#shp-upload-input")[0].files;

        if (/[^a-zA-Z0-9 ]/g.test(region_name) == true){
            addErrorMessage("Region Name cannot have special characters. Please use numbers and letters!");
            return false;
        }else{
            reset_alert();
        }
        if(region_name == ""){
            addErrorMessage("Region Name cannot be empty!");
            return false;
        }else{
            reset_alert();
        }
        if($shp_input.val() == ""){
            addErrorMessage("Region Shape File cannot be empty!");
            return false;
        }else{
            reset_alert();
        }



        //Preparing data to be submitted via AJAX POST request
        var data = new FormData();
        data.append("region_name",region_name);
        data.append("thredds",thredds);
        for(var i=0;i < shapefiles.length;i++){
            data.append("shapefile",shapefiles[i]);
        }

        addInfoMessage("Adding Region. Please wait...","message");
        var submit_button = $("#submit-add-region");
        var submit_button_html = submit_button.html();
        submit_button.text('Submitting ...');


        initial_sub_process(data);
//        jpl_tot_process(data);
//        jpl_gw_process(data);
//        csr_tot_process(data);
//        csr_gw_process(data);
//        gfz_tot_process(data);
//        gfz_gw_process(data);
//        avg_tot_process(data);
//        avg_gw_process(data);
//        sw_process(data);
//        soil_process(data);
//        cleanup_process(data);
//        update_db_process(data);





//        var xhr = ajax_update_database_with_file("submit",data); //Submitting the data through the ajax function, see main.js for the helper function.
//        xhr.done(function(return_data){ //Reset the form once the data is added successfully
//            if("success" in return_data){
//                submit_button.html(submit_button_html);
//                reset_form(return_data);
////                hide_progress_modal();
//            }
//        });

    };
    $("#submit-add-region").click(add_region);

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
