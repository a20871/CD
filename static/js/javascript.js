const username = document.getElementById("username");
const password = document.getElementById("password");
const socket = io();
const http = new XMLHttpRequest();
const json = {};

function PedidoHTTP()
{
    const http = new XMLHttpRequest();
    const url = "http://127.0.0.1:5000" + document.getElementById("domain").value + document.getElementById("domain2").value;
    const method = document.getElementById("method").value;
    const json = document.getElementById("json").value

    http.open(method, url);
    http.setRequestHeader("Authorization", "Basic " + btoa(username.value + ":" + password.value));
    http.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    http.send(JSON.stringify(json));
        
    http.onreadystatechange = (e) => {
        if (http.readyState === 4){
            document.getElementById('mensagem').innerHTML = http.responseText

            /*document.getElementById("mensagem").text = http.responseText
            console.log("|" + http.responseType + "|")
            var element = document.createElement('a');
            element.setAttribute('href', 'data:attachment;charset=utf-8,' + encodeURIComponent(http.responseText));
            element.setAttribute('download', "ola");

            element.style.display = 'none';
            document.body.appendChild(element);

            element.click();

            document.body.removeChild(element);*/
        }
    }
}

  const url = "http://127.0.0.1:5000/login";
function fazerLogin(method, url)
{
    http.open(method, url);
    http.setRequestHeader("Authorization", "Basic " + btoa(username + ":" + password));
    // http.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    //http.send(json);

    http.onreadystatechange = (e) => {
        if (http.readyState === 4)
        {
            document.write(http.response)
            socket.emit('canais/entrar', {username: username});
            socket.on('novamensagem', function(data) {
                console.log(data['data'])
                var div = document.getElementById('mensagens');
                div.innerHTML += data['data'] + "<br>";
            });
        }
    }
}

function registar()
{
    const http = new XMLHttpRequest();
    const url = "http://localhost:3000/utilizadores/criar_conta/";
    const method = "POST"
    const json = {"username":username, "password":password};

    http.open(method, url);
    http.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
console.log(json);
    http.send(JSON.stringify(json));


    http.onreadystatechange = (e) => {
        if (http.readyState === 4)
            document.write(http.response)
        console.log(http.response)
    }
}

function PedidoHTTPFicheiros()
{
    const http = new XMLHttpRequest();
    const url = "http://127.0.0.1:5000" + document.getElementById("domain").value + document.getElementById("domain2").value;
    const method = document.getElementById("method").value;
    const json = document.getElementById("json").value

    http.open(method, url, true);
    http.setRequestHeader("Authorization", "Basic " + btoa(username + ":" + password));
    const file = document.getElementById("ficheiro")[0].files[0]
    console.log(file)
    
    var formData = new FormData();
    formData.append("ficheiro", file);
    http.send(formData);
        
    http.onreadystatechange = (e) => {
        document.getElementById("mensagem").text = http.responseText
    }
}