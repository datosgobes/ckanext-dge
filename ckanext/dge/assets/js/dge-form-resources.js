/*
* Copyright (C) 2026 Entidad Pública Empresarial Red.es
*
* This file is part of "dge (datos.gob.es)".
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 2 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program. If not, see <http://www.gnu.org/licenses/>.
*/
$(document).ready(function(){
    $("#new-distribution-button").on("click", function () {
        $("#resource-edit").slideToggle(300);
    });

    $(".edit-distribution-link").on("click", function (e) {
        let edit = $("#other_resources").val();
        if (edit == ''){
            e.preventDefault();
            alert('Seleccione una Distribucion');
        } else {
            e.preventDefault();
            $("#select-distribution-form").attr("action", edit);
            $("#select-distribution-form").trigger("submit");
        }
    });

    $(".delete-distribution-link").on("click", function (e) {
        let delete_id = $("#other_resources").val();$(".delete-distribution-link").attr("href", "");
        if (delete_id == ''){
            e.preventDefault();
            alert('Seleccione una Distribucion para borrar');
        } else {
            let delete_id = $("#other_resources").find('option:selected').attr('id');
            let delete_url = $("#delete-"+delete_id).val();
            if(delete_url)
                $(".delete-distribution-link").attr("href", delete_url);
        }
    });



});