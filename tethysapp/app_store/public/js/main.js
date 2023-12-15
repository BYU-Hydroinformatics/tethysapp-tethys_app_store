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

const getVersionsHTML_new = (app,channel,label) => {
    // let app = allResources.filter((resource) => resource.name == selectedApp)
    if (app.hasOwnProperty('name')) {
        // let versions = app[versions].reverse()
        let versions = app['versions'][channel][label].reverse();
        let sel = document.createElement("select"),
            options_str = ""

        sel.name = "versions"
        sel.id = "versions"

        versions.forEach(function(version) {
            options_str += `<option value='${channel}__${label}__${version}'>${version}</option>`
        })

        sel.innerHTML = options_str
        return sel
    } else {
        console.log("No App found with that name. Check input params")
    }
}

const getVersionsHTML_dropdown = (app,checkIfNeeded,isUpdate) => {
    var class_html = 'install';
    if(isUpdate){
        class_html = 'install-update';
    }
    // https://stackoverflow.com/questions/70098157/bootstrap-5-1-3-dropdown-data-bs-boundary-no-longer-works
    // let app = allResources.filter((resource) => resource.name == selectedApp)
    if (app.hasOwnProperty('name') && !checkIfNeeded) {
        var icon_warning = '';
        var color_icon = 'primary';
        if(Object. keys(app['compatibility'][channel][label]).length == 0 ){
          icon_warning = `<i class="bi bi-exclamation-triangle"></i> `
          color_icon = 'danger';
        }
        // let versions = app[versions].reverse()
        let string_dropdown = `<div class="dropdown">`
        string_dropdown += `<a class="custom-label label-color-info label-outline-xs dropdown-toggle install2" href="#" role="button" id="dropdownMenuLink_${app['name']}" data-bs-toggle="dropdown" aria-expanded="false"> <i class="bi bi-plus-lg"></i> Install </a>`
        string_dropdown += `<ul class="dropdown-menu position-fixed" aria-labelledby="dropdownMenuLink_${app['name']}">`
        let versions_obj = app['versions'];

        for (channel in versions_obj){
            string_dropdown += `<li class="dropdown dropend">`;
            string_dropdown +=`<a class="dropdown-item dropdown-toggle" href="#" id="${channel}_${app['name']}}" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">`
            string_dropdown +=`<span class="label_dropdown custom-label label-outline-${labels_style_dict[channel]} label-outline-xs"> <i class="bi bi-shop"></i> ${channel} </span>`;
            string_dropdown += `</a>`
            string_dropdown += `<ul class="dropdown-menu position-fixed" aria-labelledby="${channel}_${app['name']}}">`

            for (label in versions_obj[channel]){
                string_dropdown += `<li class="dropdown dropend">`;
                string_dropdown +=`<a class="dropdown-item dropdown-toggle" href="#" id="${channel}_${label}_${app['name']}}" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">`
                // string_dropdown +=`<span class="store_label custom-label label-outline-${labels_style_dict[channel]} label-outline-xs"> <i class="bi bi-shop"></i> ${channel} </span>`;
                string_dropdown +=`<span class="label_dropdown custom-label label-outline-${labels_style_dict[label]} label-outline-xs"><i class="bi bi-tags"></i>${label}</span>`
                string_dropdown += `</a>`
                string_dropdown += `<ul class="dropdown-menu position-fixed drop_down_scroll" aria-labelledby="${channel}_${label}_${app['name']}}">`
                for (sinlge_version in versions_obj[channel][label]){
                    // string_dropdown += `<li><a class="dropdown-item" href="#">${versions_obj[channel][label][sinlge_version]}</a></li>`
                    string_dropdown +=`<li><a class="${class_html} button-spaced dropdown-item" href="javascript:void(0)" title="Install">
                        <button type="button" id="${channel}__${label}__${versions_obj[channel][label][sinlge_version]}__${app['name']}__install" class="label_dropdown custom-label label-color-${color_icon} label-outline-xs">${versions_obj[channel][label][sinlge_version]}</button>
                    </a></li>`
                }
                string_dropdown += `</ul></li>`;
            }
            string_dropdown += `</ul></li>`;

        }

            string_dropdown += `</ul></div>`;

        return string_dropdown
    } else {
        var string_dropdown = ''
        return string_dropdown
        // console.log("No App found with that name. Check input params")
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
const updateTethysPlatformCompatibility_new = (app, selectedVersion,channel,label) => {
    let platform_compatibility = '<=3.4.4'
    if (app.hasOwnProperty('name')) {
        let compatibility_channel_label_keys = Object.keys(app['compatibility'][channel][label])
        if (compatibility_channel_label_keys.includes(selectedVersion)) {
            platform_compatibility = app['compatibility'][channel][label][selectedVersion]
        }
        
    } else {
        console.log("No App found with that name, store, tag, and version. Check input params")
    }
    
    $("#tethysPlatformVersion").text('Tethys Platform Compatibility: ' + platform_compatibility)
}


// const startInstall = (appName) => {
//     showLoader()
//     let version = $("#versions").select2("data")[0].text
//     installRunning = true
//     installData["version"] = version

//     notification_ws.send(
//         JSON.stringify({
//             data: {
//                 name: appName,
//                 version
//             },
//             type: `begin_install`
//         })
//     )
// }

const startInstall = (appName,channel_app,label_app,current_version) => {
    showLoader()
    // let current_version = $("#versions").select2("data")[0].text
    installRunning = true
    installData["version"] = current_version

    notification_ws.send(
        JSON.stringify({
            data: {
                name: appName,
                channel:channel_app,
                label:label_app,
                version: current_version
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
                    url: githubURL,
                    stores: active_stores
                },
                type: `pull_git_repo_all`
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

    var htmlStr = `<span>`
    htmlStr += `<span class="labels_container" style="display: inline-block;"> `
    htmlStr += `<span class="custom-label label-color-${labels_style_dict[updateData.channel]} label-outline-xs"> <i class="bi bi-shop"></i> ${updateData.channel} </span>`
    htmlStr += `<span class="custom-label label-color-${labels_style_dict[updateData.label]} label-outline-xs"><i class="bi bi-tags"></i> ${updateData.label}</span>`
    htmlStr += `<span class="custom-label label-outline-xs label-color-gray">${updateData.version}</span>`
    htmlStr += `</span>`


    $("#update-processing-label").html(

        `Updating to: ${htmlStr}`
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
            console.log(data)
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


const get_merged_resources = (store) => {

    $.ajax({
        url: `${warehouseHomeUrl}get_merged_resources`,
        dataType: "json",
        data: store
    })
        .done(function(data) {
            
            availableApps = data.availableApps
            installedApps = data.installedApps
            incompatibleApps = data.incompatibleApps
            tethysVersion = data.tethysVersion
            $("#mainAppLoader").hide()
            console.log(data)
            initMainTables()
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
        console.log(data)
        storesDataList = data['stores']
        console.log(storesDataList)
        labels_style_dict = get_color_label_dict(storesDataList)
        create_request_obj(storesDataList)

        let storessMenuHtml = createStoresMenusHtml(storesDataList)
        $("#storeList").html(storessMenuHtml)

        addFunctionalityStores(storesDataList)

        var default_store = storesDataList.filter((x) => x.default == true)[0]
        console.log(default_store)
        active_store = default_store['github_organization']
        var stores_list = []
        // console.log("current_channel", default_conda_channel)
        // Get Main Data and load the table
        storesDataList.forEach(function(store_single){
            stores_list.push(store_single['conda_channel']);
            $(`#pills-${store_single['conda_channel']}-tab`).click(function(){

                active_store = store_single['conda_channel']

                // get_resources_for_channel(store_single)
                // get_merged_resources({'active_store': store_single['conda_channel']})
                get_merged_resources({'active_store':active_store})

            })
        })
        
        $(`#pills-all-tab`).click(function(){
            active_store = "all"
            get_merged_resources({'active_store': active_store})
        })
        console.log(stores_list)
        // get_resources_for_channel(default_store)
        active_store = "all"
        get_merged_resources({'active_store': active_store})
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
    // let new_temp = '/apps/app-store/'
    // ws_url = `${ws_url}${new_temp}install/notifications/ws/`

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
