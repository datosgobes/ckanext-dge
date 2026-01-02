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

window.addEventListener("DOMContentLoaded", () => {

  const harvester_delete_clear_link = document.getElementById('harvester_delete_clear');
  const harvester_delete_link = document.getElementById('harvester_delete');
  const harvester_clear_link = document.getElementById('harvester_clear');

  // Adding dgeHarvester.delete with clear True success message
  if (harvester_delete_clear_link) {
    harvester_delete_clear_link.addEventListener('click', function (event) {
      event.preventDefault();
      const success_clear_message = this.dataset.successMessage;
      if (success_clear_message) {
        localStorage.setItem('success_harvest_clear_message', success_clear_message);
      }
    });
  }

  // Adding dgeHarvester.delete success message
  if (harvester_delete_link) {
    harvester_delete_link.addEventListener('click', function (event) {
      event.preventDefault();
      const success_clear_message = this.dataset.successMessage;
      if (success_clear_message) {
        localStorage.setItem('success_harvest_clear_message', success_clear_message);
      }
    });
  }

  // Adding dgeHarvester.clear success message
  if (harvester_clear_link) {
    harvester_clear_link.addEventListener('click', function (event) {
      event.preventDefault();
      const success_clear_message = this.dataset.successMessage;
      if (success_clear_message) {
        localStorage.setItem('success_harvest_clear_message', success_clear_message);
      }
    });
  }

  
  // Showing harvest clear success message
  const success_harvest_clear_message = localStorage.getItem('success_harvest_clear_message');
  if (success_harvest_clear_message) {
    const div = document.createElement('div');
    div.className = 'alert fade in alert-success';
    div.innerHTML = success_harvest_clear_message;
    document.querySelector(".flash-messages")?.appendChild(div);
    localStorage.removeItem('success_harvest_clear_message');
  }
});
