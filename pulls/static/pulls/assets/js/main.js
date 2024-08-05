// Fonction d'allert en fonction du type d'erreur
function showAlert(type, message,times) {
    var iconClass;
    switch (type) {
        case 'success':
            iconClass = 'dripicons-checkmark';
            break;
        case 'danger':
            iconClass = 'dripicons-wrong';
            break;
        case 'warning':
            iconClass = 'dripicons-warning';
            break;
        case 'info':
            iconClass = 'dripicons-information';
            break;
        default:
            iconClass = '';
    }

    var alertHTML = '<div class="alert alert-' + type + '" role="alert">' +
                        '<i class="' + iconClass + ' me-2"></i>' +
                        message +
                    '</div>';
    $('#container-error').append(alertHTML);
    setTimeout(function() {
        $('.alert').alert('close');
    }, times); 
}

function showAlertContenair(type, message,container_error,times) {
    var iconClass;
    switch (type) {
        case 'success':
            iconClass = 'dripicons-checkmark';
            break;
        case 'danger':
            iconClass = 'dripicons-wrong';
            break;
        case 'warning':
            iconClass = 'dripicons-warning';
            break;
        case 'info':
            iconClass = 'dripicons-information';
            break;
        default:
            iconClass = '';
    }

    var alertHTML = '<div class="alert alert-' + type + '" role="alert">' +
                        '<i class="' + iconClass + ' me-2"></i>' +
                        message +
                    '</div>';
    container_error.append(alertHTML);
    setTimeout(function() {
        $('.alert').alert('close');
    }, times); 
}

function ActivationOpt(){
    activation_mfa=document.getElementById('activate-2fa-btn')
    if(activation_mfa){
        document.getElementById('activate-2fa-btn').addEventListener('click',function(event){
            event.preventDefault();
            var standard_modal = new bootstrap.Modal(document.getElementById('standard-modal'));
            var myFirstModal = new bootstrap.Modal(document.getElementById('login-modal'));
            myFirstModal.show();
            console.log(document.getElementById('password1'));
            $('#confirmationAcount').on('click',function(event){
                if (document.getElementById('password1').value ==='') {
                    console.log('conspiration')
                    showAlert('info', 'Verifier le champs de saissi est obligatoire',2000)
                }else{
                    
                    const csrfToken= $('input[name=csrfmiddlewaretoken]').val()
                    var formData = new FormData();
                    formData.append('password', $('#password1').val());
                    fetch('verification', {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken
                        },
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status){
                            myFirstModal.hide();
                            document.getElementById('opt-secret').value=data.message.otp_secret
                            document.getElementById('qr_code').innerHTML=data.message.qr_code
                            standard_modal.show();
                            
                        }else{
                            console.log('erreur :');
                        }
                    })
                    .catch(error => {
                        console.error('Erreur lors de la requête fetch :', error);
                    });
            
                }
            });
        });
    } 
    
}


function enableopt(){
    $('#activeteOptsecret').on('click', function(event) {
        event.preventDefault(); 
        try {
            var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const secret = document.getElementById("id_otp");
            
            $.ajax({
                type: 'POST',
                url: "verification",
                data: {
                    'otp': secret.value,
                    'csrfmiddlewaretoken': csrftoken
                },
                success: function(data) {
                    if (data.status) {
                        var myFirstModal = bootstrap.Modal.getInstance(document.getElementById('standard-modal'));
                        myFirstModal.hide();
                        $('#activate-2fa-btn').prop('disabled', true);
                        $('#deactivate-2fa-btn').removeClass("d-none disabled");
                        $('#deactivate-2fa-btn').prop('disabled', false);
                        $('#activate-2fa-btn').addClass("d-none");
                        $('#testspan').text("Authentification à deux facteurs activé");
                        $('#testspan').text("Authentification à deux facteurs activé");
                        $('#checkValid').removeClass("dripicons-warning text-warning");
                        $('#checkValid').addClass("dripicons-checkmark text-white");
                        $('#btn-text').removeClass("btn-light");
                        $('#btn-text').addClass("btn-success");
                        $('#activate-2fa-btn').addClass("d-none");
                        
                    } else {
                        showAlert('danger', data.message ,5000);
                    }
                }
            });
        } catch (error) {
            console.log('erreur :'+ error);
        }
    });
}

function updatePassword(){
    $('#login_modal').on('click',function(event){
        event.preventDefault();
        var myFirstModal = new bootstrap.Modal(document.getElementById('login-modal'));
        var mySecondtModal = new bootstrap.Modal(document.getElementById('password-modal'));
        myFirstModal.show();
        $('#confirmationAcount').attr('id', 'sendPassword');
        $('#sendPassword').on('click',function(event){
            event.preventDefault();
            var formData = new FormData();
            formData.append('password', $('#password1').val());
            const csrfToken= $('input[name=csrfmiddlewaretoken]').val()
            fetch('change_pass', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.reponse==='succes'){
                    myFirstModal.hide()
                    mySecondtModal.show()
                    $('#change_password').on('click',function(event){
                        event.preventDefault();
                        var form = new FormData();
                        form.append('new_password', $('#new_password').val());
                        form.append('con_password', $('#cpassword').val());
                        const csrfToken= $('input[name=csrfmiddlewaretoken]').val();
                        fetch('change_pass', {
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': csrfToken
                            },
                            body: form
                        })
                        .then(response => response.json())
                        .then(data => {
                            containerMsg =$("#container-change")
                            console.log(data);
                            if (data.reponse==='succes'){
                                mySecondtModal.hide();
                                $.NotificationApp.send("Success",data.message,"Position","top-left","success");
                            }else{
                                showAlertContenair('danger', data.message,containerMsg,5000);
                            }
                        })
                    })
                    
                }else{
                    containerMsg =$("#container-login");
                    showAlertContenair('danger', data.message,containerMsg,5000);
                }
            })
            .catch(error => {
                console.error('Erreur lors de la requête fetch :', error);
            });
        });
    });
}


$(document).ready(function() {
    
    $('#signupForm').submit(function(event) {
        event.preventDefault(); 
        var csrfTokenValue = document.querySelector("[name=csrfmiddlewaretoken]").value;
        var firstNameValue = $("#id_fname").val();
        var lastNameValue = $("#id_lname").val();
        var emailValue = $("#id_email").val();
        var passwordValue = $("#id_password").val();
        var acceptTermsValue = $("#checkbox-signup").prop("checked");
        var decimal =
          /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9])(?!.*\s).{8,25}$/;

        if (
            (firstNameValue==="") |
            (lastNameValue==="") |
            (emailValue==="") |
            (passwordValue==="")
        ) {
            showAlert('info', 'Veuillez remplir, tous les champs sont obligatoires',5000);
        }else 
        if (passwordValue.match(decimal)) {
            try {
                var formData = $(this).serialize();
                $.ajax({
                    type: 'POST', 
                    url: "Inscription", 
                    data: formData, 
                    dataType: 'json', 
                    headers: {
                        'X-CSRFToken': csrfTokenValue
                    },
                    success: function(response) {
                        if (response.success) {
                            showAlert('success', response.msg ,5000);
                        } else {
                            showAlert('danger',response.msg,5000);
                        }
                    },
                    error: function(xhr, status, error) {
                        showAlert('warning', 'Service momentanement insdiponible',5000);
                    }
                });
            } catch (error) {
              console.error("Error:", response.errors);
            }
            
        }else
        {
            showAlert('warning', 'Le mot de passe doit contenir 8 à 15 caractères contenant au moins une lettre minuscule, une lettre majuscule, un chiffre numérique et un caractère spécial',5000);
        }
        
    });


    $('#form').submit(function(e) {
        e.preventDefault();
        var csrfTokenValue = document.querySelector("[name=csrfmiddlewaretoken]").value;
        var id_username = $("#id_username").val();
        var id_password = $("#id_password").val();

        if (
            (id_username==="") |
            (id_password==="")
        ) {
            showAlert('info', 'Veuillez remplir, tous les champs sont obligatoires',5000);
        }else{
            try {
                var formData = $(this).serialize();
                $.ajax({
                    type: 'POST', 
                    url: "Connexion", 
                    data: formData,
                    dataType: 'json', 
                    headers: {
                        'X-CSRFToken': csrfTokenValue
                    },
                    success: function(response) {
                        if (response.success) {
                            if(response.opt==='activate'){
                                showAlert('success', response.msg ,5000);
                                window.location="Authentification"
                            }
                            else if(response.opt==='deactivate'){
                                showAlert('success', response.msg ,5000);
                                window.location="Home"
                            }
                        } else {
                            showAlert('danger',response.msg,5000);
                        }
                    },
                    error: function(xhr, status, error) {
                        showAlert('warning', 'error',5000);
                    }
                });
            } catch (error) {
              console.error("Error:", response.errors);
            }
        }
    });

    $('#2fa-form').on('submit', function(event) {
        event.preventDefault();
        
        var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        var otp = $('#id_otp').val();
        
        $.ajax({
            type: 'POST',
            url: "../Confirme/",
            data: {
                'otp': otp,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(data) {
                if (data.success) {
                    showAlert('success', data.message ,2000);
                    window.location.href = '../Home';
                } else {
                    showAlert('danger', data.message ,5000);
                }
            }
        });
    });

    ActivationOpt()
    enableopt()
    updatePassword()

    console.log($('.add-comment'));
    $('.add-comment').on('click', function() {
        
        var cvId = $(this).data('id');
        console.log(cvId)
        $('#comment-modal-cv').modal('show');
    });
});