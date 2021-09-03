
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

    document.body.classList.add('waiting');
    let responseData;
    try{
    const response = await fetch('/apps/hydroshare-python/mapview/', {
        method: 'post',
        body: formData
    });

    responseData = await response.json()
    } catch{

    }finally{
        document.body.classList.remove('waiting');
    }resourceslist = responseData

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
 const url = '/apps/hydroshare-python/random/?id='+selectedid;
 const iframe = document.querySelector('.iframe');
 iframe.src='/apps/hydroshare-python/loading'
 setTimeout(()=>{
    iframe.src=url
 }, 100)
 

    }
})


