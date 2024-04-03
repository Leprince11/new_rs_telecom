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
    }, 10000); 
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
          /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9])(?!.*\s).{8,15}$/;

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
                        showAlert('warning', 'error',5000);
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
                            showAlert('success', response.msg ,5000);
                            window.location="Home"
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

    $('#demo').pagination({
        dataSource: [1, 2, 3, 4, 5, 6, 7],
        pageSize: 5,
        autoHidePrevious: true,
        autoHideNext: true,
        callback: function(data, pagination) {
            var html = template(data);
            dataContainer.html(html);
        }
    })
});