/*
  Display settings: text size, spacing, font, colors, and how much to show.

  Loaded in <head> without "defer" so the page draws in the chosen colors
  from the start (no flash). Settings are saved in this browser's
  localStorage under one key. They are never sent anywhere: the page's
  Content Security Policy blocks all network requests from scripts.
  If storage is blocked, settings still work for the current page.

  "How much to show" has two controls that always agree: the choices in
  the Display settings panel, and the strip above each page's heading
  (one button: "Show just the key points" or "Show everything"). Both
  write the same value, "details", to the same key. Nothing new is stored.
  The strip shows only when this script has run: it sets data-js on the
  html element, and the style sheet waits for that.

  A link that points into hidden detail must not lead nowhere. When the
  address names an element inside hidden detail, the page goes back to
  "Everything" first and then moves to that element.
*/
(function () {
  'use strict';

  var KEY = 'stasis-display-v1';
  var DEFAULTS = { text: 'm', spacing: 'normal', font: 'system', theme: 'auto', details: 'all' };
  var ALLOWED = {
    text: ['m', 'l', 'xl'],
    spacing: ['normal', 'roomy'],
    font: ['system', 'hyper'],
    theme: ['auto', 'warm', 'white', 'dark'],
    details: ['all', 'fewer']
  };
  var DETAILS_SAID = {
    fewer: 'Just the key points. Extra details on this page are now hidden.',
    all: 'Everything. All the details on this page are showing again.'
  };
  var root = document.documentElement;
  var panel = null;
  var strip = null;

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
    root.setAttribute('data-font', settings.font);
    root.setAttribute('data-theme', settings.theme);
    root.setAttribute('data-details', settings.details);
  }

  var state = sanitize(read());
  apply(state);
  root.setAttribute('data-js', '');

  /* Make the panel and the strip show the current state. */
  function reflect() {
    if (panel) {
      Object.keys(DEFAULTS).forEach(function (name) {
        var input = panel.querySelector('input[name="' + name + '"][value="' + state[name] + '"]');
        if (input) { input.checked = true; }
      });
    }
    if (strip) {
      strip.setAttribute('aria-pressed', state.details === 'fewer' ? 'true' : 'false');
    }
  }

  function announce(message) {
    var live = document.getElementById('settings-status');
    if (!live) { return; }
    live.textContent = '';
    window.setTimeout(function () { live.textContent = message; }, 60);
  }

  /* One way to change "how much to show", used by the panel, the strip,
     and links into hidden detail. Focus is never moved. */
  function setDetails(value) {
    state.details = value;
    state = sanitize(state);
    apply(state);
    write(state);
    reflect();
    announce(DETAILS_SAID[state.details]);
  }

  /* The element the address points to (#id), if there is one. */
  function hashTarget() {
    var hash = window.location.hash;
    if (!hash || hash.length < 2) { return null; }
    var id = hash.slice(1);
    try { id = decodeURIComponent(id); } catch (e) { /* Use it as written. */ }
    return document.getElementById(id);
  }

  /* If the address points into hidden detail, show everything, then go there. */
  function revealTarget() {
    if (state.details !== 'fewer') { return; }
    var target = hashTarget();
    if (!target || !target.closest || !target.closest('.more')) { return; }
    setDetails('all');
    if (target.scrollIntoView) { target.scrollIntoView(); }
  }

  document.addEventListener('DOMContentLoaded', function () {
    panel = document.querySelector('[data-settings]');
    strip = document.querySelector('[data-toggle-details]');
    reflect();

    if (strip) {
      strip.addEventListener('click', function () {
        setDetails(state.details === 'fewer' ? 'all' : 'fewer');
      });
    }

    revealTarget();
    window.addEventListener('hashchange', revealTarget);

    if (!panel) { return; }

    panel.addEventListener('change', function (event) {
      var target = event.target;
      if (!target || target.type !== 'radio' || !Object.prototype.hasOwnProperty.call(DEFAULTS, target.name)) {
        return;
      }
      if (target.name === 'details') {
        setDetails(target.value);
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
        reflect();
        announce('Display settings are back to standard.');
      });
    }
  });
}());
