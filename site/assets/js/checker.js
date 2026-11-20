/*
  "Do the rules fit me?" check. This file runs the check for both guides.
  The words, links, and lists for each state come from checker-oregon.js
  or checker-utah.js, which the page loads first.

  Privacy: answers live only in this page's memory. Nothing is saved to
  storage and nothing is sent: the Content Security Policy sets
  connect-src 'none' and form-action 'none', so the browser itself blocks
  any network request from this page. "Start over" clears the answers.

  Wording: every result line is tied to a claim in data/claims.json
  (claim IDs in the comments of each state's file). The check never says
  "you are exempt" or "you qualify". Only the state decides. It never asks
  about immigration status.

  The decision table is documented in docs/checker-logic.md.
*/
(function () {
  'use strict';

  var CHECK = window.StasisCheck || null;
  var REASONS = CHECK ? CHECK.reasons : {};
  var MEETS = CHECK ? CHECK.meets : {};

  var form;
  var progress;
  var steps;
  var result;
  var current = 1;
  var TOTAL = 3;

  var SVG_NS = 'http://www.w3.org/2000/svg';
  var ICON_SHAPES = {
    shield: [['path', { d: 'M12 3l7.5 3v6c0 4.5-3.2 7.8-7.5 9-4.3-1.2-7.5-4.5-7.5-9V6L12 3z' }]],
    paper: [
      ['path', { d: 'M6 3h8l4 4v14H6V3z' }],
      ['path', { d: 'M14 3v4h4' }],
      ['path', { d: 'M9 12h6M9 16h6' }]
    ],
    log: [
      ['rect', { x: '5', y: '4', width: '14', height: '17', rx: '2' }],
      ['path', { d: 'M9 4V3h6v1' }],
      ['path', { d: 'M8.5 10l1.5 1.5 3-3' }],
      ['path', { d: 'M14.5 10h2' }],
      ['path', { d: 'M8.5 15l1.5 1.5 3-3' }],
      ['path', { d: 'M14.5 15h2' }]
    ],
    helper: [
      ['circle', { cx: '9', cy: '8.5', r: '3' }],
      ['path', { d: 'M3.5 19a5.5 5.5 0 0 1 11 0' }],
      ['circle', { cx: '16.5', cy: '9.5', r: '2.25' }],
      ['path', { d: 'M15.5 14a4.5 4.5 0 0 1 5 5' }]
    ],
    check: [
      ['circle', { cx: '12', cy: '12', r: '9' }],
      ['path', { d: 'M8.5 12.5l2.5 2.5 4.5-5.5' }]
    ]
  };

  function svgIcon(name) {
    var svg = document.createElementNS(SVG_NS, 'svg');
    svg.setAttribute('class', 'icon');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('width', '24');
    svg.setAttribute('height', '24');
    svg.setAttribute('fill', 'none');
    svg.setAttribute('stroke', 'currentColor');
    svg.setAttribute('stroke-width', '1.75');
    svg.setAttribute('stroke-linecap', 'round');
    svg.setAttribute('stroke-linejoin', 'round');
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('focusable', 'false');
    (ICON_SHAPES[name] || []).forEach(function (item) {
      var node = document.createElementNS(SVG_NS, item[0]);
      Object.keys(item[1]).forEach(function (k) { node.setAttribute(k, item[1][k]); });
      svg.appendChild(node);
    });
    return svg;
  }

  function guidePrefix() {
    var href = (CHECK && CHECK.age && CHECK.age.link && CHECK.age.link.href) || 'apply';
    var idx = href.lastIndexOf('apply');
    return idx > 0 ? href.slice(0, idx) : '';
  }

  function el(tag, text, className) {
    var node = document.createElement(tag);
    if (text) { node.textContent = text; }
    if (className) { node.className = className; }
    return node;
  }

  function link(href, text) {
    var a = document.createElement('a');
    a.href = href;
    a.textContent = text;
    return a;
  }

  function para(parts, className) {
    var p = el('p', null, className);
    parts.forEach(function (part) {
      p.appendChild(typeof part === 'string' ? document.createTextNode(part) : part);
    });
    return p;
  }

  function checkedValues(name) {
    var values = [];
    Array.prototype.forEach.call(form.querySelectorAll('input[name="' + name + '"]:checked'), function (input) {
      values.push(input.value);
    });
    return values;
  }

  function checkedLabels(name) {
    var labels = [];
    Array.prototype.forEach.call(form.querySelectorAll('input[name="' + name + '"]:checked'), function (input) {
      var wrap = input.closest('label');
      var text = wrap ? wrap.textContent.replace(/\s+/g, ' ').trim() : input.value;
      labels.push(text);
    });
    return labels;
  }

  function buildRecapBox(headingText, includeStep3) {
    var box = el('div', null, 'answer-recap');
    var head = el('p', null, 'recap-title');
    head.appendChild(svgIcon('check'));
    head.appendChild(el('span', headingText));
    box.appendChild(head);

    var dl = el('dl', null, 'recap-list');
    var ageLabels = checkedLabels('age');
    var reasonLabels = checkedLabels('reason');
    var meetLabels = checkedLabels('meet');

    function addRow(term, value) {
      var row = el('div', null, 'recap-row');
      row.appendChild(el('dt', term));
      row.appendChild(el('dd', value));
      dl.appendChild(row);
    }

    addRow('Age', ageLabels.length ? ageLabels.join(', ') : 'Not picked yet');
    if (checkedValues('age')[0] === '19to64') {
      addRow('Reasons that fit you', reasonLabels.length ? reasonLabels.join(' ') : 'Not picked yet');
      if (includeStep3) {
        addRow('Ways to meet the rules', meetLabels.length ? meetLabels.join(' ') : 'Pick at least one above');
      }
    }
    box.appendChild(dl);
    return box;
  }

  function updatePreviewRecap() {
    var container = document.getElementById('checker-recap-preview');
    if (!container) { return; }
    while (container.firstChild) { container.removeChild(container.firstChild); }
    container.appendChild(buildRecapBox('Your answers so far', true));
  }

  function buildNextStrip() {
    var prefix = guidePrefix();
    var wrap = el('div', null, 'next-needs');
    wrap.appendChild(el('h3', 'What you may need next'));
    var ul = el('ul', null, 'next-strip');
    var items = [
      { icon: 'paper', href: prefix + 'apply', title: 'How to apply', note: 'Online, on paper, in person, or by phone' },
      { icon: 'log', href: prefix + 'log', title: 'Hours log', note: 'Print a sheet to write down your hours' },
      { icon: 'helper', href: prefix + 'help', title: 'Free help', note: 'In-person helpers, language help, and phone lines' }
    ];
    items.forEach(function (item) {
      var li = el('li');
      var a = document.createElement('a');
      a.href = item.href;
      var head = el('span', null, 'next-strip-head');
      head.appendChild(svgIcon(item.icon));
      head.appendChild(el('span', item.title));
      a.appendChild(head);
      a.appendChild(el('span', item.note, 'next-strip-note'));
      li.appendChild(a);
      ul.appendChild(li);
    });
    wrap.appendChild(ul);
    return wrap;
  }

  function showStep(n, moveFocus) {
    current = n;
    steps.forEach(function (step) {
      step.hidden = Number(step.getAttribute('data-step')) !== n;
    });
    progress.textContent = 'Step ' + n + ' of ' + TOTAL;
    if (n === 3) { updatePreviewRecap(); }
    if (moveFocus) {
      var target = form.querySelector('[data-step="' + n + '"]');
      if (target) { target.focus(); }
    }
  }

  function showError(n, show) {
    var error = document.getElementById('step-' + n + '-error');
    if (!error) { return; }
    error.hidden = !show;
    if (show) {
      var first = form.querySelector('[data-step="' + n + '"] input');
      if (first) { first.focus(); }
    }
  }

  function stepIsAnswered(n) {
    if (n === 1) { return checkedValues('age').length > 0; }
    if (n === 2) { return checkedValues('reason').length > 0; }
    if (n === 3) { return checkedValues('meet').length > 0; }
    return true;
  }

  function wireNoneBoxes(name) {
    var inputs = form.querySelectorAll('input[name="' + name + '"]');
    Array.prototype.forEach.call(inputs, function (input) {
      input.addEventListener('change', function () {
        if (input.checked) {
          Array.prototype.forEach.call(inputs, function (other) {
            var otherIsNone = other.hasAttribute('data-none');
            var thisIsNone = input.hasAttribute('data-none');
            if (other !== input && (otherIsNone || thisIsNone)) { other.checked = false; }
          });
        }
        if (current === 3) { updatePreviewRecap(); }
      });
    });
  }

  /* An ordered list of steps. Each step is a list of plain strings and
     { href, text } links. */
  function stepsOf(items) {
    var ol = el('ol', null, 'steps');
    items.forEach(function (parts) {
      var li = el('li');
      parts.forEach(function (part) {
        li.appendChild(typeof part === 'string' ? document.createTextNode(part) : link(part.href, part.text));
      });
      ol.appendChild(li);
    });
    return ol;
  }

  function listOf(keys, table) {
    var ul = el('ul', null, 'short');
    keys.forEach(function (key) {
      var item = table[key];
      if (!item) { return; }
      var li = el('li');
      li.appendChild(el('strong', item.label));
      if (item.how) { li.appendChild(document.createTextNode(' ' + item.how)); }
      ul.appendChild(li);
    });
    return ul;
  }

  function changeAnswers() {
    var age = checkedValues('age')[0];
    clearResult();
    result.hidden = true;
    form.hidden = false;
    progress.hidden = false;
    showStep(age === '19to64' ? 3 : 1, true);
  }

  function buildResult() {
    var age = checkedValues('age')[0];
    var reasons = checkedValues('reason').filter(function (v) { return v !== 'none'; });
    var meets = checkedValues('meet').filter(function (v) { return v !== 'none'; });
    var notApply = reasons.some(function (key) { return REASONS[key] && REASONS[key].notApply; });

    var title = clearResult();

    result.appendChild(buildRecapBox('Your answers', age === '19to64'));

    if (age !== '19to64') {
      title.textContent = 'The new rules do not apply to your age group.';
      result.appendChild(el('p', CHECK.age.body));
      result.appendChild(para([link(CHECK.age.link.href, CHECK.age.link.text)]));
    } else if (reasons.length > 0) {
      title.textContent = notApply
        ? 'The new rules likely do not apply to you.'
        : 'You may not have to meet the new rules.';
      result.appendChild(el('p', CHECK.reasonIntro));
      result.appendChild(listOf(reasons, REASONS));
      if (meets.length > 0) {
        result.appendChild(el('h3', 'You may also already meet the rules'));
        result.appendChild(listOf(meets, MEETS));
      }
      result.appendChild(el('h3', 'What to do'));
      result.appendChild(stepsOf(CHECK.reasonTodo));
    } else if (meets.length > 0) {
      title.textContent = 'You may already meet the new rules.';
      result.appendChild(el('p', 'Here is what you picked:'));
      result.appendChild(listOf(meets, MEETS));
      result.appendChild(el('h3', 'What to do'));
      result.appendChild(stepsOf(CHECK.meetTodo));
      result.appendChild(para([link(CHECK.meetLink.href, CHECK.meetLink.text)]));
    } else {
      title.textContent = 'The new rules may apply to you.';
      result.appendChild(el('p', CHECK.mayApply.body));
      result.appendChild(el('h3', 'What you can do'));
      var ways = el('ul', null, 'short');
      CHECK.mayApply.ways.forEach(function (way) {
        var li = el('li');
        li.appendChild(el('strong', way.strong));
        li.appendChild(document.createTextNode(' '));
        li.appendChild(link(way.link.href, way.link.text));
        ways.appendChild(li);
      });
      result.appendChild(ways);
    }

    result.appendChild(buildNextStrip());

    var promise = el('div', null, 'promise');
    var kicker = el('p', null, 'box-kicker');
    var iconWrap = el('span', null, 'box-icon');
    iconWrap.appendChild(svgIcon('shield'));
    kicker.appendChild(iconWrap);
    kicker.appendChild(el('span', 'Privacy'));
    promise.appendChild(kicker);
    CHECK.promise.forEach(function (line) { promise.appendChild(el('p', line)); });
    result.appendChild(promise);

    var actions = el('div', null, 'actions');
    var edit = el('button', 'Change my answers', 'button-secondary');
    edit.type = 'button';
    edit.addEventListener('click', changeAnswers);
    actions.appendChild(edit);
    var again = el('button', 'Start over', 'button-secondary');
    again.type = 'button';
    again.addEventListener('click', startOver);
    actions.appendChild(again);
    var print = el('button', 'Print my results', 'button-secondary');
    print.type = 'button';
    print.addEventListener('click', function () { window.print(); });
    actions.appendChild(print);
    result.appendChild(actions);

    result.hidden = false;
    form.hidden = true;
    progress.hidden = true;
    title.setAttribute('tabindex', '-1');
    try {
      title.focus({ preventScroll: false });
    } catch (e) {
      title.focus();
    }
    var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (result.scrollIntoView) {
      result.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
    }
  }

  /* Empties the result area but keeps its heading, which the page
     references with aria-labelledby. Returns the heading. */
  function clearResult() {
    var title = document.getElementById('result-title');
    Array.prototype.slice.call(result.children).forEach(function (child) {
      if (child !== title) { result.removeChild(child); }
    });
    title.textContent = 'Your results';
    return title;
  }

  function startOver() {
    form.reset();
    clearResult();
    result.hidden = true;
    form.hidden = false;
    progress.hidden = false;
    [1, 2, 3].forEach(function (n) { showError(n, false); });
    showStep(1, true);
  }

  document.addEventListener('DOMContentLoaded', function () {
    form = document.getElementById('checker');
    progress = document.getElementById('checker-progress');
    result = document.getElementById('checker-result');
    if (!form || !progress || !result || !CHECK) { return; }

    var step3 = form.querySelector('[data-step="3"]');
    if (step3) {
      var preview = el('div', null, 'answer-preview');
      preview.id = 'checker-recap-preview';
      preview.setAttribute('aria-live', 'polite');
      var step3Actions = step3.querySelector('.actions');
      step3.insertBefore(preview, step3Actions);
    }

    steps = Array.prototype.slice.call(form.querySelectorAll('[data-step]'));
    form.hidden = false;
    progress.hidden = false;
    showStep(1, false);

    wireNoneBoxes('reason');
    wireNoneBoxes('meet');

    form.addEventListener('click', function (event) {
      var button = event.target.closest('button');
      if (!button || !form.contains(button)) { return; }
      if (button.hasAttribute('data-next')) {
        if (!stepIsAnswered(current)) { showError(current, true); return; }
        showError(current, false);
        var age = checkedValues('age')[0];
        if (current === 1 && age !== '19to64') { buildResult(); return; }
        showStep(current + 1, true);
      } else if (button.hasAttribute('data-back')) {
        showError(current, false);
        showStep(Math.max(1, current - 1), true);
      }
    });

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      if (!stepIsAnswered(3)) { showError(3, true); return; }
      showError(3, false);
      buildResult();
    });
  });
}());
