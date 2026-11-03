/*
  Display settings: text size, spacing, colors, and how much to show.

  Loaded in <head> without "defer" so the page draws in the chosen colors
  from the start (no flash). Settings are saved in this browser's
  localStorage under one key. They are never sent anywhere: the page's
  Content Security Policy blocks all network requests from scripts.
  If storage is blocked, settings still work for the current page.
*/
(function () {
  'use strict';

  var KEY = 'stasis-display-v1';
  var DEFAULTS = { text: 'm', spacing: 'normal', theme: 'auto', details: 'all' };
  var ALLOWED = {
    text: ['m', 'l', 'xl'],
    spacing: ['normal', 'roomy'],
    theme: ['auto', 'warm', 'white', 'dark'],
    details: ['all', 'fewer']
  };
  var root = document.documentElement;

  function read() {
    try {
      var raw = window.localStorage.getItem(KEY);
      if (!raw) { return {}; }
      var value = JSON.parse(raw);
      return (value && typeof value === 'object') ? value : {};
    } catch (e) {
      return {};
    }
  }

  function write(settings) {
    try {
      window.localStorage.setItem(KEY, JSON.stringify(settings));
    } catch (e) {
      /* Storage blocked or full: settings last for this page only. */
    }
  }

  function clear() {
    try {
      window.localStorage.removeItem(KEY);
    } catch (e) {
      /* Nothing to clear. */
    }
  }

  function sanitize(settings) {
    var clean = {};
    Object.keys(DEFAULTS).forEach(function (name) {
      var value = settings[name];
      clean[name] = ALLOWED[name].indexOf(value) !== -1 ? value : DEFAULTS[name];
    });
    return clean;
  }

  function apply(settings) {
    root.setAttribute('data-text', settings.text);
    root.setAttribute('data-spacing', settings.spacing);
    root.setAttribute('data-theme', settings.theme);
    root.setAttribute('data-details', settings.details);
  }

  var state = sanitize(read());
  apply(state);

  function reflect(panel) {
    Object.keys(DEFAULTS).forEach(function (name) {
      var input = panel.querySelector('input[name="' + name + '"][value="' + state[name] + '"]');
      if (input) { input.checked = true; }
    });
  }

  function announce(message) {
    var live = document.getElementById('settings-status');
    if (!live) { return; }
    live.textContent = '';
    window.setTimeout(function () { live.textContent = message; }, 60);
  }

  document.addEventListener('DOMContentLoaded', function () {
    var panel = document.querySelector('[data-settings]');
    if (!panel) { return; }
    reflect(panel);

    panel.addEventListener('change', function (event) {
      var target = event.target;
      if (!target || target.type !== 'radio' || !Object.prototype.hasOwnProperty.call(DEFAULTS, target.name)) {
        return;
      }
      state[target.name] = target.value;
      state = sanitize(state);
      apply(state);
      write(state);
      announce('Display updated.');
    });

    var reset = panel.querySelector('[data-reset-settings]');
    if (reset) {
      reset.addEventListener('click', function () {
        state = sanitize({});
        apply(state);
        clear();
        reflect(panel);
        announce('Display settings are back to standard.');
      });
    }
  });
}());
