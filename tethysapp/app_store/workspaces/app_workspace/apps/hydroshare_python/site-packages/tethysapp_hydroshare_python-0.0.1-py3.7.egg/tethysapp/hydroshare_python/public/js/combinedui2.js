
// let buttons = document.getElementById('fetchfile')
// buttons.addEventListener('clicks', async function () {
//     const username = document.getElementById('username')
//     const password = document.getElementById('password')
//     const resourceid = document.getElementById('resourcein')
//     const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]')
//     const fileSelector = document.getElementById('title_input')

//     const formData = new FormData();
//     formData.append('username', username.value);
//     formData.append('password', password.value);
//     formData.append('resourcein', resourceid.value);
//     formData.append('csrfmiddlewaretoken', csrfToken.value);

//     const response = await fetch('/apps/hydroshare-python/filev/', {
//         method: 'post',
//         body: formData
//     });

//     const responseData = await response.json()


//     var child = fileSelector.lastElementChild;
//     while (child) {
//         fileSelector.removeChild(child);
//         child = fileSelector.lastElementChild;
//     }
//     // Default option
//     const option = document.createElement('option');
//     option.textContent = "Select a file";
//     fileSelector.append(option)

//     // File name options
//     responseData.results.forEach(result => {
//         const option = document.createElement('option');
//         option.value = result.file_name;
//         option.textContent = result.file_name;
//         fileSelector.append(option)
//     })
// })

const clickevents = (event) => {
    var r = confirm("Are you sure you want to download the file ?")
    if (r==false){
        event.preventDefault()
    }
}

var downloadbutton = document.querySelector("[name=download-button]")
downloadbutton.addEventListener('clicks', clickevents);
