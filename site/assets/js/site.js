/*
  Small page helpers. No network, no storage, no tracking.

  1. Time-limited notes: an element with data-show-until="YYYY-MM-DD"
     is hidden after that date (device's local date). Without JavaScript
     the note stays visible; its text names its own dates, so it is never
     wrong, only out of season. tools/check_review_dates.py flags expired
     notes so a person removes them.
  2. Print buttons: any button with data-print opens the print dialog.
*/
(function () {
  'use strict';

  function todayISO() {
    var now = new Date();
    var month = String(now.getMonth() + 1);
    var day = String(now.getDate());
    if (month.length < 2) { month = '0' + month; }
    if (day.length < 2) { day = '0' + day; }
    return now.getFullYear() + '-' + month + '-' + day;
  }

  document.addEventListener('DOMContentLoaded', function () {
    var today = todayISO();

    Array.prototype.forEach.call(document.querySelectorAll('[data-show-until]'), function (el) {
      var until = el.getAttribute('data-show-until');
      if (/^\d{4}-\d{2}-\d{2}$/.test(until) && today > until) {
        el.hidden = true;
      }
    });

    Array.prototype.forEach.call(document.querySelectorAll('[data-print]'), function (button) {
      button.hidden = false;
      button.addEventListener('click', function () { window.print(); });
    });
  });
}());
