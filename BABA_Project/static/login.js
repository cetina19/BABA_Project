function validate(){
    let username = document.getElementById('Username').value;
    let password = document.getElementById('Password').value;
    let email = document.getElementById('Email').value;

    if(username === 'BABA_' && password === 'BABA1234'){
        alert('Login Successful');
    }
}