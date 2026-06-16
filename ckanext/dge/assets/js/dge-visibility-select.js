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
this.ckan.module('visibilidad-select', function ($) {
  return {
    initialize: function () {
      var $select = this.$el;
      var hintId = $select.attr('id') + '-hint';
      var $hint = $('<div/>', {
        id: hintId,
        class: 'visibilidad-hint'
      });

      $select.after($hint);

      function updateState() {
        var value = $select.val();

        $select.removeClass('is-publico is-privado');
        $hint.removeClass('is-publico is-privado');

        if (value === 'publico') {
          $select.addClass('is-publico');
          $hint.addClass('is-publico');
          $hint.text('El conjunto de datos será visible para los usuarios.');
        } else if (value === 'privado') {
          $select.addClass('is-privado');
          $hint.addClass('is-privado');
          $hint.text('El conjunto de datos tendrá acceso restringido.');
        } else {
          $hint.text('');
        }
      }

      $select.on('change', updateState);
      updateState();
    }
  };
});