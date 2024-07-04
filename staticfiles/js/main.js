AOS.init();
function sleep(mls) {
    return new Promise((resolve, reject) => setTimeout(resolve, mls))
}


class Custumer {
    constructor(element) {
        this.element = element;
    }
    addClass() {
        this.element.classList.add('d-none');
    }

    removeClass() {
        this.element.classList.remove('d-none');
    }
}

const title = ["Le numerique, autrement !", "NOUS CHOISIR"];
const descriptions = ["Nous accompagnons nos clients dans la réussite de leurs projets de transformation numérique. Avec un positionnement généraliste, notre Background technique et nos équipes d'experts nous permettent de mieux appréhender les besoins  de nos clients pour convenablement les adresser, nous délivrons la solution à leurs sollicitations en moins de 48h !",
    ` Des consultants passionnés et passionnants. 
      Des effectifs commerciaux très techniques et constamment en veille technologique sur leurs domaines d'expertise.
      Réactivité et agilité, avec une solution en moins de 48h.`
    ];
document.addEventListener('DOMContentLoaded', function () {
    const titre = document.getElementById('title');
    const modal = document.getElementById('modal-form');
    const Path = document.getElementById("Path");
    const input = document.querySelectorAll('.input-form');
    const label = document.querySelectorAll(".label-form");
    const clients = document.querySelectorAll('.client');
    const condidats = document.querySelectorAll('.condidat');
    const secondary = document.getElementById("secondary");
    const formClient = document.querySelector(".formClient");
    const formCandidat = document.querySelector(".formCandidat");
    const main = document.getElementById("main");

    let isformclient = false;

    const title2 = document.getElementById("typewriterh2");
    
    const submit = document.getElementById("sendCandidat");
    const submit2 = document.getElementById("sendClient");
    
    var typewriter = document.getElementById('typewriter');
    var typewriterp = document.getElementById('typewriterp');

    let sleeptime = 100;
    let curTitleIndex = 0;
    let curDescriptionIndex = 0;
    // const desc2 = document.getElementById("typewriterph2");

    $(".demo1").kwtFileUpload();
    async function printwriter(curWord, typewriterElement) {
        for (let i = 0; i < curWord.length; i++) {
            typewriterElement.innerText = curWord.substring(0, i + 1);
            await sleep(100);
        }
    }

    if (title2) {
        printwriter(title2.textContent, title2);
        sleep(100);
    }
    if(document.getElementById('showemodal')){
        document.getElementById('showemodal').addEventListener('click', () => {
            const curWord2 = "Votre réussite à portée de main";
            const typewriterElement = document.getElementById('enbleme');
            printwriter(curWord2, typewriterElement);
            // Formulaire 
            
            let btnActif = document.querySelector('.btn-toggle');
            if (btnActif) {
                const desable = btnActif.getAttribute("aria-pressed")=="true";
                
                try {
                    btnActif.addEventListener("click", () => {
                        const desables = btnActif.getAttribute("aria-pressed");
                        Path.style.transition = "fill 0.2s ease-out";
                        console.log(isformclient);
                        if (document.querySelector(".focus.active")) {
                            titre.innerText = "Augmentez vos chances d'être contacté par un recruteur";
                            modal.style.backgroundColor = "#EEF9FF";
                            submit.style.backgroundColor = "#317ACA"
                            secondary.style.backgroundColor = "#317ACA";
                            Path.setAttribute("fill", "#317ACA");
                            for (var i = 0; i < input.length; i++) {
                                input[i].style.borderBottom = '1px solid #317ACA';
                                input[i].style.backgroundColor = 'transparent';
                                input[i].style.color='#317ACA';
    
                            };
                            for (var i = 0; i < label.length; i++) {
                                label[i].style.color = '#317ACA';
                            };
    
                            if (formCandidat.classList.contains("d-none")) {
                                formCandidat.classList.remove("d-none");
                                formClient.classList.add("d-none");
                                isformclient=false;
                            } else {
                                formClient.classList.remove("d-none");
                                formCandidat.classList.add("d-none");
                                isformclient=true;
                                
                            }
                        } else {
                            titre.innerText = "Recherchez des competences et trouvez vos futurs collaborateurs parmi plus de 300 000 profils";
                            modal.style.backgroundColor = "#317ACA";
                            submit2.style.backgroundColor = "#EEF9FF"
                            secondary.style.backgroundColor = "#EEF9FF";
                            Path.setAttribute("fill", "#EEF9FF");
                            for (var i = 0; i < input.length; i++) {
                                input[i].style.borderBottom = '1px solid #EEF9FF';
                                input[i].style.backgroundColor = 'transparent';
                                input[i].style.color='#EEF9FF';
                            };
                            for (var i = 0; i < label.length; i++) {
                                label[i].style.color = '#EEF9FF';
                            };
                            if (formClient.classList.contains("d-none")) {
                                formClient.classList.remove("d-none");
                                formCandidat.classList.add("d-none");
                                isformclient=true;
                            } else {
                                formCandidat.classList.remove("d-none");
                                formClient.classList.add("d-none");
                                isformclient=false;
                            }
                        }
                        console.log(isformclient)
                        postCandidatClient(isformclient);
                    });
                    console.log(isformclient)
                    postCandidatClient(isformclient);
                } catch (error) {
                    console.error("L'erreur :" + error.message);
                }
            }
        });
    }
    const writeLoop = async () => {
        while (true) {
            let curWord = title[curTitleIndex];
            let curWordDescrption = descriptions[curDescriptionIndex];
            for (let i = 0; i < curWord.length; i++) {
                typewriter.innerText = curWord.substring(0, i + 1);
                await sleep(sleeptime);
            }
            for (let i = 0; i < curWordDescrption.length; i++) {
                typewriterp.innerText = curWordDescrption.substring(0, i + 1);
                await sleep(sleeptime / 10);
            }
            await sleep(sleeptime * 120);

            for (let i = curWord.length; i > 0; i--) {
                typewriter.innerText = curWord.substring(0, i - 1);
                await sleep(sleeptime);
            }
            if (curTitleIndex === title.length - 1) {
                curTitleIndex = 0;
                curDescriptionIndex = 0;
            } else {
                curTitleIndex++;
                curDescriptionIndex++;
            }
            await sleep(sleeptime * 10);
        }
    }

    writeLoop()
    expertise()
    // sendContact() 
    const wrapper = document.querySelector(".wrapper");
    const carousel = document.querySelector(".carousel");
    const firstCardWidth = carousel.querySelector(".card").offsetWidth;
    const arrowBtns = document.querySelectorAll(".wrapper i");
    const carouselChildrens = [...carousel.children];

    let isDragging = false, isAutoPlay = true, startX, startScrollLeft, timeoutId;

    // Get the number of cards that can fit in the carousel at once
    let cardPerView = Math.round(carousel.offsetWidth / firstCardWidth);

    // Insert copies of the last few cards to beginning of carousel for infinite scrolling
    carouselChildrens.slice(-cardPerView).reverse().forEach(card => {
        carousel.insertAdjacentHTML("afterbegin", card.outerHTML);
    });

    // Insert copies of the first few cards to end of carousel for infinite scrolling
    carouselChildrens.slice(0, cardPerView).forEach(card => {
        carousel.insertAdjacentHTML("beforeend", card.outerHTML);
    });

    // Scroll the carousel at appropriate postition to hide first few duplicate cards on Firefox
    carousel.classList.add("no-transition");
    carousel.scrollLeft = carousel.offsetWidth;
    carousel.classList.remove("no-transition");

    // Add event listeners for the arrow buttons to scroll the carousel left and right
    arrowBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            carousel.scrollLeft += btn.id == "left" ? -firstCardWidth : firstCardWidth;
        });
    });

    const dragStart = (e) => {
        isDragging = true;
        carousel.classList.add("dragging");
        // Records the initial cursor and scroll position of the carousel
        startX = e.pageX;
        startScrollLeft = carousel.scrollLeft;
    }

    const dragging = (e) => {
        if(!isDragging) return; // if isDragging is false return from here
        // Updates the scroll position of the carousel based on the cursor movement
        carousel.scrollLeft = startScrollLeft - (e.pageX - startX);
    }

    const dragStop = () => {
        isDragging = false;
        carousel.classList.remove("dragging");
    }

    const infiniteScroll = () => {
        // If the carousel is at the beginning, scroll to the end
        if(carousel.scrollLeft === 0) {
            carousel.classList.add("no-transition");
            carousel.scrollLeft = carousel.scrollWidth - (2 * carousel.offsetWidth);
            carousel.classList.remove("no-transition");
        }
        // If the carousel is at the end, scroll to the beginning
        else if(Math.ceil(carousel.scrollLeft) === carousel.scrollWidth - carousel.offsetWidth) {
            carousel.classList.add("no-transition");
            carousel.scrollLeft = carousel.offsetWidth;
            carousel.classList.remove("no-transition");
        }

        // Clear existing timeout & start autoplay if mouse is not hovering over carousel
        clearTimeout(timeoutId);
        if(!wrapper.matches(":hover")) autoPlay();
    }

    const autoPlay = () => {
        if(window.innerWidth < 800 || !isAutoPlay) return; // Return if window is smaller than 800 or isAutoPlay is false
        // Autoplay the carousel after every 2500 ms
        timeoutId = setTimeout(() => carousel.scrollLeft += firstCardWidth, 2500);
    }
    autoPlay();

    carousel.addEventListener("mousedown", dragStart);
    carousel.addEventListener("mousemove", dragging);
    document.addEventListener("mouseup", dragStop);
    carousel.addEventListener("scroll", infiniteScroll);
    wrapper.addEventListener("mouseenter", () => clearTimeout(timeoutId));
    wrapper.addEventListener("mouseleave", autoPlay);
    
});

(function ($) {
    var customDragandDrop = function (element) {
        $(element).addClass("kwt-file__input");
        var element = $(element).wrap(
            `<div class="kwt-file"><div class="kwt-file__drop-area"><span class='kwt-file__choose-file ${element.attributes.data_btn_text
                ? "" === element.attributes.data_btn_text.textContent
                    ? ""
                    : "kwt-file_btn-text"
                : ""
            }'>${element.attributes.data_btn_text
                ? "" === element.attributes.data_btn_text.textContent
                    ? `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor"><path d="M67.508 468.467c-58.005-58.013-58.016-151.92 0-209.943l225.011-225.04c44.643-44.645 117.279-44.645 161.92 0 44.743 44.749 44.753 117.186 0 161.944l-189.465 189.49c-31.41 31.413-82.518 31.412-113.926.001-31.479-31.482-31.49-82.453 0-113.944L311.51 110.491c4.687-4.687 12.286-4.687 16.972 0l16.967 16.971c4.685 4.686 4.685 12.283 0 16.969L184.983 304.917c-12.724 12.724-12.73 33.328 0 46.058 12.696 12.697 33.356 12.699 46.054-.001l189.465-189.489c25.987-25.989 25.994-68.06.001-94.056-25.931-25.934-68.119-25.932-94.049 0l-225.01 225.039c-39.249 39.252-39.258 102.795-.001 142.057 39.285 39.29 102.885 39.287 142.162-.028A739446.174 739446.174 0 0 1 439.497 238.49c4.686-4.687 12.282-4.684 16.969.004l16.967 16.971c4.685 4.686 4.689 12.279.004 16.965a755654.128 755654.128 0 0 0-195.881 195.996c-58.034 58.092-152.004 58.093-210.048.041z" /></svg>`
                    : `${element.attributes.data_btn_text.textContent}`
                : `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor"><path d="M67.508 468.467c-58.005-58.013-58.016-151.92 0-209.943l225.011-225.04c44.643-44.645 117.279-44.645 161.92 0 44.743 44.749 44.753 117.186 0 161.944l-189.465 189.49c-31.41 31.413-82.518 31.412-113.926.001-31.479-31.482-31.49-82.453 0-113.944L311.51 110.491c4.687-4.687 12.286-4.687 16.972 0l16.967 16.971c4.685 4.686 4.685 12.283 0 16.969L184.983 304.917c-12.724 12.724-12.73 33.328 0 46.058 12.696 12.697 33.356 12.699 46.054-.001l189.465-189.489c25.987-25.989 25.994-68.06.001-94.056-25.931-25.934-68.119-25.932-94.049 0l-225.01 225.039c-39.249 39.252-39.258 102.795-.001 142.057 39.285 39.29 102.885 39.287 142.162-.028A739446.174 739446.174 0 0 1 439.497 238.49c4.686-4.687 12.282-4.684 16.969.004l16.967 16.971c4.685 4.686 4.689 12.279.004 16.965a755654.128 755654.128 0 0 0-195.881 195.996c-58.034 58.092-152.004 58.093-210.048.041z" /></svg>`
            }</span>${element.outerHTML}</span><span class="kwt-file__msg">${"" === element.placeholder ? "or drop files here" : `${element.placeholder}`
            }</span><div class="kwt-file__delete"></div></div></div>`
        );
        var element = element.parents(".kwt-file");

        // Add class on focus and drage enter event.
        element.on("dragenter focus click", ".kwt-file__input", function (e) {
            $(this).parents(".kwt-file__drop-area").addClass("is-active");
        });

        // Remove class on blur and drage leave event.
        element.on("dragleave blur drop", ".kwt-file__input", function (e) {
            $(this).parents(".kwt-file__drop-area").removeClass("is-active");
        });

        // Show filename when change file.
        element.on("change", ".kwt-file__input", function (e) {
            let filesCount = $(this)[0].files.length;
            let textContainer = $(this).next(".kwt-file__msg");
            if (1 === filesCount) {
                let fileName = $(this).val().split("\\").pop();
                textContainer
                    .text(fileName)
                    .next(".kwt-file__delete")
                    .css("display", "block");
            } else if (filesCount > 1) {
                textContainer
                    .text(filesCount + " files selected")
                    .next(".kwt-file__delete")
                    .css("display", "inline-block");
            } else {
                textContainer.text(
                    `${"" === this[0].placeholder
                        ? "or drop files here"
                        : `${this[0].placeholder}`
                    }`
                );
                $(this)
                    .parents(".kwt-file")
                    .find(".kwt-file__delete")
                    .css("display", "none");
            }
        });

        // Delete selected file.
        element.on("click", ".kwt-file__delete", function (e) {
            let deleteElement = $(this);
            deleteElement.parents(".kwt-file").find(`.kwt-file__input`).val(null);
            deleteElement
                .css("display", "none")
                .prev(`.kwt-file__msg`)
                .text(
                    `${"" ===
                        $(this).parents(".kwt-file").find(".kwt-file__input")[0].placeholder
                        ? "or drop files here"
                        : `${$(this).parents(".kwt-file").find(".kwt-file__input")[0].placeholder
                        }`
                    }`
                );
        });
    };

    $.fn.kwtFileUpload = function (e) {
        var _this = $(this);
        $.each(_this, function (index, element) {  
            customDragandDrop(element);
        });
        return this;
    };
})(jQuery);



 function expertise() {
    try {
        fetch('static/js/data/data.json')
        .then(response => response.json())
        .then(data => {
        const contentDiv = document.getElementById('content');
        data.forEach(item => {
            contentDiv.innerHTML += `
            <div class="col-12 col-md-4 p-4">
                <div class="card border-0 ">
                <div class="card-body text-justify-center p-5">
                    <h4 class="fw-bold text-uppercase mb-4">${item.title}</h4>
                    <p class="mb-4 text-secondary">${item.description}</p>
                    <a href="${item.link}" class="fw-bold text-decoration-none link-primary">
                    En savoir plus
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-right-short" viewBox="0 0 16 16">
                        <path fill-rule="evenodd" d="M4 8a.5.5 0 0 1 .5-.5h5.793L8.146 5.354a.5.5 0 1 1 .708-.708l3 3a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708-.708L10.293 8.5H4.5A.5.5 0 0 1 4 8z" />
                    </svg>
                    </a>
                </div>
                </div>
            </div>
            `;
        });
        })
        .catch(error => console.error('Error:', error));
    } catch (error) {
        console.error('message indique ' + error)
    }
    
}



function sendContact() {
    let sendContact = document.getElementById('sendContact');
    let name = document.getElementById('name').value;
    let email = document.getElementById('email').value;
    let compagny = document.getElementById('compagny').value;
    let number = document.getElementById('phone').value;
    let subjet = document.getElementById('subject').value;
    let message = document.getElementById('message').value;


    if (sendContact) {
        sendContact.addEventListener('click', async (event) => {
            event.preventDefault();
            const form = document.querySelector('#contactId');
            document.querySelector('.loading').style.display = 'block';
            const formData = new FormData(form);
            formData.append('name', name);
            formData.append('email', email);
            formData.append('subjet', subjet);
            formData.append('compagny', compagny);
            formData.append('number', number);
            formData.append('message', message);
            const csrfToken = formData.get('csrfmiddlewaretoken');
            try{
                fetch(`Contact`, {
                    method: "POST",
                    cache: "no-cache",
                    headers: {
                        'Accept': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest', //Necessary to work with request.is_ajax()
                        'X-CSRFToken': csrfToken
                    },
                    credentials: "same-origin",
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                      throw new Error('Erreur de requête : ' + response.status);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.status) {
                        document.querySelector('.sent-message').style.display = 'block';

                        // Réinitialiser le formulaire
                        document.querySelector('#contactId').reset();
                    }
                })
                .catch(error => {
                    document.querySelector('.error-message').textContent = 'Une erreur s\'est produite lors de l\'envoi du message.';
                    document.querySelector('.error-message').style.display = 'block';
                })
                .finally(() => {
                    // Masquer le message de chargement une fois que la requête est terminée
                    document.querySelector('.loading').style.display = 'none';
                });;
            }catch(error) {
                console.error('Erreur lors de la requête fetch :', error);
                console.error('Contenu de la réponse :', response.text());
            };
            
        });
    }

}

function postCandidatClient(param) {
    let sendCandidatClient;
    if(param){
        sendCandidatClient=$('#sendClient')
    }else{
        sendCandidatClient=$('#sendCandidat')
    }
    console.log(sendCandidatClient)
    sendCandidatClient.click(function () {
        const csrfToken= $('input[name=csrfmiddlewaretoken]').val()
        var formData = new FormData();
        if (param) {
            formData.append('isClient', param);
            formData.append('company', $('#InputCompagny').val());
            formData.append('firstName', $('#InputfirstNamep').val());
            formData.append('lastName', $('#InputNamep').val());
            formData.append('email', $('#InputEmailp').val());
            formData.append('message', $('#InputMessagep').val());
        } else {
            formData.append('isClient', param);
            formData.append('cv', document.getElementById("InputCv").files[0]);
            formData.append('firstName', $('#InputfirstName').val());
            formData.append('lastName', $('#InputName').val());
            formData.append('email', $('#InputEmail').val());
            formData.append('message', $('#InputMessage').val());
        }

        // Envoyez la requête AJAX
        fetch('Spontaner/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.statut){
                showSuccessAlert(data.message, 'alertContainer', 2000,'alert-success');
                document.querySelector('#formCandidat').reset();
                document.querySelector('#formClient').reset();
            }else{
                showSuccessAlert(data.message, 'alertContainer', 5000,'alert-danger'); 
            }
        })
        .catch(error => {
            console.error('Erreur lors de la requête fetch :', error);
        });
    });

}

function showSuccessAlert(message, containerId,delay,type) {
    var alertDiv = document.createElement('div');
    alertDiv.classList.add('alert', type);
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = message;
    var container = document.getElementById(containerId);
    if (container) {
        container.appendChild(alertDiv);
        setTimeout(function() {
            alertDiv.remove();
        }, delay);
    } else {
        console.error('Container with ID ' + containerId + ' not found.');
    }
}



  




