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

/* Creates a new preview element for a slug field that displays an example of
 * what the slug will look like. Also provides an edit button to toggle back
 * to the original form element.
 *
 * options - An object of plugin options (defaults to slugPreview.defaults).
 *           prefix: An optional prefix to apply before the slug field.
 *           placeholder: Optional placeholder when there is no slug.
 *           i18n: Provide alternative translations for the plugin string.
 *           template: Provide alternative markup for the plugin.
 *
 * Examples
 *
 *   var previews = jQuery('[name=slug]').slugPreview({
 *     prefix: 'example.com/resource/',
 *     placeholder: '<id>',
 *     i18n: {edit: 'éditer'}
 *   });
 *   // previews === preview objects.
 *   // previews.end() === [name=slug] objects.
 *
 * Returns the newly created collection of preview elements..
 */
(function ($, window) {
  var escape = $.url.escape;

  function slugPreview(options) {
    options = $.extend(true, slugPreview.defaults, options || {});

    var collected = this.map(function () {
      var element = $(this);
      var field = element.find('input');
      var preview = $(options.template);
      var value = preview.find('.slug-preview-value');
      var required = $('<div>').append($('.control-required', element).clone()).html();

      function setValue() {
        var val = escape(field.val()) || options.placeholder;
        value.text(val);
      }

      preview.find('strong').html(required + ' ' + options.i18n['URL']);
      preview.find('.slug-preview-prefix').text(options.prefix);
      preview.find('button').text(options.i18n['Edit']).click(function (event) {
        event.preventDefault();
        element.show();
        preview.hide();
      });
      preview.find('#info-url').html(options.i18n['Description']);

      setValue();
      field.on('change', setValue);

      element.after(preview).hide();

      return preview[0];
    });

    // Append the new elements to the current jQuery stack so that the caller
    // can modify the elements. Then restore the originals by calling .end().
    return this.pushStack(collected);
  }

  slugPreview.defaults = {
    prefix: '',
    placeholder: '',
    i18n: {
      'URL': 'URL',
      'Edit': 'Edit',
      'Description': 'Description'
    },
    template: [
      '<div class="slug-preview">',
      '<strong></strong>',
      '<div class="flex flex-column controls editor">',
      '<div class="flex flex-wrap flex-center">',
      '<span class="slug-preview-prefix"></span><span class="slug-preview-value mb-0"></span>',
      '<button class="btn btn-default btn-xs mt-0"></button>',
      '</div>',
      '<div class="flex flex-wrap">',
      '<span id="info-url" class="info-block"></span>',
      '</div>',
      '</div>',
      '</div>'
      
    ].join('\n')
  };

  $.fn.slugPreview = slugPreview;

})(this.jQuery, this);
