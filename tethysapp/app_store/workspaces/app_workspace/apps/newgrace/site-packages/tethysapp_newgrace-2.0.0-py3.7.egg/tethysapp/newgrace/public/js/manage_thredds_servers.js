/*****************************************************************************
 * FILE:    GRACE MANAGE GEOSERVERS
 * DATE:    19 MAY 2017
 * AUTHOR: Sarva Pulla
 * COPYRIGHT: (c) Brigham Young University 2017
 * LICENSE: BSD 2-Clause
 *****************************************************************************/


/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var GRACE_MANAGE_GEOSERVERS = (function() {
    // Wrap the library in a package function
    "use strict"; // And enable strict mode for this library

    /************************************************************************
    *                      MODULE LEVEL / GLOBAL VARIABLES
    *************************************************************************/
    var m_uploading_data, m_results_per_page;

    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/
    var initializeTableFunctions, getTablePage, displayResultsText;


    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/

    m_results_per_page = 5;

    initializeTableFunctions = function() {

        //handle the submit update event
        $('.submit-update-thredds-server').off().click(function(){
            //scroll back to top
            window.scrollTo(0,0);
            //clear messages
            $('#message').addClass('hidden');
            $('#message').empty()
                .addClass('hidden')
                .removeClass('alert-success')
                .removeClass('alert-info')
                .removeClass('alert-warning')
                .removeClass('alert-danger');

            //check data store input
            var safe_to_submit = {val: true, error:""};
            var parent_row = $(this).parent().parent().parent();
            var thredds_server_id = parent_row.find('.thredds-server-id').text();
            var thredds_server_name = checkTableCellInputWithError(parent_row.find('.thredds-server-name'),safe_to_submit);
            var thredds_server_url = checkTableCellInputWithError(parent_row.find('.thredds-server-url'),safe_to_submit);
            var thredds_server_username = checkTableCellInputWithError(parent_row.find('.thredds-server-username'),safe_to_submit);
            var thredds_server_password = checkTableCellInputWithError(parent_row.find('.thredds-server-password-input'),safe_to_submit);

            var data = {
                    thredds_server_id: thredds_server_id,
                    thredds_server_name: thredds_server_name,
                    thredds_server_url: thredds_server_url,
                    thredds_server_username: thredds_server_username,
                    thredds_server_password: thredds_server_password,
                    };

            //update database
            var xhr = submitRowData($(this), data, safe_to_submit);
            if (xhr != null) {
                xhr.done(function (data) {
                    if ('success' in data) {
                        addSuccessMessage("Thredds Server Update Success!");
                    }
                });
            }
        });

        //handle the submit delete event
        $('.submit-delete-thredds-server').click(function(){
        var data = {
            thredds_server_id: $(this).parent().parent().parent()
                                .find('.thredds-server-id').text()
                };
            //update database
            var xhr = deleteRowData($(this), data);
            if (xhr != null) {
                xhr.done(function (data) {
                    if ('success' in data) {
                        addSuccessMessage("Thredds Server Successfully Deleted!");
                        var num_thredds_servers_data = $('#manage_thredds_servers_table').data('num_thredds_servers');
                        var page = parseInt($('#manage_thredds_servers_table').data('page'));
                        $('#manage_thredds_servers_table').data('num_thredds_servers', Math.max(0, parseInt(num_thredds_servers_data) - 1));
                        if (parseInt($('#manage_thredds_servers_table').data('num_thredds_servers')) <= m_results_per_page * page) {
                            $('#manage_thredds_servers_table').data('page', Math.max(0, page - 1));
                        }
                        getTablePage();
                    }
                });
            }
        });

        displayResultsText();
        if (m_results_per_page >= $('#manage_thredds_servers_table').data('num_thredds_servers')) {
            $('[name="prev_button"]').addClass('hidden');
            $('[name="next_button"]').addClass('hidden');
        }

        //pagination next and previous button update
        $('[name="prev_button"]').click(function(){
            var page = parseInt($('#manage_thredds_servers_table').data('page'));
            $('#manage_thredds_servers_table').data('page', Math.max(0, page-1));
            getTablePage();
        });
        $('[name="next_button"]').click(function(){
            var page = parseInt($('#manage_thredds_servers_table').data('page'));
            $('#manage_thredds_servers_table').data('page', Math.min(page+1,
                                                Math.floor(parseInt($('#manage_thredds_servers_table').data('num_thredds_servers')) / m_results_per_page - 0.1)));
            getTablePage();
        });
    };


    displayResultsText = function() {
        //dynamically show table results display info text on page
        var page = parseInt($('#manage_thredds_servers_table').data('page'));
        var num_thredds_servers_data = $('#manage_thredds_servers_table').data('num_thredds_servers');
        var display_min;
        if (num_thredds_servers_data == 0){
            display_min = 0
        }
        else{
            display_min = ((page + 1) * m_results_per_page) - (m_results_per_page - 1);
        }
        var display_max = Math.min(num_thredds_servers_data, ((page + 1) * m_results_per_page));
        $('[name="prev_button"]').removeClass('hidden');
        $('[name="next_button"]').removeClass('hidden');
        if (page == 0){
            $('[name="prev_button"]').addClass('hidden');
        } else if (page == Math.floor(num_thredds_servers_data / m_results_per_page - 0.1)) {
            $('[name="next_button"]').addClass('hidden');
        }
        if (num_thredds_servers_data != 0) {
            $('#display-info').append('Displaying thredds servers ' + display_min + ' - ' +
                display_max + ' of ' + num_thredds_servers_data);
        }else {
            $('#display-info').append('No thredds_servers to display' + '<br>To add one, ' +
                'click <a href="../add-thredds-server">here</a>.');
        }
    };

    getTablePage = function() {
        $.ajax({
            url: 'table',
            method: 'GET',
            data: {'page': $('#manage_thredds_servers_table').data('page')},
            success: function(data) {
                $("#manage_thredds_servers_table").html(data);
                initializeTableFunctions();
            }
        });
    };


    /************************************************************************
    *                  INITIALIZATION / CONSTRUCTOR
    *************************************************************************/

    $(function() {
        m_uploading_data = false;
        getTablePage();
    }); //document ready
}()); // End of package wrapper
