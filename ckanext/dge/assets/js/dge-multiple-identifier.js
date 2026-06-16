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

(function () {
  function initMultipleIdentifier(wrapper) {
    if (!wrapper || wrapper.dataset.initialized === "true") {
      return;
    }

    wrapper.dataset.initialized = "true";

    var list = wrapper.querySelector(".js-multiple-identifier-list");
    var addButton = wrapper.querySelector(".js-add-identifier");

    if (!list || !addButton) {
      return;
    }

    function updateIds() {
      var fieldName = list.getAttribute("data-field-name") || "identifier";
      var rows = list.querySelectorAll(".multiple-identifier-row");

      rows.forEach(function (row, index) {
        var input = row.querySelector("input");
        if (input) {
          input.id = "field-" + fieldName + "-" + index;
        }
      });
    }

    function buildRow() {
      var fieldName = list.getAttribute("data-field-name") || "identifier";
      var placeholder = list.getAttribute("data-placeholder") || "";

      var row = document.createElement("div");
      row.className = "multiple-identifier-row";

      row.innerHTML =
        '<input type="text"' +
        ' name="' +
        fieldName +
        '"' +
        ' value=""' +
        ' placeholder="' +
        placeholder.replace(/"/g, "&quot;") +
        '"' +
        ' class="form-control multiple-identifier-input" />' +
        '<button type="button" class="btn btn-danger js-remove-identifier"><i class="fa fa-trash"></i></button>';

      return row;
    }

    addButton.addEventListener("click", function (e) {
      e.preventDefault();
      list.appendChild(buildRow());
      updateIds();
    });

    wrapper.addEventListener("click", function (e) {
      var removeBtn = e.target.closest(".js-remove-identifier");
      if (!removeBtn) {
        return;
      }

      e.preventDefault();

      var rows = list.querySelectorAll(".multiple-identifier-row");
      var row = removeBtn.closest(".multiple-identifier-row");

      if (rows.length > 1 && row) {
        row.remove();
      } else if (row) {
        var input = row.querySelector("input");
        if (input) {
          input.value = "";
        }
      }

      updateIds();
    });

    updateIds();
  }

  function initAllMultipleIdentifierFields() {
    var wrappers = document.querySelectorAll(".js-multiple-identifier-wrapper");
    wrappers.forEach(initMultipleIdentifier);
  }

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      initAllMultipleIdentifierFields
    );
  } else {
    initAllMultipleIdentifierFields();
  }
})();
