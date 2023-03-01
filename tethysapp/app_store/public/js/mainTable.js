var $table = $("#mainAppsTable")

const keyLookup = {
  keywords: "Tags",
  description: "Description",
  license: "License",
  author_email: "App Developer Email"
}

function getResourceValue(key, index, apps) {
  if (apps) {
    if (apps[index]) {
      let app = apps[index]
      if (key in app) {
        return app[key]
      }
      if (key in app["metadata"]) {
        return app["metadata"][key]
      }
    }
  }
}

function getResourceValueByName(key, name, apps) {
  if (apps) {
    let currentResource = apps.filter((resource) => resource.name == name)
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

function getHtmlElementIfExists(key, index, apps) {
  let val = getResourceValue(key, index, apps)
  if (val) {
    return `<li><strong>${keyLookup[key]}</strong>: ${val}</li>`
  }
}

function detailFormatter(index, row) {
  var html = ["<ul>"]
  Object.keys(keyLookup).forEach((key) =>
    html.push(getHtmlElementIfExists(key, index, availableApps))
  )
  html.push("</ul>")
  return html.join("")
}

function detailFormatterInstalledApps(index, row) {
  var html = ["<ul>"]
  Object.keys(keyLookup).forEach((key) =>
    html.push(getHtmlElementIfExists(key, index, installedApps))
  )
  html.push("</ul>")
  return html.join("")
}

function operateFormatter(value, row, index) {

  if (
    typeof value != 'object' &&
    !Array.isArray(value) &&
    value !== null
  ){
    return [
      '<a class="install button-spaced" href="javascript:void(0)" title="Install">',
      `<button type="button" class="btn btn-info btn-outline-secondary btn-xs">Install</button>`,
      "</a>",
      '<a class="github button-spaced" href="javascript:void(0)" title="Github">',
      `<button type="button" class="btn btn-primary btn-outline-secondary btn-xs">Github</button>`,
      "</a>"
    ].join("")
  }
  else{
    var object_row = value;
    var html = ''
    for (const [key, value2] of Object.entries(object_row)) {

      html += `<div class="labels_container"> <p class="btn btn-outline-secondary btn-xs"> ${key}</p>
        <p>
          <a class="install button-spaced" href="javascript:void(0)" title="Install">
            <button type="button" class="btn btn-info btn-outline-secondary btn-xs">Install</button>
          </a>
          <a class="github button-spaced" href="javascript:void(0)" title="Github">
            <button type="button" class="btn btn-primary btn-outline-secondary btn-xs">Github</button>
          </a>
        </p>
      </div>`
      // html.push(`<div class="labels_container"> <p class="btn btn-info btn-outline-secondary btn-xs"> ${key}</p>`);
      // var second_part =['<p><a class="install button-spaced" href="javascript:void(0)" title="Install">',
      // `<button type="button" class="btn btn-info btn-outline-secondary btn-xs">Install</button>`,
      // "</a>",
      // '<a class="github button-spaced" href="javascript:void(0)" title="Github">',
      // `<button type="button" class="btn btn-primary btn-outline-secondary btn-xs">Github</button>`,
      // "</a>", 
      // `</p></div>`]
      // html.concat(second_part);
    } 
    // return html.join("")
    return html

  }

}

function operateFormatter2(value, row, index) {
  let buttons = [
    '<a class="uninstall button-spaced" href="javascript:void(0)" title="Uninstall">',
    `<button type="button" class="btn btn-info btn-warning btn-xs">Uninstall</button>`,
    "</a>"
    // '<a class="reconfigure button-spaced" href="javascript:void(0)" title="Configure">',
    // `<button type="button" class="btn btn-info btn-outline-secondary btn-xs">Configure</button>`,
    // "</a>"
  ]

  if (row.updateAvailable) {
    buttons.push(
      `<a class="update button-spaced" href="javascript:void(0)" title="Update"><button type="button" class="btn btn-primary btn-success btn-xs">Update</button></a>`
    )
  }

  return buttons.join("")
}

function fieldsFormatter(value, row, index){
  // console.log(value)
  if (
    typeof value != 'object' &&
    !Array.isArray(value) &&
    value !== null
  ) {
    return value

  }
  else{
    if ("author" in value){
      return value.author
    }
    else{
      var html = '<div class="multiple_stores_labels">'
      var object_row = value
      // console.log(object_row)
      for (const [key, value2] of Object.entries(object_row)) {
        if (
          typeof value2 != 'object' &&
          !Array.isArray(value2) &&
          value2 !== null
        ){
          html += `<div class="labels_container"> <p class="btn btn-outline-secondary btn-xs"> ${key} </p> <p>${value2}</p></div>`
        }
        else{
          if(value2.author != ""){
            html += `<div class="labels_container"> <p class="btn btn-outline-secondary btn-xs"> ${key} </p> <p>${value2.author}</p></div>`
          }
          else{
            html += `<div class="labels_container"> <p class="btn  btn-outline-secondary btn-xs"> ${key} </p> No Data Provided</p></div>`
          }

        }
      }
      html += '</div>'
    }

  }
  return html

}

function writeTethysPlatformCompatibility(e, row) {
  let appList = $(e.target).attr("class").includes("incompatible-app") ? incompatibleApps : availableApps
  // Get the currently selected app
  let appName = getResourceValueByName("name", row.name, appList)
  // Get the currently selected version
  let selectedVersion = $("#versions option:selected").val()
  // Get the compatibility for that version
  let tethysCompatibility = updateTethysPlatformCompatibility(appName, selectedVersion, appList)
}

window.operateEvents = {
  "click .install": function(e, value, row, index) {
    $("#mainCancel").show()

    let n_div = $("#notification")
    let n_content = $("#notification .lead")
    let isUsingIncompatible = $(e.target).attr("class").includes("incompatible-app")
    let appList = isUsingIncompatible ? incompatibleApps : availableApps
    //let appList = $(e.target).attr("class").includes("incompatible-app") ? incompatibleApps : availableApps
    n_content.empty()
    n_div.modal({ backdrop: "static", keyboard: false })
    n_div.modal('show')
    $("#goToAppButton").hide()
    notifCount = 0
    // Setup Versions
    let appName = getResourceValueByName("name", row.name, appList)
    $("#installingAppName").text(appName)
    installData["name"] = appName
    let versionHTML = getVersionsHTML(appName, appList)
    n_content.append(htmlHelpers.versions(appName, isUsingIncompatible))
    n_content.find("#selectVersion").append(versionHTML)
    $("#versions").select2()
    writeTethysPlatformCompatibility(e, row)
  },

  //$('#versions').on('select2:select', function (e, _, row, _) {
  //"click .versions": function (e, _, row, _) {
  //  writeTethysPlatformCompatibility(e, row)
  //},

  "click .github": function(e, value, row, index) {
    let githubURL = getResourceValueByName("dev_url", row.name, availableApps)
    if (githubURL) window.open(githubURL, "_blank")
  },

  "click .uninstall": function(e, value, row, index) {
    $("#uninstallingAppNotice").html(
      `Are you sure you would like to uninstall <strong>${
        row["name"]
      }</strong> app from your Tethys Portal? 
      \n This will remove all associated files and data stored in any linked persistent stores.`
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
    $("#uninstall-app-modal").modal("show")
  },

  "click .update": function(e, value, row, index) {
    let n_content = $("#update-notices .lead")
    // Find The installed App's version
    let installedApp = installedApps.find((app) => app.name == row["name"])
    $("#current-version-update").html(installedApp.installedVersion)
    $("#latest-version-update").html(installedApp.latestVersion)
    $("#update-app-notice").html(
      `Are you sure you would like to update the <strong>${
        row["name"]
      }</strong> app to version ${installedApp.latestVersion}? `
    )
    updateData = {
      name: row["name"],
      version: installedApp.latestVersion
    }
    $("#update-app-notice").show()
    $("#done-update-button").hide()

    $("#yes-update").show()
    $("#no-update").show()
    $("#update-processing-label").empty()
    $("#update-notices").empty()
    $("#update-app-modal").modal({ backdrop: "static", keyboard: false, })
    $("#update-app-modal").modal("show")
  }
}

function initMainTables() {
  $("#tethysPlatformVersionHeader").text("Tethys Platform Version " + tethysVersion)
  $("#installedAppsTable").bootstrapTable("destroy")

  $("#installedAppsTable").bootstrapTable({ data: installedApps })
  $("#mainAppsTable").bootstrapTable("destroy")
  $("#mainAppsTable").bootstrapTable({ data: availableApps })
  $("#incompatibleAppsTable").bootstrapTable("destroy")

  $("#incompatibleAppsTable").bootstrapTable({ data: incompatibleApps })
  $("#incompatibleAppsTable").find(".install>button").removeClass("btn-info btn-outline-secondary")
  $("#incompatibleAppsTable").find(".install>button").addClass("incompatible-app btn-danger")
  $(".main-app-list").removeClass("hidden")
  $(".installed-app-list").removeClass("hidden")
}
