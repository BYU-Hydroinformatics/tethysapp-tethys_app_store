// HTML Helpers File

const htmlHelpers = {}

htmlHelpers.versions = (installURL) => {
    return `<div>Which version would you like to install: 
                    <div id="selectVersion" style="display: inline-block;"></div>
                    <a class="btn btn-primary" onclick="startInstall('${installURL}')"> Go </a>
                </div>`
}

htmlHelpers.getServicesHTML = (options, service_name) => {
    let sel = document.createElement("select"),
        options_str = ""

    sel.name = `${service_name}_options`
    sel.id = `${service_name}_options`

    options.forEach(function(option) {
        options_str += `<option value='${option.id}'>${option.name}</option>`
    })

    sel.innerHTML = options_str
    return sel
}

htmlHelpers.getServiceCard = (settingName, service) => {
    let optionsElement = ""

    if (service.options.length > 0) {
        optionsElement += `<p>We found ${service.options.length} existing service${
            service.options.length > 1 ? "s" : ""
        }: ${htmlHelpers.getServicesHTML(service.options, service.name).outerHTML}</p>
                        <input id="servicesToConfigureCount" hidden value="${
                            service.options.length
                        }" />
                        `
    }

    return `<div class="card card-default">
                <div class="card-header">${settingName}: ${service.name}</div>
                <div class="card-body">
                    <p>${service.description}</p>
                    ${optionsElement}
                    <button class="btn btn-primary" id="${
                        service.name
                    }_useExisting">Use Selected Service</button>
                    <button class="btn btn-success" style="float: right" id="${
                        service.name
                    }_createNew">Create New Service</button>
                </div>
                <div class="card-footer ">
                    <div id="${service.name}_loaderImage" hidden="">
                        Loading...
                        ${$("#notification .modal-footer")
                            .find("img")
                            .html()}
                    </div>
                    <div id="${service.name}_successMessage" hidden="">
                        Service Configuration Completed
                    </div>
                </div>
            </div>`
}
