// HTML Helpers File

const htmlHelpers = {}

htmlHelpers.versions = (appName, isUsingIncompatible) => {
    return `<div>Which version would you like to install: 
                    <div id="selectVersion" style="display: inline-block; min-width:100px" onchange="updateTethysPlatformVersion('${appName}', '${isUsingIncompatible}')"></div>
                    <a class="btn btn-primary" onclick="startInstall('${appName}')"> Go </a>
                    <br>
                    <br>
                    <div id="tethysPlatformVersion" style="min-width:100px"></div>
                </div>`
}
htmlHelpers.versions_new = (appName,channel, label,version,isUsingIncompatible) => {
    // <div id="selectVersion" style="display: inline-block; min-width:100px" onchange="updateTethysPlatformVersion('${appName}', '${isUsingIncompatible}')"></div>

    return `<div>Start installation: 
                    <a class="btn btn-primary" onclick="startInstall('${appName}','${channel}', '${label}','${version}')"> Start </a>
                    <br>
                    <br>
                    <div id="tethysPlatformVersion" style="min-width:100px"></div>
                </div>`
}


htmlHelpers.getServicesHTML = (options, service_name) => {
    let sel = document.createElement("select"),
        options_str = "",
        completeElement

    sel.name = `${service_name}_options`
    sel.id = `${service_name}_options`

    options.forEach(function(option) {
        options_str += `<option value='${option.id}'>${option.name}</option>`
    })

    sel.innerHTML = options_str

    if (options.length > 0) {
        completeElement = `<p id="${service_name}_optionsList">We found ${
            options.length
        } existing service${options.length > 1 ? "s" : ""}: ${sel.outerHTML}</p>
                        `
    } else {
        completeElement = `<p id="${service_name}_optionsList">No compatible exisiting services found
        <select name="${service_name}_options" id="${service_name}_options" hidden></select></p>
        `
    }
    return completeElement
}

htmlHelpers.getServiceCard = (settingName, service) => {
    let optionsElement = htmlHelpers.getServicesHTML(service.options, service.name)
    let disabledButton = service.options.length < 1 ? "disabled" : ""

    return `<div class="card card-default">
                <div class="card-header">${settingName}: ${service.name}</div>
                <div class="card-body">
                    <p>${service.description}</p>
                    <div id="${service.name}_optionsContainer">
                        ${optionsElement}
                        <button class="btn btn-primary" id="${
                            service.name
                        }_useExisting" ${disabledButton}>Use Selected Service</button>
                        <button class="btn btn-success" style="float: right" id="${
                            service.name
                        }_createNew">Create New Service</button>
                    </div>
                </div>
                <div class="card-footer ">
                    <div id="${service.name}_loaderImage" hidden="">
                        Loading...
                        ${$("#notification .modal-footer")
                            .find("div")
                            .html()}
                    </div>
                    <div id="${service.name}_successMessage" hidden="">
                        Service Configuration Completed
                    </div>
                </div>
            </div>`
}

htmlHelpers.getBranches = (conda_channel,branches) => {
    let sel = `<select  class="form-control add_branch"  name="add_branch" id="${conda_channel}_add_branch">`
    // let sel = `<select  class="form-control add_branch"  name="add_branch" >`

    let options_str = ""

    branches.forEach(
        (branch) => (options_str += `<option value='${branch}'>${branch}</option>`)
    )

    sel = `${sel}${options_str}</select>`

    return `<div class="form-group branches-form">
    <label for="add_branch">Please select the branch you would like to use:</label>${sel}</div>`
}

htmlHelpers.getLabels = (labels) => {
    let sel = `<select  class="form-control"  name="add_label" id="add_label">`
    let options_str = ""

    labels.forEach(
        (label) => (options_str += `<option value='${label}'>${label}</option>`)
    )

    sel = `${sel}${options_str}</select>`

    return `<div class="form-group">
    <label for="add_label">Please select the label you would like to use:</label>${sel}</div>`
}
