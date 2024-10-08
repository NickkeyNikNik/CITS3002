for (const form of document.forms) {
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        const select_options = document.getElementById(form.name);
        if (select_options.nodeName == "OPTION"){
            answer = select_options.options[select_options.selectedIndex].value;
        }
        else{
            answer = select_options.value;
        }
        fetch(`127.0.0.1/3002/${form.name}&${answer}&${form.parentElement.firstElementChild.textContent}`);
        setTimeout(0);
        window.location.reload();
    })

}