/*
* Copyright (C) 2025 Entidad Pública Empresarial Red.es
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

// Enable JavaScript's strict mode. Strict mode catches some common
// programming errors and throws exceptions, prevents some unsafe actions from
// being taken, and disables some confusing and bad JavaScript features.
"use strict";

ckan.module('dge_main', function ($, _) {
  return {
    initialize: function () {
      console.log("I've been initialized for element: ", this.el);
      var browserLocale = window.navigator.userLanguage || window.navigator.language;
      // Convert all datetimes to the users timezone
      jQuery('.automatic-local-datetime').each(function() {
          moment.locale(browserLocale);
          var date = moment(jQuery(this).data('datetime'));
          if (date.isValid()) {
              jQuery(this).html(date.format("L - LT ([UTC]Z)")); 
          }
          jQuery(this).show();
      })
    }
  };
});

ckan.module('toggle-tags', function($, _) {
  return {
    options: {
      view_more: 'View more',
      view_less: 'View less',
    },
    initialize: function() {
      var options = this.options;
      var self = this;
      var button = this.el;  // `this.el` hace referencia al botón
      var moreTags = $('#more-tags');
      button.on('click', function() {
        if (moreTags.is(':visible')) {
          moreTags.hide();
          button.text(options.view_more);
        } else {
          moreTags.show();
          button.text(options.view_less);
        }
      });
    }
  };
});
