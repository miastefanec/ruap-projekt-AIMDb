document.querySelector("#showAll").addEventListener("click", (event) => {
    event.preventDefault;
    document.querySelector("#term").disabled = document.querySelector("#showAll").checked;
    document.querySelector("#filter").disabled = document.querySelector("#showAll").checked;    
});
