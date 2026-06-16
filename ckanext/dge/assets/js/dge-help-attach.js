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
  function attachHelp(root) {
    if (!root || root.__dgeHelpAttached) return;
    root.__dgeHelpAttached = true;

    var source = root.querySelector('.dge-help-attach-source');
    if (!source) return;

    var help = source.querySelector('.dge-help');
    if (!help) return;

    // Busca el primer label real del componente
    var label = root.querySelector('label.control-label');
    if (!label) return;

    // Evita duplicados
    if (label.querySelector('.dge-help')) return;

    label.appendChild(help);
  }

  function boot() {
    document.querySelectorAll('.dge-help-attach').forEach(attachHelp);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();