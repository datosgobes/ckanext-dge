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
  function closeAll(exceptPopover) {
    document.querySelectorAll('.dge-help-popover.is-open').forEach(function (p) {
      if (exceptPopover && p === exceptPopover) return;
      p.classList.remove('is-open');
      p.setAttribute('aria-hidden', 'true');

      var trigger = p.closest('.dge-help')?.querySelector('.dge-help-trigger');
      if (trigger) trigger.setAttribute('aria-expanded', 'false');
    });
  }

  function toggle(trigger) {
    var wrap = trigger.closest('.dge-help');
    if (!wrap) return;

    var popId = trigger.getAttribute('aria-controls');
    var pop = popId ? document.getElementById(popId) : wrap.querySelector('.dge-help-popover');
    if (!pop) return;

    var open = pop.classList.contains('is-open');
    if (open) {
      pop.classList.remove('is-open');
      pop.setAttribute('aria-hidden', 'true');
      trigger.setAttribute('aria-expanded', 'false');
      return;
    }

    closeAll(pop);
    pop.classList.add('is-open');
    pop.setAttribute('aria-hidden', 'false');
    trigger.setAttribute('aria-expanded', 'true');
  }

  // Click en el ?
  document.addEventListener('click', function (e) {
    var t = e.target.closest('.dge-help-trigger');
    if (t) {
      e.preventDefault();
      toggle(t);
      return;
    }

    // Click fuera: cerrar
    var inside = e.target.closest('.dge-help');
    if (!inside) closeAll(null);
  });

  // ESC: cerrar
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeAll(null);
  });
})();