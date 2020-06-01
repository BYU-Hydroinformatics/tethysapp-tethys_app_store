// Some Constant Vars being used across the script
// Probably need a better way to manage this state though
// @TODO : Fix This global variable
var notifCount = 0
var currentServicesList = []
var notification_ws
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

                $("#custom-settings-modal").modal("show")
                $("#custom-settings-container").prepend(`<div>
                    <p>We found ${settingsData.length} custom setting${
                    settingsData.length > 1 ? "s" : ""
                }    
                    </p>
                    </div>
                    `)
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
                sendNotification("No Custom Settings found to process", n_content)
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

const sendNotification = (message, n_content) => {
    notifCount = notifCount + 1
    let new_element = `<div style="display: none;" id="install_notif_${notifCount}">${message}</div>`
    if (message == "install_complete") {
        hideLoader()
        new_element = `<div style="display: none;" id="install_notif_${notifCount}">Install Complete. Please restart your Tethys instance for changes to take effect. </div>`
    }
    n_content.append(new_element)
    $(`#install_notif_${notifCount}`).show("fast")
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

const hideLoader = () => {
    $("#notification .modal-footer")
        .find("img")
        .hide()
}

const showLoader = () => {
    $("#notification .modal-footer")
        .find("img")
        .show()
}

const startInstall = (appInstallURL) => {
    showLoader()
    let installURL = `${appInstallURL}&version=${$("#versions").select2("data")[0].text}`
    $.get(installURL, function(data) {
        // console.log(data)
    })
}

const createNewService = (settingType) => {
    let url = `/admin/tethys_services/spatialdatasetservice/add/?_to_field=id&_popup=1&type=${settingType}`
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

$(document).ready(function() {
    let n_div = $("#notification")
    let n_content = $("#notification .lead")
    hideLoader()
    notification_ws = new WebSocket(
        "ws://" + window.location.host + "/warehouse/install/notifications/ws/"
    )

    $("#app_button").click(function() {
        n_content.empty()
        n_div.modal()
        notifCount = 0
        // Setup Versions
        let versionHTML = getVersionsHTML($(this).data("app-name"), resources)
        n_content.append(htmlHelpers.versions($(this).data("install-url")))
        n_content.find("#selectVersion").append(versionHTML)
        $("#versions").select2()
    })

    notification_ws.onmessage = function(e) {
        let data = JSON.parse(e.data)
        if (typeof data.message == "string") {
            // It's normal string
            sendNotification(data.message, n_content)
            return false
        } else {
            // Found an object?
            // Check if we have a function to call
            if ("jsHelperFunction" in data.message) {
                settingsHelper[data.message["jsHelperFunction"]](
                    data.message.data,
                    n_content,
                    data.message,
                    notification_ws
                )
            } else {
                console.log("Undefined jsHelperFunction in JSON WebSocket call")
            }
        }
    }
})
