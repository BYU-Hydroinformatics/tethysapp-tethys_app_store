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
    const response = await fetch('/apps/hydroshare-python/viewer/', {
        method: 'post',
        body: formData
    });

    responseData = await response.json()
    } catch{

    }finally{
        document.body.classList.remove('waiting');
    }

    var child = fileSelector.lastElementChild;
    while (child) {
        fileSelector.removeChild(child);
        child = fileSelector.lastElementChild;
    }
    // Default option
    const option = document.createElement('option');
    option.textContent = "Select a file";
    fileSelector.append(option)

    // File name options
    responseData.forEach(result => {
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


