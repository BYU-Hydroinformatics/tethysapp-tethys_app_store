// Some Constant Vars being used across the script
// Probably need a better way to manage this state though
// @TODO : Fix This global variable

var notification_ws
var notifCount = 0
var inRestart = false

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
          <span span class="label-anaconda">${store.conda_channel}</span>

          <span ></span>
        </label>

      </li>
    </ul>
  </div>`
  return `<div class="row_store_submission">${html_store_string}${html_labels}</div>`
}

const createStoreLabelsHtml = (store) => {
  let isDefault = "d-none"
  let store_labels_len = store['conda_labels'].length;

  if (active_stores[`${store.conda_channel}`]['default'] && store_labels_len > 1){
    isDefault = ""
  }
  let check_box = `<div id="${store.conda_channel}_label" class="dropdown-check-list ${isDefault}" tabindex="100"> <span class="anchor">Labels</span><ul class="items">`
  let options_str = ""
  store['conda_labels'].forEach(function(label){
    // let isMain = ''
    // if(label == 'main'){
    //   isMain = 'checked'
    // }
    options_str += `<li> <input id= "${store.conda_channel}__${label}" type="checkbox" value='${label}' /><label for ="${store.conda_channel}__${label}"><span>${label}</span><span></span></label> </li>`
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
      
      if(this.checked){
        // if(store.conda_labels.lenght > 1) {
          checkList.classList.remove('d-none')
        // }
        active_stores[this.value]['active'] = true  
      }
      else{
        // if(store.conda_labels.lenght > 1) {
          checkList.classList.add('d-none')
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
