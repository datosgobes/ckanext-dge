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
  
  // Esperar a que el DOM esté listo
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initRdfFormat);
  } else {
    initRdfFormat();
  }
  
  function initRdfFormat() {
    var select = document.getElementById('field-rdf-format');
    var hidden = document.getElementById('field-config');
    // AÑADIDO: Referencia al campo URL
    var urlField = document.getElementById('field-url');
    
    if (!select || !hidden) {
      console.error('RDF Format elements not found');
      return;
    }
    
    // Función para actualizar el campo oculto manteniendo otras propiedades
    function updateHiddenField() {
      var format = select.value;
      // AÑADIDO: Obtener URL actual
      var url = urlField ? urlField.value.trim() : '';
      var currentConfig = {};
      
      // Intentar parsear el valor actual del campo oculto
      try {
        var existingValue = hidden.value;
        if (existingValue && existingValue.trim() !== '' && existingValue !== '{}') {
          currentConfig = JSON.parse(existingValue);
          // Asegurar que sea un objeto
          if (typeof currentConfig !== 'object' || currentConfig === null) {
            currentConfig = {};
          }
        }
      } catch (e) {
        // Si no es JSON válido, empezar con objeto vacío
        console.log('Existing config is not valid JSON, starting fresh');
        currentConfig = {};
      }
      
      // Actualizar solo la propiedad rdf_format
      currentConfig.rdf_format = format;
      // AÑADIDO: Incluir URL en el config como full_rdf_url
      if (url) {
        currentConfig.full_rdf_url = url;
      } else {
        delete currentConfig.full_rdf_url;
      }
      
      // Guardar de vuelta como JSON compacto (sin espacios) sin ordenar claves
      hidden.value = JSON.stringify(currentConfig);
    }
    
    // Al cambiar el select, actualizar el campo oculto
    select.addEventListener('change', updateHiddenField);
    // AÑADIDO: Escuchar cambios en URL también
    if (urlField) {
      urlField.addEventListener('input', updateHiddenField);
      urlField.addEventListener('change', updateHiddenField);
    }
    
    // Inicializar al cargar la página
    initializeSelect();
    
    function initializeSelect() {
      var currentValue = hidden.value;
      var currentFormat = 'xml';
      // AÑADIDO: Extraer URL existente si la hay
      var currentUrl = urlField ? urlField.value.trim() : '';
      
      // Intentar extraer rdf_format del JSON existente
      try {
        if (currentValue && currentValue.trim() !== '' && currentValue !== '{}') {
          var config = JSON.parse(currentValue);
          if (config && typeof config === 'object') {
            if (config.rdf_format) {
              currentFormat = config.rdf_format;
            }
            // Eliminado: ya no se restaura URL desde config. La fuente de verdad es urlField.
            // Eliminado: migración de config.url. Gestionar en backend si es necesario.
          }
        }
      } catch (e) {
        // Si no es JSON válido, buscar con regex o string matching
        var match = currentValue.match(/"rdf_format"\s*:\s*"([^"]+)"/);
        if (match) {
          currentFormat = match[1];
        } else if (currentValue === 'xml' || currentValue === 'ttl' || currentValue === 'json-ld') {
          currentFormat = currentValue;
        }
      }
      
      // Validar que el formato sea uno de los permitidos
      var validFormats = ['xml', 'ttl', 'json-ld'];
      if (validFormats.indexOf(currentFormat) === -1) {
        currentFormat = 'xml';
      }
      
      // Establecer el valor del select
      select.value = currentFormat;
      
      // Si el campo oculto estaba vacío o inválido, inicializarlo
      if (!currentValue || currentValue.trim() === '' || currentValue === '{}') {
        // AÑADIDO: Incluir URL en la inicialización como full_rdf_url
        var initialConfig = {rdf_format: 'xml'};
        if (currentUrl) initialConfig.full_rdf_url = currentUrl;
        hidden.value = JSON.stringify(initialConfig);
      } else {
        // Asegurar que el JSON esté actualizado y compacto
        updateHiddenField();
      }
    }
  }
})();