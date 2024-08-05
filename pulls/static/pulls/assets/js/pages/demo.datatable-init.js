$(document).ready(function() {
    "use strict";
    $('#basic-datatable-cv').DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": {
            "url": "get_All",
            "type": "GET",
            "data": {
                "is_type": 'cv'  
            },
            "dataSrc": "data",  
            "error": function (xhr, error, thrown) {
                console.error('Ajax error:', thrown);

            }
        },

        "columns": [
            { "data": "name", 'orderable':true,'searchable':true ,'render': function(data, type, row, meta){
                return `<a class="" href="/leads_cvs/cv-tech/${row.id}/" target=_blank ><h5 class="text-muted fw-normal mt-0 text-truncate" title="${data}">${reduceStr(String(data))}</h5> </a>`
            }},
            { "data": null ,'orderable':true,'searchable':true ,
                "render": function(data, type, row, meta) {
                            return '<p class="mb-0">' + row.nom + ' ' + row.prenom + '</p>' +
                                    '<span class="font-12">' + row.email_utilisateur + '</span>';
                    },
            },
            { "data": "create_date" ,'orderable':true,'searchable':true ,},
            { "data": "write_date" ,'orderable':true,'searchable':true ,},  
            { "data": null,'orderable':false,'searchable':false ,'render': function(data,type,row ,meta){
                return `<div class="btn-group dropdown">
                            <a href="#" class="table-action-btn dropdown-toggle arrow-none btn btn-light btn-xs" data-bs-toggle="dropdown" aria-expanded="false"><i class="mdi mdi-dots-horizontal"></i></a>
                            <div class="dropdown-menu dropdown-menu-end">
                                <a class="dropdown-item delete-file" href="/leads_cvs/cv_tech/${row.id}/" data-id="${row.id}"><i class="dripicons-search"></i>  Détails du CV</a>
                                <a class="dropdown-item rename-file" href="#" data-name="{{ cv.name }}" data-id="{{ cv.id }}"><i class="mdi mdi-pencil me-2 text-muted vertical-middle"></i>Renommer</a>
                                <a class="dropdown-item delete-file" href="#" data-id="{{ cv.id }}"><i class="mdi mdi-delete me-2 text-muted vertical-middle"></i>Retirer</a>
                            </div>
                        </div>`
            }},  
        ],
        "language": {
            url: "//cdn.datatables.net/plug-ins/1.10.21/i18n/French.json",
            "paginate": {
                "previous": "<i class='mdi mdi-chevron-left'></i>",
                "next": "<i class='mdi mdi-chevron-right'></i>"
            }
        },
        "drawCallback": function() {
            $(".dataTables_paginate > .pagination").addClass("pagination-rounded");
        }
    });
    



    $('#basic-datatable-factures').DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": {
            "url": "get_All",
            "type": "GET",
            "data": {
                "is_type": 'fac'  
            },
            "dataSrc": "data",  
            "error": function (xhr, error, thrown) {
                console.error('Ajax error:', thrown);

            }
        },

        "columns": [
            { "data": "name", 'orderable':true,'searchable':true ,'render': function(data, type, row, meta){
                return `<a class="" href="/leads_cvs/facturation/${row.id}/" target=_blank ><h5 class="text-muted fw-normal mt-0 text-truncate" title="${data}">${reduceStr(String(data))}</h5> </a>`
            }},
            { "data": null ,'orderable':true,'searchable':true ,
                "render": function(data, type, row, meta) {
                            return '<p class="mb-0">' + row.nom + ' ' + row.prenom + '</p>' +
                                    '<span class="font-12">' + row.email_utilisateur + '</span>';
                    },
            },
            { "data": "create_date" ,'orderable':true,'searchable':true ,},
            { "data": "write_date" ,'orderable':true,'searchable':true ,},  
            { "data": null,'orderable':false,'searchable':false ,'render': function(data,type,row ,meta){
                return `<div class="btn-group dropdown">
                            <a href="#" class="table-action-btn dropdown-toggle arrow-none btn btn-light btn-xs" data-bs-toggle="dropdown" aria-expanded="false"><i class="mdi mdi-dots-horizontal"></i></a>
                            <div class="dropdown-menu dropdown-menu-end">
                                <a class="dropdown-item delete-file" href="/leads_cvs/facturation/${row.id}/" data-id="${row.id}"><i class="dripicons-search"></i>  Détails du CV</a>
                                <a class="dropdown-item rename-file" href="#" data-name="{{ cv.name }}" data-id="{{ cv.id }}"><i class="mdi mdi-pencil me-2 text-muted vertical-middle"></i>Renommer</a>
                                <a class="dropdown-item delete-file" href="#" data-id="{{ cv.id }}"><i class="mdi mdi-delete me-2 text-muted vertical-middle"></i>Retirer</a>
                            </div>
                        </div>`
            }},  
        ],
        "language": {
            url: "//cdn.datatables.net/plug-ins/1.10.21/i18n/French.json",
            "paginate": {
                "previous": "<i class='mdi mdi-chevron-left'></i>",
                "next": "<i class='mdi mdi-chevron-right'></i>"
            }
        },
        "drawCallback": function() {
            $(".dataTables_paginate > .pagination").addClass("pagination-rounded");
        }
    });
    
    $("#basic-datatable").DataTable({
        keys: !0,
        language: {
            paginate: {
                previous: "<i class='mdi mdi-chevron-left'>",
                next: "<i class='mdi mdi-chevron-right'>"
            }
        },
        drawCallback: function() {
            $(".dataTables_paginate > .pagination").addClass("pagination-rounded")
        }
    });

    var a = $("#datatable-buttons").DataTable({
        lengthChange: !1,
        buttons: ["copy", "print"],
        language: {
            paginate: {
                previous: "<i class='mdi mdi-chevron-left'>",
                next: "<i class='mdi mdi-chevron-right'>"
            }
        },
        drawCallback: function() {
            $(".dataTables_paginate > .pagination").addClass("pagination-rounded")
        }
    });
    $("#selection-datatable").DataTable({
        select: {
            style: "multi"
        },
        language: {
            paginate: {
                previous: "<i class='mdi mdi-chevron-left'>",
                next: "<i class='mdi mdi-chevron-right'>"
            }
        },
        drawCallback: function() {
            $(".dataTables_paginate > .pagination").addClass("pagination-rounded")
        }
    }),
    a.buttons().container().appendTo("#datatable-buttons_wrapper .col-md-6:eq(0)"),
    $("#alternative-page-datatable").DataTable({
        pagingType: "full_numbers",
        drawCallback: function() {
            $(".dataTables_paginate > .pagination").addClass("pagination-rounded")
        }
    }),
    $("#scroll-vertical-datatable").DataTable({
        scrollY: "350px",
        scrollCollapse: !0,
        paging: !1,
        language: {
            paginate: {
                previous: "<i class='mdi mdi-chevron-left'>",
                next: "<i class='mdi mdi-chevron-right'>"
            }
        },
        drawCallback: function() {
            $(".dataTables_paginate > .pagination").addClass("pagination-rounded")
        }
    }),
    $("#scroll-horizontal-datatable").DataTable({
        scrollX: !0,
        language: {
            paginate: {
                previous: "<i class='mdi mdi-chevron-left'>",
                next: "<i class='mdi mdi-chevron-right'>"
            }
        },
        drawCallback: function() {
            $(".dataTables_paginate > .pagination").addClass("pagination-rounded")
        }
    }),
    $("#complex-header-datatable").DataTable({
        language: {
            paginate: {
                previous: "<i class='mdi mdi-chevron-left'>",
                next: "<i class='mdi mdi-chevron-right'>"
            }
        },
        drawCallback: function() {
            $(".dataTables_paginate > .pagination").addClass("pagination-rounded")
        },
        columnDefs: [{
            visible: !1,
            targets: -1
        }]
    }),
    $("#row-callback-datatable").DataTable({
        language: {
            paginate: {
                previous: "<i class='mdi mdi-chevron-left'>",
                next: "<i class='mdi mdi-chevron-right'>"
            }
        },
        drawCallback: function() {
            $(".dataTables_paginate > .pagination").addClass("pagination-rounded")
        },
        createdRow: function(a, e, t) {
            15e4 < +e[5].replace(/[\$,]/g, "") && $("td", a).eq(5).addClass("text-danger")
        }
    }),
    $("#state-saving-datatable").DataTable({
        stateSave: !0,
        language: {
            paginate: {
                previous: "<i class='mdi mdi-chevron-left'>",
                next: "<i class='mdi mdi-chevron-right'>"
            }
        },
        drawCallback: function() {
            $(".dataTables_paginate > .pagination").addClass("pagination-rounded")
        }
    }),
    $(".dataTables_length select").addClass("form-select form-select-sm"),
    $(".dataTables_length label").addClass("form-label")
});

function reduceStr(str) {
    // Convert the input to a string in case it's not already

    str = String(str);
    // Define the substring to check for
    const char = '.pdf';
    
    if (str.length<20)  {
        return str;
    
    }
    // Check if the string contains ".pdf"
    if (str.includes(char)) {
        // Extract the part before ".pdf"
        let nom = str.split(char)[0];
        // Truncate if the length is greater than 20
        if (nom.length > 20) {
            return nom.substring(0, 17) +char;
        }
        return nom + char
    } else {
        // Truncate if the length is greater than 20
        if (str.length > 20) {
            return str.substring(0, 19) 
        }
        return str 
    }
}