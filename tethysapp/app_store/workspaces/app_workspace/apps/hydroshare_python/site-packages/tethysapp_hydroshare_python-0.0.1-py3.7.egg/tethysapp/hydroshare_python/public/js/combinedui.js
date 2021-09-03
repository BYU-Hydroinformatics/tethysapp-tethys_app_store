

let button = document.getElementById('fetchfile')
button.addEventListener('click', async function () {
    const username = document.getElementById('username')
    const password = document.getElementById('password')
    const resourceid = document.getElementById('resourcein')
    const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]')
    const fileSelector = document.getElementById('title_input')

    const formData = new FormData();
    formData.append('username', username && username.value);
    formData.append('password', password && password.value);
    formData.append('resourcein', resourceid.value);
    formData.append('csrfmiddlewaretoken', csrfToken.value);
    
    document.body.classList.add('waiting');
    let responseData;
    try{
    const response = await fetch('/apps/hydroshare-python/filev/', {
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
    responseData.results.forEach(result => {
        const option = document.createElement('option');
        option.value = result.file_name;
        option.textContent = result.file_name;
        fileSelector.append(option)
    })
})


const clickevent = (event) => {
    var r = confirm("Are you sure to delete the file? Once deleted, you cannot retrieve it !")
    if (r==false){
        event.preventDefault()
    }
}



var deletebutton = document.querySelector("[name=delete-button]")
deletebutton.addEventListener('click', clickevent);


