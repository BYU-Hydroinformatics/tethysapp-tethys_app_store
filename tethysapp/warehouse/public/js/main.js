// Some Constant Vars being used across the script
// Probably need a better way to manage this state though
// @TODO : Fix This global variable
var currentServicesList = []
var installRunning = false
var installData = {}
// End Vars
const settingsHelper = {
    processCustomSettings: (settingsData, n_content, completeMessage, ws) => {
        resetInstallStatus()
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

const createNewService = (settingType) => {
    let serviceURLPart = serviceLookup[settingType]
    let url = `/admin/tethys_services/${serviceURLPart}/add/?_to_field=id&_popup=1&type=${settingType}`
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

$(document).ready(function() {
    initMainTable()
    // Hide the nav
    $("#app-content-wrapper").toggleClass("show-nav")

    let n_div = $("#notification")
    let n_content = $("#notification .lead")
    hideLoader()
    let protocol = "ws"
    if (location.protocol === "https:") {
        protocol = "wss"
    }
    let ws_url = `${protocol}://${window.location.host}`
    let app_path = warehouseHomeUrl.replace("/apps", "")
    ws_url = `${ws_url}${app_path}install/notifications/ws/`
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

    $('a[id^="app_button_"]').click(function() {
        n_content.empty()
        n_div.modal()
        notifCount = 0
        // Setup Versions

        installData["name"] = $(this).data("app-name")
        let versionHTML = getVersionsHTML($(this).data("app-name"), resources)
        n_content.append(htmlHelpers.versions($(this).data("app-name")))
        n_content.find("#selectVersion").append(versionHTML)
        $("#versions").select2()
    })

    $("#skipServicesButton").click(() => {
        // Service Configuration skipped.
        sendNotification("Services Setup Skipped", n_content)
        sendNotification("install_complete", n_content)
    })
})
