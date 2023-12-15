// Some Constant Vars being used across the script
// Probably need a better way to manage this state though
// @TODO : Fix This global variable

var notification_ws
var notifCount = 0
var inRestart = false


const label_styles = (index) => {
  var list_styles = [
    "blue",
    "indigo",
    "pink",
    "red",
    "orange",
    "yellow",
    "green",
    "teal",
    "cyan",
    "white",
    "gray",
    "gray-dark",
    "primary",
    "secondary",
    "success",
    "info",
    "warning",
    "danger",
    "light",
    "dark",
    "purple"
  ]
  return list_styles[index]
}

const get_color_label_dict = (stores) => {
  var color_store_dict = {}
  var index_style = 0;
  for (store in stores){
    if (stores[store]['conda_channel'] in color_store_dict == false){
      color_store_dict[stores[store]['conda_channel']] = label_styles(index_style)
      stores[store]['conda_style'] = label_styles(index_style)
      index_style += 1;
    }
    document.getElementById(`label-color-id-${stores[store]['conda_channel']}`).classList.add(`label-outline-${color_store_dict[stores[store]['conda_channel']]}`);

    for (label in stores[store]['conda_labels']){
      if (stores[store]['conda_labels'][label] in color_store_dict == false){
        color_store_dict[stores[store]['conda_labels'][label]] = label_styles(index_style)
        index_style += 1;
      }
      document.getElementById(`label-color-id-${stores[store]['conda_channel']}-${stores[store]['conda_labels'][label]}`).classList.add(`label-color-${color_store_dict[stores[store]['conda_labels'][label]]}`);

    }
  }
  return color_store_dict
}



const serviceLookup = {
  spatial: "spatialdatasetservice",
  dataset: "datasetservice",
  wps: "webprocessingservice",
  persistent: "persistentstoreservice"
}

const reloadCacheRefresh = () => {
  notification_ws.send(
    JSON.stringify({
      data: {},
      type: `clear_cache`
    })
  )
  // Refresh Page
  location.reload()
}

function resetInstallStatus() {
  if (installData) {
    installData = {}
  }
  installRunning = false
}

function setServerOffline() {
  $("#offline-modal").modal("show")
  $("#overlay").show()
  $("#serverStatusOnline").hide()
  $("#serverStatusOffline").show()
}

function setServerOnline() {
  $("#overlay").hide()
  $("#offline-modal").modal("hide")
  $("#serverStatusOnline").show()
  $("#serverStatusOffline").hide()
  // Check for any pending updates and resume processing
  if (installRunning) {
    // Send WS request
    notification_ws.send(
      JSON.stringify({
        data: installData,
        type: "continueAfterInstall"
      })
    )
  }
}

function getParameterByName(name, url) {
  if (!url) return null
  name = name.replace(/[\[\]]/g, "\\$&")
  var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
    results = regex.exec(url)
  if (!results) return null
  if (!results[2]) return ""
  return decodeURIComponent(results[2].replace(/\+/g, " "))
}

const hideLoader = (modal = "notification") => {
  $(`#installLoaderEllipsis`).hide()
}

const showLoader = (modal = "notification") => {
  $(`#installLoaderEllipsis`).show()
  $("#mainCancel").hide()
}

const sendNotification = (message, n_content) => {
  notifCount = notifCount + 1
  let new_element = `<div style="display: none;" id="install_notif_${notifCount}">${message}</div>`
  if (message == "install_complete") {
    new_element = `<div style="display: none;" id="install_notif_${notifCount}">Install Complete. Restarting Server for changes to take effect.</div>`
    inRestart = true
    notification_ws.send(
      JSON.stringify({
        data: { ...installData, restart_type: "install" },
        type: `restart_server`
      })
    )
    resetInstallStatus()
  }
  if (message == "Uninstall completed. Restarting server...") {
    inRestart = true
    notification_ws.send(
      JSON.stringify({
        data: { ...uninstallData, restart_type: "uninstall" },
        type: `restart_server`
      })
    )
  }
  n_content.append(new_element)
  $(`#install_notif_${notifCount}`).show("fast")
}

function startWS(websocketServerLocation, n_content) {
  notification_ws = new WebSocket(websocketServerLocation)
  notification_ws.onopen = () => {
    console.log("WebSocket is Open")
    if (inRestart) {
      inRestart = false

      if ("name" in uninstallData) {
        // Coming back from an uninstall restart
        sendNotification(
          "Server restart completed successfully",
          $("#uninstallNotices")
        )

        $("#uninstallLoaderEllipsis").hide()
        $("#doneUninstallButton").show()
      } else {
        hideLoader()
        sendNotification("Server restart completed successfully", n_content)
        $("#goToAppButton").show()
        $("#doneInstallButton").show()
        // Hide Cancel Button
        $("#mainCancel").hide()
      }
    }
    // Check if we have any updateData
    if ("name" in updateData) {
      // clear out updateData
      updateData = {}
      sendNotification(
        "Server restart completed successfully",
        $("#update-notices")
      )
      $("#update-loader").hide()
      $("#done-update-button").show()
    }
    setServerOnline()
  }

  notification_ws.onmessage = function(e) {
    let data = JSON.parse(e.data)
    let content = n_content

    if (typeof data.message == "string") {
      // It's normal string
      sendNotification(data.message, content)
      return false
    } else {
      // Found an object?
      // Check if we have a function to call
      let helper = settingsHelper

      if ("target" in data.message) {
        content = $(`#${data.message.target}`)
        return sendNotification(data.message.message, content)
      }

      if ("helper" in data.message) {
        if (data.message["helper"] == "addModalHelper") {
          helper = addModalHelper
          content = $("#statusMessagesAdd")
        }
      }
      if ("jsHelperFunction" in data.message) {
        helper[data.message["jsHelperFunction"]](
          data.message.data,
          content,
          data.message,
          notification_ws
        )
      } else {
        console.log("Undefined jsHelperFunction in JSON WebSocket call")
      }
    }
  }

  notification_ws.onclose = function() {
    setServerOffline()
    // Try to reconnect in 1 second
    setTimeout(function() {
      startWS(websocketServerLocation, n_content)
    }, 1000)
  }
}


var labels_options_str = `<select>` 
$("#labelList").html("hol")


const createStoreMenuHtml = (store) => {
  let html_labels = createStoreLabelsHtml(store)
  let isDefault = ""
  if (active_stores[`${store.conda_channel}`]['default']){
    isDefault = 'checked'
  }
  var html_store_string = `<div class="dropdown-check-list-channels">
    <ul class="items">
      <li><input type="checkbox" id="${store.conda_channel}"  name= "${store.conda_channel}" value= "${store.conda_channel}" ${isDefault} >

        <label for="${store.conda_channel}">
          <div class="loader_and_title">
            <div id="${store.conda_channel}_spinner" class="spinner-border spinner-border-sm text-info" style="display:none;" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>  
            <p class="label-anaconda">
              ${store.conda_channel} 
            </p>
          </div>

          <span ></span>
        </label>

      </li>
    </ul>
  </div>`
  
  var success_string = `<div id="${store.conda_channel}_successMessage" style="display:none;margin-top:10px;" class="p-3 mb-2 bg-success text-white">
      <p>Your Tethys Application has been successfully queued for processing.You will be notified via email when you application is available on the Tethys App Store. <span id="${store.conda_channel}_SuccessLinkMessage">Click <span id="${store.conda_channel}_addSuccessLink">here</span> to follow the processing logs and inspect it for errors.</span>
    </p>
  </div>`
  var fail_string =`<div id="${store.conda_channel}_failMessage" style="display:none;margin-top:10px;" class="p-3 mb-2 bg-info text-white"></div>`
  return `<div class="row_store_submission">${html_store_string}${html_labels}<div id="${store.conda_channel}_branchesList"></div>${success_string}${fail_string}</div>`
}

const createStoreLabelsHtml = (store) => {
  let isDefault = "d-none"
  let store_labels_len = store['conda_labels'].length;

  if (active_stores[`${store.conda_channel}`]['default'] && store_labels_len > 1){
    isDefault = ""
  }
  let check_box = `<div id="${store.conda_channel}_label" class="dropdown-check-list ${isDefault}" tabindex="100"> <div><span>Please select the labels to use:</span> <span class="anchor">Labels</span></div><ul class="items">`
  let options_str = ""
  store['conda_labels'].forEach(function(label){
    // let isMain = ''
    // if(label == 'main'){
    //   isMain = 'checked'
    // }
    options_str += `<li><input id= "${store.conda_channel}__${label}" type="checkbox" value='${label}' /><label for ="${store.conda_channel}__${label}"><span>${label}</span><span></span></label> </li>`
  })

  sel = `${check_box}${options_str}</ul></div>`

  
  return sel
}

const createStoresMenusHtml = (stores) =>{
  let storesMenuHtml = ''
  stores.forEach(
    (store) => storesMenuHtml += createStoreMenuHtml(store)
    
  )
  return storesMenuHtml
}

const addFunctionalitySingleStores = (store) =>{
  
  var checkList = document.getElementById(`${store.conda_channel}_label`);
  
  checkList.getElementsByClassName('anchor')[0].onclick = function(evt) {
    console.log(active_stores)

    if (checkList.classList.contains('visible')){
      checkList.classList.remove('visible');
    }
      
    else{
      checkList.classList.add('visible');

    }
  }
  
  var checkListStore = document.getElementById(`${store.conda_channel}`);
    checkListStore.onchange = function(evt){
    var branch_select = document.getElementById(`${store.conda_channel}_branchesList`);
      if(this.checked){
        // if(store.conda_labels.lenght > 1) {
          checkList.classList.remove('d-none')
          branch_select.classList.remove('d-none')
        // }
        active_stores[this.value]['active'] = true  
      }
      else{
        // if(store.conda_labels.lenght > 1) {
          checkList.classList.add('d-none')
          branch_select.classList.add('d-none')

        // }
        active_stores[this.value]['active'] = false
      }
    }

  store.conda_labels.forEach(function(label){
    var checkListLabel = document.getElementById(`${store.conda_channel}__${label}`);
    checkListLabel.onchange = function(evt){
      console.log(this.checked)
      if(this.checked){
        if(!active_stores[`${store.conda_channel}`]['conda_labels'].includes(this.value)){
          active_stores[`${store.conda_channel}`]['conda_labels'].push(this.value);
          console.log(active_stores[`${store.conda_channel}`]['conda_labels']);
        }
      }
      else{
        if(active_stores[`${store.conda_channel}`]['conda_labels'].includes(this.value)){
          const index = active_stores[`${store.conda_channel}`]['conda_labels'].indexOf(this.value);
          active_stores[`${store.conda_channel}`]['conda_labels'].splice(index, 1);
          console.log(active_stores[`${store.conda_channel}`]['conda_labels'])
        }
      }
    }

    
  })

}
const addFunctionalityStores = (stores) =>{
  stores.forEach(
    (store) => addFunctionalitySingleStores(store)
  )
}

const create_request_obj = (storesDataList) =>{
  storesDataList.forEach(function(store){
    active_stores[`${store.conda_channel}`] = Object.assign({}, store);
    
    if (active_stores[`${store.conda_channel}`].hasOwnProperty(`${store.conda_channel}`)){
        delete active_stores[`${store.conda_channel}`][`${store.conda_channel}`]
    }
    let labels_selected = []
    if(active_stores[`${store.conda_channel}`]['conda_labels'].length < 2){
      labels_selected.push(active_stores[`${store.conda_channel}`]['conda_labels'][0])
    }
    // active_stores[`${store.conda_channel}`]['conda_labels'].forEach(function(label){
      
    //   if(active_stores[`${store.conda_channel}`]['conda_labels'].includes('main') && !labels_selected.includes('main')){
    //     labels_selected.push('main')
    //   }

    // })
    active_stores[`${store.conda_channel}`]['active'] = active_stores[`${store.conda_channel}`]['default'];
    active_stores[`${store.conda_channel}`]['conda_labels'] = labels_selected
  })
}
