// Some Constant Vars being used across the script
// Probably need a better way to manage this state though
// @TODO : Fix This global variable
var currentServicesList = []
var installRunning = false
var installData = {}
var uninstallData = {}
var uninstallRunning = false
var availableApps = {}
var installedApps = {}
var updateData = {}
var tethysVersion = ""
var storesDataList = []
// End Vars
const settingsHelper = {
    processCustomSettings: (settingsData, n_content, completeMessage, ws) => {
        if (settingsData) {
            if (settingsData.length > 0) {
                $("#skipConfigButton").click(function() {
                    ws.send(
                        JSON.stringify({
                            data: {
                                app_py_path: completeMessage["app_py_path"],
                                skip: true
                            },
                            type: completeMessage.returnMethod
                        })
                    )
                })
                $("#custom-settings-container").empty()

                $("#custom-settings-modal").modal("show")
                $("#custom-settings-container").prepend(`<div>
                    <p>We found ${settingsData.length} custom setting${
                    settingsData.length > 1 ? "s" : ""
                }    
                    </p>
                    </div>
                    `)
                $("#custom-settings-container").append("<form></form>")
                let formDataElement = $("#custom-settings-container").children("form")
                settingsData.forEach((setting) => {
                    let defaultValue = setting.default ? setting.default : ""
                    let newElement = `
                    <div class="form-group">
                        <label for="${setting.name}">${setting.name}</label>
                        <input type="text" class="form-control" id="${setting.name}" value="${defaultValue}">
                        <p class="help-block">${setting.description}</p>
                    </div>`
                    formDataElement.append(newElement)
                })

                formDataElement.append(
                    `<button type="submit" class="btn btn-success">Submit</button>`
                )
                formDataElement.submit(function(event) {
                    event.preventDefault()
                    let formData = { settings: {} }
                    if ("app_py_path" in completeMessage) {
                        formData["app_py_path"] = completeMessage["app_py_path"]
                    }
                    $("#custom-settings-container")
                        .children("form")
                        .find(".form-control")
                        .each(function() {
                            formData.settings[$(this).attr("id")] = $(this).val()
                        })

                    ws.send(
                        JSON.stringify({
                            data: formData,
                            type: completeMessage.returnMethod
                        })
                    )
                })
            } else {
                ws.send(
                    JSON.stringify({
                        data: {
                            app_py_path: completeMessage["app_py_path"],
                            skip: true,
                            noneFound: true
                        },
                        type: completeMessage.returnMethod
                    })
                )
            }
        } else {
            sendNotification("No Custom Settings found to process", n_content)
        }
    },
    customSettingConfigComplete: (settingsData, n_content, completeMessage, ws) => {
        $("#custom-settings-modal").modal("hide")
    },
    getSettingName: (settingType) => {
        const settingMap = {
            spatial: "Spatial Dataset Service",
            persistent: "Persistent Store Service",
            dataset: "Dataset Service",
            wps: "Web Processing Services"
        }
        if (settingType in settingMap) {
            return settingMap[settingType]
        } else {
            console.log("Error: Could not find setting for settingtype: ", settingType)
            return ""
        }
    },
    processServices: (servicesData, n_content, completeMessage, ws) => {
        // Check if there are any services to configure. Otherwise move on to next step
        if (servicesData) {
            if (servicesData.length > 0) {
                currentServicesList = servicesData
                $("#services-modal").modal("show")
                $("#services-container").empty()
                $("#services-container").prepend(`<div>
                    <input id="servicesToConfigureCount" hidden value="${
                        servicesData.length
                    }" />
                    <p>We found ${servicesData.length} service configuration${
                    servicesData.length > 1 ? "s" : ""
                }    
                    </p>
                    </div>
                    `)
                servicesData.forEach((service) => {
                    let settingName = settingsHelper.getSettingName(service.service_type)

                    let newElement = htmlHelpers.getServiceCard(settingName, service)
                    $("#services-container").append(newElement)
                    $(`#${service.name}_useExisting`).click(function() {
                        $(`#${service.name}_loaderImage`).show()
                        // Send WS request to set this.

                        ws.send(
                            JSON.stringify({
                                data: {
                                    app_py_path: completeMessage["app_py_path"],
                                    service_name: service.name,
                                    service_type: service.service_type,
                                    setting_type: service.setting_type,
                                    app_name: completeMessage.current_app_name,
                                    service_id: $(`#${service.name}_options`).val()
                                },
                                type: completeMessage.returnMethod
                            })
                        )
                    })
                    $(`#${service.name}_createNew`).click(() =>
                        createNewService(service.service_type)
                    )
                })
            } else {
                sendNotification("No Services found to process", n_content)
                sendNotification("install_complete", n_content)
            }
        } else {
            sendNotification("No Services found to process", n_content)
            sendNotification("install_complete", n_content)
        }
    },
    serviceConfigComplete: (data, n_content, completeMessage, ws) => {
        // Assuming Successfull configuration for now
        // @TODO : Allow for error reporting and re attempts

        // Find Service and show success
        let serviceName = data.serviceName
        $(`#${serviceName}_loaderImage`).hide()
        $(`#${serviceName}_successMessage`).show(400)
        $(`#${serviceName}_optionsContainer`).hide()

        // Check if there are more services to configure, else enable finish button
        if (parseInt($(`#servicesToConfigureCount`).val()) == 1) {
            // We are done
            $(`#finishServicesButton`).prop("disabled", false)
            $("#services-modal").modal("hide")
            sendNotification("install_complete", n_content)
        } else {
            $(`#servicesToConfigureCount`).val(
                parseInt($(`#servicesToConfigureCount`).val()) - 1
            )
        }
    },
    updateServiceListing: (data, n_content, completeMessage, ws) => {
        let filteredServices = currentServicesList.filter(
            (service) => service.service_type == data.settingType
        )
        filteredServices.forEach((service) => {
            if (data.newOptions.length > 0) {
                $(`#${service.name}_optionsList`).replaceWith(
                    htmlHelpers.getServicesHTML(data.newOptions, service.name)
                )
                $(`#${service.name}_useExisting`).removeAttr("disabled")
            }
        })
    }
}

// Converts the list of versions into an HTML dropdown for selection
const getVersionsHTML = (selectedApp, allResources) => {
    let app = allResources.filter((resource) => resource.name == selectedApp)
    if (app.length > 0) {
        let versions = app[0].metadata.versions.reverse()

        let sel = document.createElement("select"),
            options_str = ""

        sel.name = "versions"
        sel.id = "versions"

        versions.forEach(function(version) {
            options_str += `<option value='${version}'>${version}</option>`
        })

        sel.innerHTML = options_str
        return sel
    } else {
        console.log("No App found with that name. Check input params")
    }
}

const updateTethysPlatformCompatibility = (selectedApp, selectedVersion, allResources) => {
    let app = allResources.filter((resource) => resource.name == selectedApp)
    let platform_compatibility = '<=3.4.4'
    if (app.length > 0) {
        let keys = Object.keys(app[0].metadata.compatibility)
        if (keys.includes(selectedVersion)) {
            platform_compatibility = app[0].metadata.compatibility[selectedVersion]
        }
        
    } else {
        console.log("No App found with that name and version. Check input params")
    }
    
    $("#tethysPlatformVersion").text('Tethys Platform Compatibility: ' + platform_compatibility)
}

const startInstall = (appName) => {
    showLoader()
    let version = $("#versions").select2("data")[0].text
    installRunning = true
    installData["version"] = version

    notification_ws.send(
        JSON.stringify({
            data: {
                name: appName,
                version
            },
            type: `begin_install`
        })
    )
}

const updateTethysPlatformVersion = (appName, isUsingIncompatible) => {
    let selectedVersion = $("#versions").select2("data")[0].text
    let appList = isUsingIncompatible ? incompatibleApps : availableApps
    updateTethysPlatformCompatibility(appName, selectedVersion, appList)
}

const createNewService = (settingType) => {
    let serviceURLPart = serviceLookup[settingType]
    let baseURL = warehouseHomeUrl.replace("/apps/warehouse", "/admin")
    let url = `${baseURL}tethys_services/${serviceURLPart}/add/?_to_field=id&_popup=1&type=${settingType}`
    let newWindow = window.open(
        url,
        "_blank",
        "location=yes,height=570,width=600,scrollbars=yes,status=yes"
    )
}

// This function is called when add new service window is closed by Django
function dismissAddRelatedObjectPopup(win, newId, newRepr) {
    win.close()
    notification_ws.send(
        JSON.stringify({
            data: {
                settingType: getParameterByName("type", win.location.href)
            },
            type: `getServiceList`
        })
    )
}

const getRepoForAdd = () => {
    let githubURL = $("#githubURL").val()
    if (githubURL) {
        // Disable UI Elements and showloading
        $("#loaderEllipsis").show()
        $("#fetchRepoButton").prop("disabled", true)
        $("#githubURL").prop("disabled", true)
        $("#loadingTextAppSubmit").text("Please wait. Fetching GitHub Repo")

        // notification_ws.send(
        //     JSON.stringify({
        //         data: {
        //             url: githubURL
        //         },
        //         type: `validate_git_repo`
        //     })
        // )

        notification_ws.send(
            JSON.stringify({
                data: {
                    url: githubURL
                },
                type: `pull_git_repo`
            })
        )
    } else {
        //@TODO: Show error here that url is missing.
    }
}

const uninstall = () => {
    // Hide Elements
    $("#uninstallingAppNotice").hide()
    $("#yesUninstall").hide()
    $("#noUninstall").hide()
    $("#uninstallLoaderEllipsis").show()
    $("#uninstall_processing_label").text(`Uninstalling: ${uninstallData.name}`)
    notification_ws.send(
        JSON.stringify({
            data: uninstallData,
            type: `uninstall_app`
        })
    )
}

const update = () => {
    // Hide Elements
    $("#update-app-notice").hide()
    $("#yes-update").hide()
    $("#no-update").hide()
    $("#pre-update-notice").hide()
    $("#update-loader").show()
    $("#update-processing-label").text(
        `Updating: ${updateData.name} to version ${updateData.version}`
    )
    notification_ws.send(
        JSON.stringify({
            data: updateData,
            type: `update_app`
        })
    )
}

const get_resources_for_channel= (default_store) => {

    $.ajax({
        url: `${warehouseHomeUrl}get_resources`,
        dataType: "json",
        data: default_store
    })
        .done(function(data) {
            availableApps = data.availableApps
            installedApps = data.installedApps
            incompatibleApps = data.incompatibleApps
            tethysVersion = data.tethysVersion
            // storesDataList = data.storesDataList
            // console.log(storesData)
            $("#mainAppLoader").hide()
            initMainTables()
            // create_content_for_channel(storesDataList)
        })
        .fail(function(err) {
            console.log(err)
            location.reload()
        })

}



$(document).ready(function() {
    // Hide the nav
    $("#app-content-wrapper").removeClass('show-nav');
    $(".toggle-nav").removeClass('toggle-nav');
    // create ajax function to get the stores now and call the get_resources for each one of the stores, you will need to send channel as a parameter :/
    storesDataList = []
    $.ajax({
        url: `${warehouseHomeUrl}get_available_stores`,
        dataType: "json"
    }).done(function(data){
        storesDataList = data['stores']
        console.log(storesDataList)

        var default_store = storesDataList.filter((x) => x.default == true)[0]
        console.log(default_store)
        // console.log("current_channel", default_conda_channel)
        // Get Main Data and load the table
        storesDataList.forEach(function(store_single){
            $(`#pills-${store_single['conda_channel']}-tab`).click(function(){
                console.log(store_single)
                get_resources_for_channel(store_single)

            })
        })
        
        get_resources_for_channel(default_store)

        // $.ajax({
        //     url: `${warehouseHomeUrl}get_resources`,
        //     dataType: "json",
        //     data: default_store
        // })
        //     .done(function(data) {
        //         availableApps = data.availableApps
        //         installedApps = data.installedApps
        //         incompatibleApps = data.incompatibleApps
        //         tethysVersion = data.tethysVersion
        //         // storesDataList = data.storesDataList
        //         // console.log(storesData)
        //         $("#mainAppLoader").hide()
        //         initMainTables()
        //         // create_content_for_channel(storesDataList)
        //     })
        //     .fail(function(err) {
        //         console.log(err)
        //         location.reload()
        //     })


    }).fail(function(err) {
        storesDataList = []
        console.log(err)
    })
    // console.log(storesDataList)


    let n_div = $("#notification")
    let n_content = $("#notification .lead")
    hideLoader()
    let protocol = "ws"
    if (location.protocol === "https:") {
        protocol = "wss"
    }
    let ws_url = `${protocol}://${window.location.host}`
    ws_url = `${ws_url}${warehouseHomeUrl}install/notifications/ws/`
    startWS(ws_url, n_content)

    $("#serverRefresh").click(function() {
        setServerOffline()
        notification_ws.send(
            JSON.stringify({
                data: {},
                type: `restart_server`
            })
        )
    })

    $("#skipServicesButton").click(() => {
        // Service Configuration skipped.
        sendNotification("Services Setup Skipped", n_content)
        sendNotification("install_complete", n_content)
    })

    $("#doneInstallButton").click(() => reloadCacheRefresh())
    $("#doneUninstallButton").click(() => reloadCacheRefresh())
    $("#done-update-button").click(() => reloadCacheRefresh())
})
