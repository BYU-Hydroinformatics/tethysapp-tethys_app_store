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
  if (index == 0) {
    return [
      '<a class="install button-spaced" href="javascript:void(0)" title="Uninstall">',
      `<button type="button" class="btn btn-info btn-warning btn-xs">Uninstall</button>`,
      "</a>",
      '<a class="install button-spaced" href="javascript:void(0)" title="Configure">',
      `<button type="button" class="btn btn-info btn-default btn-xs">Configure</button>`,
      "</a>"
    ].join("")
  } else {
    return [
      '<a class="install button-spaced" href="javascript:void(0)" title="Uninstall">',
      `<button type="button" class="btn btn-info btn-warning btn-xs">Uninstall</button>`,
      "</a>",
      '<a class="install button-spaced" href="javascript:void(0)" title="Configure">',
      `<button type="button" class="btn btn-info btn-default btn-xs">Configure</button>`,
      "</a>",
      '<a class="github button-spaced" href="javascript:void(0)" title="Update">',
      `<button type="button" class="btn btn-primary btn-success btn-xs">Update</button>`,
      "</a>"
    ].join("")
  }
}

window.operateEvents = {
  "click .install": function(e, value, row, index) {
    let n_div = $("#notification")
    let n_content = $("#notification .lead")
    n_content.empty()
    n_div.modal()
    notifCount = 0
    // Setup Versions

    let appName = getResourceValue("name", index)
    $("#installingAppName").text(appName)
    installData["name"] = appName
    let versionHTML = getVersionsHTML(appName, resources)
    n_content.append(htmlHelpers.versions(appName))
    n_content.find("#selectVersion").append(versionHTML)
    $("#versions").select2()
  },

  "click .github": function(e, value, row, index) {
    let githubURL = getResourceValue("dev_url", index)
    if (githubURL) window.open(githubURL, "_blank")
  }
}

function initMainTable() {
  // $table.on("all.bs.table", function(e, name, args) {
  //   console.log(name, args)
  // })
}
