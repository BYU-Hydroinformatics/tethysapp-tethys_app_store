
const clickevent = (event) => {
    var r = confirm("Warning: Once deleted you cannot retrieve the resource. Are you sure you want to delete the resource?")
    if (r==false){
        event.preventDefault()
    }
}

var deletebutton = document.querySelector("[name=delete-button]")
deletebutton.addEventListener('click', clickevent);