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
  function initMultiSelect(multiSelect) {
    if (!multiSelect || multiSelect.__initialized) return;
    multiSelect.__initialized = true;

    const trigger = multiSelect.querySelector(".multi-select__trigger");
    const dropdown = multiSelect.querySelector(".multi-select__dropdown");
    const options = multiSelect.querySelectorAll(".multi-select__option");
    const chipsContainer = multiSelect.querySelector(".multi-select__chips");
    const nativeSelect = multiSelect.querySelector(".multi-select__native");

    function getSelectedValues() {
      return Array.from(nativeSelect.options)
        .filter((o) => o.selected)
        .map((o) => o.value);
    }

    function setOptionState(value, selected) {
      options.forEach((option) => {
        if (option.dataset.value === value) {
          option.classList.toggle("is-selected", selected);
        }
      });
    }

    function syncDropdownFromSelect() {
      Array.from(nativeSelect.options).forEach((opt) => {
        setOptionState(opt.value, opt.selected);
      });
    }

    function renderChips() {
      const selected = getSelectedValues();

      chipsContainer.innerHTML = "";

      if (selected.length === 0) {
        multiSelect.classList.remove("has-selection");
      } else {
        multiSelect.classList.add("has-selection");
      }

      selected.forEach((value) => {
        const option = Array.from(options).find(
          (o) => o.dataset.value === value
        );

        if (!option) return;

        const label = option.textContent.trim();

        const chip = document.createElement("div");
        chip.className = "multi-select__chip";
        chip.textContent = label;
        chip.tabIndex = 0;
        chip.setAttribute("role", "button");
        chip.setAttribute("aria-label", `Eliminar ${label}`);

        chip.addEventListener("click", function (e) {
          e.stopPropagation();
          deselectOption(value);
        });

        chip.addEventListener("keydown", function (e) {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            e.stopPropagation();
            deselectOption(value);
          }
        });

        const remove = document.createElement("span");
        remove.className = "remove-chip";
        remove.textContent = "×";

        chip.appendChild(remove);
        chipsContainer.appendChild(chip);
      });
    }

    function deselectOption(value) {
      Array.from(nativeSelect.options).forEach((opt) => {
        if (opt.value === value) {
          opt.selected = false;
        }
      });

      setOptionState(value, false);

      nativeSelect.dispatchEvent(new Event("change", { bubbles: true }));
    }

    function selectOption(value) {
      Array.from(nativeSelect.options).forEach((opt) => {
        if (opt.value === value) {
          opt.selected = true;
        }
      });

      setOptionState(value, true);

      nativeSelect.dispatchEvent(new Event("change", { bubbles: true }));
    }

    function toggleOption(value) {
      const opt = Array.from(nativeSelect.options).find(
        (o) => o.value === value
      );

      if (!opt) return;

      if (opt.selected) {
        deselectOption(value);
      } else {
        selectOption(value);
      }
    }

    function adjustDropdownHeight() {
      const option = dropdown.querySelector(".multi-select__option");

      if (option) {
        const h = option.offsetHeight;
        dropdown.style.maxHeight = `${h * 4.5}px`;
      }
    }

    trigger.addEventListener("click", function () {
      const isOpen = multiSelect.classList.toggle("is-open");

      if (isOpen) {
        adjustDropdownHeight();
      } else {
        dropdown.style.maxHeight = null;
      }
    });

    options.forEach((option) => {
      option.addEventListener("click", function () {
        toggleOption(option.dataset.value);
      });
    });

    nativeSelect.addEventListener("change", function () {
      syncDropdownFromSelect();
      renderChips();
    });

    document.addEventListener("click", (e) => {
      if (!multiSelect.contains(e.target)) {
        multiSelect.classList.remove("is-open");
        dropdown.style.maxHeight = null;
      }
    });

    syncDropdownFromSelect();
    renderChips();
  }

  function boot() {
    document
      .querySelectorAll(
        ".multiple-select-spatial [data-component='multi-select']"
      )
      .forEach(initMultiSelect);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
