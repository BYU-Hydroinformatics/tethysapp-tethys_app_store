var $table = $("#mainAppsTable")



const keyLookup = {
  keywords: "Tags",
  description: "Description",
  license: "License",
  author_email: "App Developer Email",
  
}


function getResourceValue(key, index, apps) {

  var return_val;
  // return return_val
  if (apps) {
    if (apps[index]) {
      let app = apps[index]
      if (key in app) {
        return_val = app[key]
        return return_val
      }
      if (key in app["metadata"]) {
        return_val = app["metadata"][key]
        return return_val
      }

      else{

        var return_val = ""
        Object.keys(app["metadata"]).forEach(function(storeName){
          if(key in app["metadata"][storeName]){
            var val_attr = app["metadata"][storeName][key]
            if (val_attr){
              return_val += `${val_attr}`
            }
          }
        })
        return return_val
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
      if(name in app["metadata"]){
        if(key in app["metadata"][name]){
          return app["metadata"][name][key]
        }
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
    var index_label_color = 0
    for (const [key, value2] of Object.entries(object_row)) {
      html += `<div class="labels_container"> <p class="store_label btn btn-outline-${label_styles(index_label_color)} btn-xs"> #${key}</p>
        <p class="store_label_val">
          <a class="install button-spaced" href="javascript:void(0)" title="Install">
            <button type="button" class="btn btn-info btn-outline-secondary btn-xs">Install</button>
          </a>
          <a class="github_${key} button-spaced" href="${row['metadata'][key]['dev_url']}" target="_blank" title="Github">
            <button type="button" class="btn btn-primary btn-outline-secondary btn-xs">Github</button>
          </a>
        </p>
      </div>`
      index_label_color += 1;

    } 
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

function mergedFieldsFormatter(value, row, index){
  var html_str = '<div>';
  var wasAdded = false;
  for(channel in value){
    // html_str += `<div class="multiple_stores_labels">`
    for (label in value[channel]){
      if (value[channel][label] !== null && value[channel][label] !== ""){
        if(!wasAdded){
          html_str += `<div class="channels_container"> <div><span class="store_label btn label-outline-${labels_style_dict[channel]} label-outline-xs"> <i class="bi bi-shop"></i> ${channel} </span></div><span class="labels_container"> `;
        }
        html_str += `<div><span class="custom-label label-outline-${labels_style_dict[label]} label-outline-xs"><i class="bi bi-tags"></i> ${label}</span></div><div><span class="custom-label label-outline-xs label-color-gray">${value[channel][label]}</span></div>`
        wasAdded = true
      }
    }
    html_str += `</span></div>`
    wasAdded = false
  }
  return html_str
}
function mergedOperateFormatter(value, row, index){

  var html_str = '<div class="actions_channel_container">';
  for(channel in value){
    html_str += `<div class="channels_container"> <div class="channels_centered"><span class="store_label custom-label label-outline-${labels_style_dict[channel]} label-outline-xs"> <i class="bi bi-shop"></i> ${channel} </span></div><div> `;
    for (label in value[channel]){
      if (value[channel][label] !== null || value[channel][label] !== ""){
        var github_url =  value[channel][label]
        if(github_url == ""){
          var normal_json = row['license'][channel][label];
          var licenseChannnelLabel = JSON.parse(normal_json.replace(/'/g, '"'));
          var github_url = licenseChannnelLabel['dev_url']
        }
        html_str += `<div class="actions_label_container"><div><span class="label_label custom-label label-outline-${labels_style_dict[label]} label-outline-xs"><i class="bi bi-tags"></i>${label}</span></div>
        <span>
          <p class="store_label_val">
            <a class="github_type button-spaced" href="${github_url}" target="_blank" title="Github">
              <button type="button" class="custom-label label-color-info label-outline-xs"><i class="bi bi-github"></i></button>
            </a>
            <a class="install button-spaced" href="javascript:void(0)" title="Install">
              <button type="button" class="custom-label label-color-primary label-outline-xs">Install</button>
            </a>
          </p>
        </span></div>`
      }
    }
    html_str += `</div></div>`
  }
  return html_str
  
}


// implement this and all the others
function mergedDetailFormatter(value, row, index){
  var object_for_table_body = {}
  var table_html = '<table class="table_small_font table table-light table-sm table-hover">';
  var table_header = '<thead class="table-dark"><tr><th scope="col">Last Version metadata</th>'
  var table_body = "<tbody>"
  for (key in row){
    if (key == 'license'){
      for (channel in row[key]){
        for (label in row[key][channel]){
          // table_header += `<th scope="col">${channel}-${label}</th>`
          table_header += `<th scope="col"><div style="display:flex;justify-content: center;">`;
          table_header +=  `<span class="store_label custom-label label-outline-${labels_style_dict[channel]} label-outline-xs"><i class="bi bi-shop"></i>${channel}</span>`;
          table_header +=  `<span class="label_label custom-label label-outline-${labels_style_dict[label]} label-outline-xs"><i class="bi bi-tags"></i>${label}</span>`;
          table_header += `<div></th>`
          try{
            var normal_json = row[key][channel][label];
            var licenseChannnelLabel = JSON.parse(normal_json.replace(/'/g, '"'));
            // var wasAdded = false
            for (license_attr in licenseChannnelLabel){
              if(license_attr in object_for_table_body == false){
                object_for_table_body[license_attr] = []
                object_for_table_body[license_attr].push(licenseChannnelLabel[license_attr])
              }
              else{
                object_for_table_body[license_attr].push(licenseChannnelLabel[license_attr])
              }
            }
          }
          catch(e){
            console.log(e)
            continue
          }
        }

      }
      table_header +=`</tr></thead>`

    }
  }

  for(license_attr in object_for_table_body){
    table_body += `<tr><th>${license_attr}</th>`
    for(license_attr_index in object_for_table_body[license_attr]){
      if (license_attr == 'dev_url' || license_attr == 'url'){
        var icon_logo = (license_attr == 'dev_url') ? 'github' : 'box-arrow-right';

        table_body += `<td><a class="github_type button-spaced" href="${object_for_table_body[license_attr][license_attr_index]}" target="_blank" title="Github">
          <button type="button" class="custom-label label-outline-xs label-color-gray"><i class="bi bi-${icon_logo}"></i></button>
        </a></td>`

      }
      else{
        table_body += `<td><span class="custom-label label-outline-xs label-color-gray">${object_for_table_body[license_attr][license_attr_index]}</span></td>`
      }
    }
    table_body += `</tr>`
  }
  table_body += `</tbody>`

  table_html += `${table_header}${table_body}</table>`

  return table_html
  // return html.join("")
}

function fieldsFormatter(value, row, index){
  console.log(value)
  console.log(row)
  console.log(index)
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

      var index_label_color = 0
      for (const [key, value2] of Object.entries(object_row)) {
        if (
          typeof value2 != 'object' &&
          !Array.isArray(value2) &&
          value2 !== null
        ){
          html += `<div class="labels_container"> <span class="store_label btn btn-outline-${label_styles(index_label_color)} btn-xs"> #${key} </span> <span class="store_label_val">${value2}</span></div>`        
        }
        else{
          if(value2.author != ""){
            html += `<div class="labels_container"> <span class="store_label btn btn-outline-${label_styles(index_label_color)} btn-xs"> #${key} </span> <span class="store_label_val">${value2.author}</span></div>`
          }
          // else{
          //   html += `<div class="labels_container"> <span class="store_label btn-outline-secondary btn-xs"> #${key} </span > <span class="store_label_val"> No Data Provided</span></div>`
          // }
        }
        index_label_color += 1;
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
