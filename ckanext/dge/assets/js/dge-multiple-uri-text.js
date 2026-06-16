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

this.ckan.module('dge-multiple-uri-text', function ($) {
  return {
    initialize: function () {
      var container = this.el;
      var fieldName = container.data('field-name');
      var labelText = container.data('label') || 'URL';
      var placeholderText = container.data('placeholder') || '';
      
      // Manejar click en "Añadir"
      container.on('click', '.btn-add-multiple-field', function (e) {
        e.preventDefault();
        
        var $btn = $(this);
        var nextIndex = parseInt($btn.data('next-index')) || 2;
        
        var wrapperId = 'wrapper-' + fieldName + '-' + nextIndex;
        var inputId = 'field-' + fieldName + '-' + nextIndex;
        var inputName = fieldName + '-' + nextIndex;
        
        var newFieldHtml = [
          '<div class="url-field-wrapper" id="' + wrapperId + '" data-index="' + nextIndex + '">',
            '<div class="control-group control-medium div-' + fieldName + '">',
              '<div class="controls">',
                '<input id="' + inputId + '" type="text" name="' + inputName + '" value="" placeholder="' + placeholderText + '" class="form-control">',
              '</div>',
            '</div>',
            '<button type="button" class="btn btn-danger btn-remove-field" data-wrapper-id="' + wrapperId + '" title="Remove">',
              '<i class="fa fa-trash"></i>',
            '</button>',
          '</div>'
        ].join('');
        
        container.find('.multi-add-field').before(newFieldHtml);
        
        $btn.data('next-index', nextIndex + 1);
      });
      
      // Manejar click en "Eliminar"
      container.on('click', '.btn-remove-field', function (e) {
        e.preventDefault();
        
        var wrapperId = $(this).data('wrapper-id');
        $('#' + wrapperId).remove();
      });
    }
  };
});