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

  function showStep(n, moveFocus) {
    current = n;
    steps.forEach(function (step) {
      step.hidden = Number(step.getAttribute('data-step')) !== n;
    });
    progress.textContent = 'Step ' + n + ' of ' + TOTAL;
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
        if (!input.checked) { return; }
        Array.prototype.forEach.call(inputs, function (other) {
          var otherIsNone = other.hasAttribute('data-none');
          var thisIsNone = input.hasAttribute('data-none');
          if (other !== input && (otherIsNone || thisIsNone)) { other.checked = false; }
        });
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

  function buildResult() {
    var age = checkedValues('age')[0];
    var reasons = checkedValues('reason').filter(function (v) { return v !== 'none'; });
    var meets = checkedValues('meet').filter(function (v) { return v !== 'none'; });
    var notApply = reasons.some(function (key) { return REASONS[key] && REASONS[key].notApply; });

    var title = clearResult();

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

    var promise = el('div', null, 'promise');
    CHECK.promise.forEach(function (line) { promise.appendChild(el('p', line)); });
    result.appendChild(promise);

    var actions = el('div', null, 'actions');
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
    result.focus();
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
