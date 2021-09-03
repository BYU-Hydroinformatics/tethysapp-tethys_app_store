var L
    var mymap = L.map('mapid').setView([11.000082, 76.969214], 8);

    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        maxZoom: 18,
        id: 'mapbox/streets-v11',
        tileSize: 512,
        zoomOffset: -1,
        accessToken: 'pk.eyJ1IjoiYWJoaXNoZWthbWFsMTgiLCJhIjoiY2s1eTVxNGExMmQ5MDNubjExaWY5MjdvbSJ9.3nmdjWZmUCDNyRdlPo5gbg'
        }).addTo(mymap);

let resourceslist = []


let button = document.getElementById('fetchfile')
const fileSelector = document.querySelector('#title_input')
button.addEventListener('click', async function () {
    const username = document.getElementById('username')
    const password = document.getElementById('password')
    const viewr = document.getElementById('viewr')
    const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]')

    const formData = new FormData();
    formData.append('username', username && username.value);
    formData.append('password', password && password.value);
    formData.append('viewr', viewr.value);
    formData.append('csrfmiddlewaretoken', csrfToken.value);

    const response = await fetch('/apps/hydroshare-python/mapview/', {
        method: 'post',
        body: formData
    });

    const responseData = await response.json()
    resourceslist = responseData

    var child = fileSelector.lastElementChild;
    while (child) {
        fileSelector.removeChild(child);
        child = fileSelector.lastElementChild;
    }
    const filteredresource = responseData.filter(resource=>{
        
        if(!resource.coverages || resource.coverages.length==0){
            return false
        }
        const box = resource.coverages.find(coveragesItem=>coveragesItem.type=="box")
        if (box){return true}
        return false
    })
    // Default option
    const option = document.createElement('option');
    option.textContent = filteredresource.length==0?"THE SUBJECT YOU SEARCHED FOR DOES NOT HAVE RESOURCES WITH A SHAPEFILE":"Select a Resource";
    fileSelector.append(option)

    // File name options
        
        filteredresource.forEach(result => {
        const option = document.createElement('option');
        option.value = result.resource_id;
        option.textContent = result.resource_title;
        fileSelector.append(option)
    })
})
fileSelector.addEventListener('change', function(event){
    const selected = document.querySelector('#selected_resource')
    selected.textContent = event.target.value
})

const viewbutton = document.querySelector('[name=add-button]')
viewbutton.addEventListener('click', function(event){
    event.preventDefault()
    const selectedid = fileSelector.value
    const resource = resourceslist.find(resource=>resource.resource_id==selectedid)
    if(resource){
        console.log("Map works")
        const box = resource.coverages.find(coveragesItem=>coveragesItem.type=="box")
        var bounds = [[box.value.northlimit, box.value.westlimit], [box.value.southlimit, box.value.eastlimit]];
// create an orange rectangle
        L.rectangle(bounds, {color: "#ff7800", weight: 3}).addTo(mymap);
// zoom the map to the rectangle bounds
        mymap.fitBounds(bounds);
    }
})

