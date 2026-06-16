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
  function parseJSONAttr(el, attr, fallback) {
    try {
      var raw = el.getAttribute(attr);
      if (!raw) return fallback;
      return JSON.parse(raw);
    } catch (e) {
      return fallback;
    }
  }

  function reinitMarkdown(containerEl) {
    try {
      if (window.ckan && window.ckan.module && window.jQuery) {
        window.jQuery(containerEl).find('[data-module]').each(function () {
          window.ckan.module.initializeElement(this);
        });
      }
    } catch (e) {}
  }

  function escapeRegExp(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function removeFieldKeyNoise(root) {
    var fieldName = root.getAttribute('data-field-name');
    if (!fieldName) return;

    var re = new RegExp('^\\*?\\s*' + escapeRegExp(fieldName) + '\\-[a-z]{2}\\s*$', 'i');

    root.querySelectorAll('.dge-md-wrap *').forEach(function (el) {
      if (!el || !el.textContent) return;
      var txt = el.textContent.trim();
      if (!txt) return;
      if (re.test(txt)) {
        el.remove();
      }
    });
  }

  function buildInputHTML(uiType, fieldName, lang, placeholder, value) {
    var safePlaceholder = (placeholder || '').replaceAll('"', '&quot;');
    var safeValue = (value || '');
    if (uiType === 'text') {
      return (
        '<div class="controls">' +
          '<input type="text"' +
            ' id="field-' + fieldName + '-' + lang + '"' +
            ' name="' + fieldName + '-' + lang + '"' +
            ' class="form-control control-large"' +
            ' placeholder="' + safePlaceholder + '"' +
            ' value="' + safeValue.replaceAll('"', '&quot;') + '"' +
          ' />' +
        '</div>'
      );
    }
    safeValue = safeValue.replace(/<\/textarea>/gi, '<\\/textarea>');
    return (
      '<div class="dge-md-wrap">' +
        '<textarea id="field-' + fieldName + '-' + lang + '"' +
          ' name="' + fieldName + '-' + lang + '"' +
          ' class="form-control control-medium"' +
          ' placeholder="' + safePlaceholder + '"' +
          ' rows="6">' + safeValue + '</textarea>' +
      '</div>'
    );
  }

  function init(root) {
    if (!root || root.__mlInit) return;
    root.__mlInit = true;

    var reqLang = root.getAttribute('data-required-lang');
    var fieldName = root.getAttribute('data-field-name') || '';
    var uiType = root.getAttribute('data-ui-type') || 'markdown';
    var baseLabel = root.getAttribute('data-base-label') || '';

    var langNames = parseJSONAttr(root, 'data-lang-names', {});
    var placeholders = parseJSONAttr(root, 'data-placeholders', {});

    var extra = root.querySelector('.fluent-extra');
    var list = root.querySelector('.fluent-translations-list');
    var showAddBtn = root.querySelector('.fluent-show-add-btn');

    var select = root.querySelector('.fluent-lang-select');
    var addBtn = root.querySelector('.fluent-add-btn');
    var newInput = root.querySelector('.fluent-new-value');
    var newLabel = root.querySelector('.fluent-new-label');
    var addBlock = root.querySelector('.fluent-add-translation');
    var cancelBtn = root.querySelector('.fluent-cancel-btn');

    var tplEl = root.querySelector('.fluent-translation-template');
    var tpl = tplEl ? tplEl.textContent : '';

    function hideAddForm() {
      if (addBlock) {
        addBlock.style.display = 'none';
      }
      if (showAddBtn) showAddBtn.style.display = '';
      if (newInput) newInput.value = '';
    }

    function showAddForm() {
      if (addBlock) {
        addBlock.style.display = '';
      }
      if (extra) {
        extra.classList.remove('is-hidden');
        extra.style.display = '';
      }
      if (showAddBtn) showAddBtn.style.display = 'none';
      refresh();
      if (newInput) newInput.focus();
    }

    function hideExtra() {
      if (extra) {
        extra.classList.add('is-hidden');
        extra.style.display = 'none';
      }
      if (showAddBtn) showAddBtn.style.display = '';
      if (newInput) newInput.value = '';
    }

    function showExtra() {
      if (extra) {
        extra.classList.remove('is-hidden');
        extra.style.display = '';
      }
      showAddForm();
    }

    function updateNewUI() {
      if (!select) return;
      var lang = select.value;
      if (!lang) return;

      if (newLabel) newLabel.textContent = baseLabel + " (" + (langNames[lang] || lang) + ")";
      if (newInput) {
        newInput.placeholder = placeholders[lang] || "";
        newInput.disabled = false;
      }
    }

    function refresh() {
      if (!select || !addBtn || !newInput || !newLabel) return;

      var empty = select.options.length === 0;
      select.disabled = empty;
      addBtn.disabled = empty;

      if (empty) {
        newLabel.textContent = "";
        newInput.placeholder = "";
        newInput.value = "";
        newInput.disabled = true;

        if (addBlock) {
          addBlock.style.display = 'none';
        }
      } else {
        if (addBlock) {
          addBlock.style.display = '';
        }
        updateNewUI();
      }
    }

    // Estado inicial: mostrar lista si tiene items, ocultar solo el form de añadir
    var hasTranslations = list && list.children.length > 0;
    if (hasTranslations) {
      // Hay traducciones guardadas: mostrar la lista pero ocultar el form de añadir
      if (extra) {
        extra.classList.remove('is-hidden');
        extra.style.display = '';
      }
      if (addBlock) addBlock.style.display = 'none';
      if (showAddBtn) showAddBtn.style.display = '';
    } else {
      // No hay traducciones: ocultar todo como antes
      hideExtra();
    }

    removeFieldKeyNoise(root);

    if (showAddBtn) showAddBtn.addEventListener('click', showExtra);
    
    if (cancelBtn) {
      cancelBtn.addEventListener('click', hideAddForm);
    }
    
    if (select) select.addEventListener('change', updateNewUI);

    if (addBtn) {
      addBtn.addEventListener('click', function () {
        if (!select || select.options.length === 0) return;

        var lang = select.value;
        var value = (newInput.value || '').trim();
        if (!lang) return;
        if (!value) { newInput.focus(); return; }

        if (list.querySelector('.fluent-translation-item[data-lang="' + lang + '"]')) return;

        var inputHTML = buildInputHTML(uiType, fieldName, lang, placeholders[lang] || '', value);

        var html = tpl
          .replaceAll('__LANG__', lang)
          .replaceAll('__LANGNAME__', (langNames[lang] || lang))
          .replace('__INPUT__', inputHTML);

        var div = document.createElement('div');
        div.innerHTML = html.trim();
        var node = div.firstChild;
        list.appendChild(node);

        var opt = select.querySelector('option[value="' + lang + '"]');
        if (opt) opt.remove();

        newInput.value = "";
        refresh();

        if (uiType !== 'text') reinitMarkdown(node);
        removeFieldKeyNoise(root);
      });
    }

    root.addEventListener('click', function (e) {
      var btn = e.target.closest('.fluent-remove-translation');
      if (!btn) return;

      var item = btn.closest('.fluent-translation-item');
      if (!item) return;

      var lang = item.getAttribute('data-lang');
      item.remove();

      if (lang && lang !== reqLang && select) {
        if (!select.querySelector('option[value="' + lang + '"]')) {
          var opt = document.createElement('option');
          opt.value = lang;
          opt.textContent = (langNames[lang] || lang);
          select.appendChild(opt);
        }
      }

      refresh();
      removeFieldKeyNoise(root);
    });

    refresh();
  }

  function boot() {
    document.querySelectorAll('.fluent-multilang-field').forEach(init);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();