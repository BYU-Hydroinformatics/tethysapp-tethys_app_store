var $table = $("#mainAppsTable")

const keyLookup = {
  keywords: "Tags",
  description: "Description",
  license: "License",
  author_email: "App Developer Email"
}

function getResourceValue(key, index) {
  if (resources) {
    if (resources[index]) {
      let app = resources[index]
      if (key in app) {
        return app[key]
      }
      if (key in app["metadata"]) {
        return app["metadata"][key]
      }
    }
  }
}

function getResourceValueByName(key, name) {
  if (resources) {
    let currentResource = resources.filter((resource) => resource.name == name)
    if (currentResource.length > 0) {
      let app = currentResource[0]
      if (key in app) {
        return app[key]
      }
      if (key in app["metadata"]) {
        return app["metadata"][key]
      }
    }
  }
}

function getHtmlElementIfExists(key, index) {
  let val = getResourceValue(key, index)
  if (val) {
    return `<li><strong>${keyLookup[key]}</strong>: ${val}</li>`
  }
}

function detailFormatter(index, row) {
  var html = ["<ul>"]
  Object.keys(keyLookup).forEach((key) => html.push(getHtmlElementIfExists(key, index)))
  html.push("</ul>")
  return html.join("")
}

function operateFormatter(value, row, index) {
  return [
    '<a class="install button-spaced" href="javascript:void(0)" title="Install">',
    `<button type="button" class="btn btn-info btn-default btn-xs">Install</button>`,
    "</a>",
    '<a class="github button-spaced" href="javascript:void(0)" title="Github">',
    `<button type="button" class="btn btn-primary btn-default btn-xs">Github</button>`,
    "</a>"
  ].join("")
}

function operateFormatter2(value, row, index) {
  let buttons = [
    '<a class="uninstall button-spaced" href="javascript:void(0)" title="Uninstall">',
    `<button type="button" class="btn btn-info btn-warning btn-xs">Uninstall</button>`,
    "</a>",
    '<a class="reconfigure button-spaced" href="javascript:void(0)" title="Configure">',
    `<button type="button" class="btn btn-info btn-default btn-xs">Configure</button>`,
    "</a>"
  ]

  if (row.updateAvailable) {
    buttons.push(
      `<a class="update button-spaced" href="javascript:void(0)" title="Update">
      <button type="button" class="btn btn-primary btn-success btn-xs">Update</button>
      </a>`
    )
  }

  return buttons.join("")
}

window.operateEvents = {
  "click .install": function(e, value, row, index) {
    $("#mainCancel").show()

    let n_div = $("#notification")
    let n_content = $("#notification .lead")
    n_content.empty()
    n_div.modal({ backdrop: "static", keyboard: false })
    $("#goToAppButton").hide()
    notifCount = 0
    // Setup Versions

    let appName = getResourceValueByName("name", row[0])
    $("#installingAppName").text(appName)
    installData["name"] = appName
    let versionHTML = getVersionsHTML(appName, resources)
    n_content.append(htmlHelpers.versions(appName))
    n_content.find("#selectVersion").append(versionHTML)
    $("#versions").select2()
  },

  "click .github": function(e, value, row, index) {
    let githubURL = getResourceValueByName("dev_url", row[0])
    if (githubURL) window.open(githubURL, "_blank")
  },

  "click .uninstall": function(e, value, row, index) {
    $("#uninstallingAppNotice").html(
      `Are you sure you would like to uninstall <strong>${
        row["name"]
      }</strong> app from your Tethys Portal?`
    )
    uninstallData = {
      name: row["name"]
    }
    $("#uninstallingAppNotice").show()
    $("#doneUninstallButton").hide()

    $("#yesUninstall").show()
    $("#noUninstall").show()
    $("#uninstall_processing_label").empty()
    $("#uninstallNotices").empty()
    $("#uninstall-app-modal").modal({ backdrop: "static", keyboard: false })
  }
}

function initMainTable() {
  var $table = $("#installedAppsTable")
  $table.bootstrapTable({ data: installedApps })
}
