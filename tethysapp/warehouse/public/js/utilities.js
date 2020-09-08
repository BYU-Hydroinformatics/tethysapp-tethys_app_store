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
	$(`#${modal} .modal-footer`)
		.find("img")
		.hide()
}

const showLoader = (modal = "notification") => {
	$(`#${modal} .modal-footer`)
		.find("img")
		.show()
}

const sendNotification = (message, n_content) => {
	notifCount = notifCount + 1
	let new_element = `<div style="display: none;" id="install_notif_${notifCount}">${message}</div>`
	if (message == "install_complete") {
		new_element = `<div style="display: none;" id="install_notif_${notifCount}">Install Complete. Restarting Server for changes to take effect.</div>`
		inRestart = true
		notification_ws.send(
			JSON.stringify({
				data: {},
				type: `restart_server`
			})
		)
		$("#goToAppButton").show()
		$("#doneInstallButton").show()
	}
	n_content.append(new_element)
	$(`#install_notif_${notifCount}`).show("fast")
}

function startWS(websocketServerLocation, n_content) {
	notification_ws = new WebSocket(websocketServerLocation)
	notification_ws.onopen = () => {
		console.log("WebSocket is Open")
		if (inRestart) {
			hideLoader()
			inRestart = false
			sendNotification("Server restart completed successfully", n_content)
			// Hide Cancel Button
			$("#mainCancel").hide()
		}
		setServerOnline()
	}

	notification_ws.onmessage = function(e) {
		let data = JSON.parse(e.data)
		if (typeof data.message == "string") {
			let content = n_content
			if ("target" in data.message) {
				content = $(`#${data.message.target}`)
			}
			// It's normal string
			sendNotification(data.message, content)
			return false
		} else {
			// Found an object?
			// Check if we have a function to call
			let helper = settingsHelper
			let content = n_content

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
