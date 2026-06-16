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

(function ($) {
  'use strict';

  function buildDateTime(dateValue, timeValue, isEnd) {
    if (!dateValue) {
      return null;
    }

    var safeTime = timeValue || (isEnd ? '23:59' : '00:00');
    var value = dateValue + 'T' + safeTime;
    var date = new Date(value);

    if (isNaN(date.getTime())) {
      return null;
    }

    return date;
  }

  function getFieldParts($block) {
    return {
      $dateFrom: $block.find('input[name*="-date-from-"]'),
      $timeFrom: $block.find('input[name*="-time-from-"]'),
      $dateTo: $block.find('input[name*="-date-to-"]'),
      $timeTo: $block.find('input[name*="-time-to-"]')
    };
  }

  function getOrCreateErrorBox($block) {
    var $errorBox = $block.find('.js-date-period-error');

    if (!$errorBox.length) {
      $errorBox = $('<div/>', {
        'class': 'date-period-error js-date-period-error',
        'aria-live': 'polite'
      });
      $block.append($errorBox);
    }

    return $errorBox;
  }

  function clearValidation($block) {
    $block.removeClass('date-period-invalid');
    $block.find('.js-date-period-error').text('').hide();
  }

  function setValidationError($block, message) {
    var $errorBox = getOrCreateErrorBox($block);
    $block.addClass('date-period-invalid');
    $errorBox.text(message).show();
  }

  function validateBlock($block) {
    var parts = getFieldParts($block);

    var dateFrom = parts.$dateFrom.val();
    var timeFrom = parts.$timeFrom.val();
    var dateTo = parts.$dateTo.val();
    var timeTo = parts.$timeTo.val();

    clearValidation($block);

    if (!dateFrom || !dateTo) {
      return true;
    }

    var fromDate = buildDateTime(dateFrom, timeFrom, false);
    var toDate = buildDateTime(dateTo, timeTo, true);

    if (!fromDate || !toDate) {
      return true;
    }

    if (toDate < fromDate) {
      setValidationError($block, 'La fecha y hora "Hasta" debe ser posterior o igual a "Desde".');
      return false;
    }

    return true;
  }

  function validateAll(containerSelector) {
    var isValid = true;

    $(containerSelector).find('[id^="div-coverage_new-"], .div-coverage_new').each(function () {
      var blockValid = validateBlock($(this));
      if (!blockValid) {
        isValid = false;
      }
    });

    return isValid;
  }

  function bindValidation(containerSelector) {
    $(document).on(
      'change input',
      containerSelector + ' input[type="date"], ' + containerSelector + ' input[type="time"]',
      function () {
        var $block = $(this).closest('.div-coverage_new');
        validateBlock($block);
      }
    );

    $(document).on('submit', 'form', function (e) {
      var $form = $(this);
      var $container = $form.find(containerSelector);

      if (!$container.length) {
        return;
      }

      var ok = validateAll(containerSelector);

      if (!ok) {
        e.preventDefault();

        var $firstError = $container.find('.date-period-invalid').first();
        if ($firstError.length) {
          $('html, body').animate({
            scrollTop: $firstError.offset().top - 120
          }, 200);
        }
      }
    });
  }

  $(function () {
    var containerSelector = '#multi-value-coverage_new';

    if (!$(containerSelector).length) {
      return;
    }

    bindValidation(containerSelector);

    $(containerSelector).find('.div-coverage_new').each(function () {
      validateBlock($(this));
    });
  });

})(window.jQuery);