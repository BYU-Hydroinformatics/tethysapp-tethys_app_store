


const clickevent = (event) => {
    var r = confirm("Are you sure ?")
    if (r==false){
        event.preventDefault()
    }
}

var addbutton = document.querySelector("[name=add-button]")
addbutton.addEventListener('click', clickevent);

