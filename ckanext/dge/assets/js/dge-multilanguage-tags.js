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

(function() {
  'use strict';
  
  // Guardar textos originales de los botones al inicializar
  var originalButtonTexts = {};
  
  // Mostrar error inline
  function showInlineError(fieldName, type) {
    var errorClass = type === 'lang' ? '.fluent-error-lang' : '.fluent-error-input';
    var errorElement = document.querySelector('#add-form-' + fieldName + ' ' + errorClass);
    var inputElement = type === 'lang' 
      ? document.getElementById('lang-select-' + fieldName)
      : document.getElementById('new-field-' + fieldName);
    
    if (errorElement) {
      errorElement.style.display = 'block';
    }
    if (inputElement) {
      inputElement.classList.add('error');
    }
  }
  
  // Ocultar error inline
  function hideInlineError(fieldName, type) {
    var errorClass = type === 'lang' ? '.fluent-error-lang' : '.fluent-error-input';
    var errorElement = document.querySelector('#add-form-' + fieldName + ' ' + errorClass);
    var inputElement = type === 'lang' 
      ? document.getElementById('lang-select-' + fieldName)
      : document.getElementById('new-field-' + fieldName);
    
    if (errorElement) {
      errorElement.style.display = 'none';
    }
    if (inputElement) {
      inputElement.classList.remove('error');
    }
  }
  
  // Ocultar todos los errores
  function hideAllErrors(fieldName) {
    hideInlineError(fieldName, 'lang');
    hideInlineError(fieldName, 'input');
  }
  
  // Obtener el primer idioma disponible en el select
  function getFirstAvailableLang(langSelect) {
    var options = Array.from(langSelect.options);
    for (var i = 0; i < options.length; i++) {
      var opt = options[i];
      if (opt.value && opt.style.display !== 'none') {
        return opt.value;
      }
    }
    return '';
  }
  
  // Preseleccionar primer idioma disponible
  function selectFirstAvailableLang(fieldName) {
    var langSelect = document.getElementById('lang-select-' + fieldName);
    if (!langSelect) return;
    
    var firstAvailable = getFirstAvailableLang(langSelect);
    if (firstAvailable) {
      langSelect.value = firstAvailable;
      // Disparar evento change para actualizar label si es necesario
      var event = new Event('change');
      langSelect.dispatchEvent(event);
    }
  }
  
  // Mostrar el formulario de añadir traducción
  window.addTranslationField = function(fieldName) {
    var wrapper = document.querySelector('[data-field-name="' + fieldName + '"]');
    var addForm = document.getElementById('add-form-' + fieldName);
    var showAddBtn = wrapper.querySelector('.fluent-main-field .btn-add-translation');
    
    // Guardar texto original del botón si no está guardado
    if (!originalButtonTexts[fieldName]) {
      originalButtonTexts[fieldName] = showAddBtn.textContent;
    }
    
    // Ocultar errores previos
    hideAllErrors(fieldName);
    
    // Ocultar botón, mostrar formulario
    showAddBtn.style.display = 'none';
    addForm.style.display = 'block';
    
    // Limpiar input y preseleccionar primer idioma
    document.getElementById('new-field-' + fieldName).value = '';
    updateLangOptions(fieldName);
    selectFirstAvailableLang(fieldName);
  };
  
  // Confirmar añadir traducción
  window.confirmAddTranslation = function(fieldName) {
    var langSelect = document.getElementById('lang-select-' + fieldName);
    var newInput = document.getElementById('new-field-' + fieldName);
    var selectedLang = langSelect.value;
    var inputValue = newInput.value.trim();
    
    var hasError = false;
    
    // Validar idioma
    if (!selectedLang) {
      showInlineError(fieldName, 'lang');
      hasError = true;
    } else {
      hideInlineError(fieldName, 'lang');
    }
    
    // Validar traducción
    if (!inputValue) {
      showInlineError(fieldName, 'input');
      newInput.focus();
      hasError = true;
    } else {
      hideInlineError(fieldName, 'input');
    }
    
    if (hasError) return;
    
    var container = document.getElementById('translations-' + fieldName);
    var existingRow = container.querySelector('.translation-row[data-lang="' + selectedLang + '"]');
    
    if (existingRow) {
      var input = existingRow.querySelector('input[name="' + fieldName + '-' + selectedLang + '"]');
      if (input) input.value = inputValue;
      existingRow.style.display = 'flex';
    }
    
    // Limpiar input y errores
    newInput.value = '';
    hideAllErrors(fieldName);
    updateLangOptions(fieldName);
    
    // Verificar si quedan idiomas disponibles
    var remainingLang = getFirstAvailableLang(langSelect);
    
    if (!remainingLang) {
      document.getElementById('add-form-' + fieldName).style.display = 'none';
      var showAddBtn = document.querySelector('[data-field-name="' + fieldName + '"] .fluent-main-field .btn-add-translation');
      showAddBtn.style.display = 'inline-block';
      showAddBtn.disabled = true;
      // Usar el texto guardado o uno por defecto si no existe
      var noMoreLangsText = '{{ _("No hay más idiomas disponibles") }}';
      showAddBtn.textContent = noMoreLangsText;
    } else {
      selectFirstAvailableLang(fieldName);
      newInput.focus();
    }
  };
  
  // Cancelar - oculta el formulario y muestra el botón
  window.cancelAddTranslation = function(fieldName) {
    var wrapper = document.querySelector('[data-field-name="' + fieldName + '"]');
    var addForm = document.getElementById('add-form-' + fieldName);
    var showAddBtn = wrapper.querySelector('.fluent-main-field .btn-add-translation');
    
    // Ocultar errores
    hideAllErrors(fieldName);
    
    addForm.style.display = 'none';
    showAddBtn.style.display = 'inline-block';
    showAddBtn.disabled = false;
    
    // Restaurar el texto original guardado
    if (originalButtonTexts[fieldName]) {
      showAddBtn.textContent = originalButtonTexts[fieldName];
    }
    
    // Limpiar inputs
    document.getElementById('new-field-' + fieldName).value = '';
    document.getElementById('lang-select-' + fieldName).value = '';
  };
  
  // Eliminar traducción
  window.removeTranslationField = function(btn) {
    var row = btn.closest('.translation-row');
    var wrapper = row.closest('.fluent-field-wrapper');
    var fieldName = wrapper.getAttribute('data-field-name');
    var lang = row.getAttribute('data-lang');
    
    // Limpiar el input
    var input = row.querySelector('input');
    if (input) input.value = '';
    
    // Ocultar la fila
    row.style.display = 'none';
    
    // Si el formulario está visible, actualizar opciones
    var addForm = document.getElementById('add-form-' + fieldName);
    var langSelect = document.getElementById('lang-select-' + fieldName);
    
    if (addForm.style.display !== 'none') {
      hideAllErrors(fieldName);
      updateLangOptions(fieldName);
      selectFirstAvailableLang(fieldName);
    } else {
      var showAddBtn = wrapper.querySelector('.fluent-main-field .btn-add-translation');
      showAddBtn.style.display = 'inline-block';
      showAddBtn.disabled = false;
      // Restaurar texto original si existe
      if (originalButtonTexts[fieldName]) {
        showAddBtn.textContent = originalButtonTexts[fieldName];
      }
    }
    
    updateLangOptions(fieldName);
  };
  
  // Actualizar opciones de idioma disponibles
  function updateLangOptions(fieldName) {
    var container = document.getElementById('translations-' + fieldName);
    var langSelect = document.getElementById('lang-select-' + fieldName);
    
    if (!container || !langSelect) return;
    
    var usedLangs = Array.from(container.querySelectorAll('.translation-row:not([style*="none"])'))
                         .map(function(r) { return r.getAttribute('data-lang'); });
    
    Array.from(langSelect.options).forEach(function(option) {
      if (!option.value) return;
      option.style.display = (usedLangs.indexOf(option.value) !== -1) ? 'none' : 'block';
    });
  }
  
  // Inicialización
  function initFluentFields() {
    document.querySelectorAll('.fluent-field-wrapper').forEach(function(wrapper) {
      var fieldName = wrapper.getAttribute('data-field-name');
      if (fieldName) {
        // Guardar texto original del botón al inicializar
        var showAddBtn = wrapper.querySelector('.fluent-main-field .btn-add-translation');
        if (showAddBtn && !originalButtonTexts[fieldName]) {
          originalButtonTexts[fieldName] = showAddBtn.textContent;
        }
        updateLangOptions(fieldName);
      }
    });
  }
  
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFluentFields);
  } else {
    initFluentFields();
  }
})();