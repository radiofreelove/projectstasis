/*
  "Do the rules fit me?" check.

  Privacy: answers live only in this page's memory. Nothing is saved to
  storage and nothing is sent: the Content Security Policy sets
  connect-src 'none' and form-action 'none', so the browser itself blocks
  any network request from this page. "Start over" clears the answers.

  Wording: every result line is tied to a claim in data/claims.json
  (claim IDs in the comments). The check never says "you are exempt" or
  "you qualify". Only OHP decides. It never asks about immigration status.

  The decision table is documented in docs/checker-logic.md.
*/
(function () {
  'use strict';

  var REASONS = {
    pregnant: { // C-EX-PREG
      label: 'You are pregnant, or you were in the last 12 months.',
      how: 'Tell OHP. No proof is needed.'
    },
    child: { // C-EX-CHILD
      label: 'You care for a child 13 or younger.',
      how: 'Tell OHP how you are related to the child. Starting in 2028, OHP may ask for a calendar or schedule.'
    },
    caregiver: { // C-EX-CARE
      label: 'You care for someone with a disability or a serious health condition.',
      how: 'Tell OHP. If you do not live with them and are not related, you need to give at least 80 hours of care a month.'
    },
    health: { // C-EX-HEALTH, C-HEALTH-2027
      label: 'You have a serious or disabling health condition.',
      how: 'Tell OHP. In 2027, you do not need a note from a doctor.'
    },
    ssi: { // C-EX-SSI
      label: 'You get SSI or SSDI.',
      how: 'Tell OHP. OHA counts this as a qualifying health condition.'
    },
    treatment: { // C-EX-SUD
      label: 'You are in drug or alcohol treatment, or you were in the last 5 years.',
      how: 'Tell OHP. Starting in 2028, OHP may ask for a paper that shows your treatment dates.'
    },
    medicare: { // C-NA-MEDICARE
      label: 'You have Medicare.',
      how: 'The rules do not apply to people with Medicare. OHP can usually check this itself.',
      notApply: true
    },
    disability_ohp: { // C-NA-PROGRAM
      label: 'You are applying for OHP because of a disability.',
      how: 'The rules do not apply to OHP programs based on disability.',
      notApply: true
    },
    snap: { // C-EX-SNAP
      label: 'You get SNAP, and you meet SNAP work rules.',
      how: 'OHP checks this for you. Being excused from SNAP work rules is not enough.'
    },
    tanf: { // C-EX-TANF
      label: 'You get TANF, and you meet TANF work rules.',
      how: 'OHP checks this for you.'
    },
    aian: { // C-EX-AIAN
      label: 'You are American Indian or Alaska Native.',
      how: 'Tell OHP. No proof is needed.'
    },
    foster: { // C-EX-FOSTER
      label: 'You were in foster care at age 18, and you are under 26.',
      how: 'OHP checks this for you.'
    },
    veteran: { // C-EX-VET
      label: 'You are a veteran with a 100% disability rating from the VA.',
      how: 'Tell OHP. If OHP asks, send your VA award letter.'
    },
    jail: { // C-EX-JAIL
      label: 'You got out of jail or prison in the last 4 months.',
      how: 'Tell OHP. No proof is needed.'
    },
    hospital: { // C-EX-HOSP
      label: 'You stayed at least one night as a patient in a hospital, nursing facility, or behavioral health facility.',
      how: 'Tell OHP.'
    },
    travel: { // C-EX-TRAVEL
      label: 'You were away from home 7 or more days in a month to get medical care for you, your child, or a tax dependent.',
      how: 'Tell OHP.'
    }
  };

  var MEETS = {
    income: { // C-MEET-INCOME, C-DATA-FIRST
      label: 'Your household brings in $580 or more a month.',
      how: 'OHP may check payroll records first. Keep pay stubs, just in case.'
    },
    school: { // C-MEET-SCHOOL, C-DATA-FIRST
      label: 'You go to school at least half-time.',
      how: 'OHP may check school records first. Keep proof that you are enrolled, just in case.'
    },
    hours: { // C-MEET-HOURS
      label: 'You spend 80 hours a month on work, volunteering, school, or job training, added together.',
      how: 'Write down your hours. You can print an hours log from this site.'
    }
  };

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

  function listOf(keys, table) {
    var ul = el('ul', null, 'short');
    keys.forEach(function (key) {
      var item = table[key];
      if (!item) { return; }
      var li = el('li');
      li.appendChild(el('strong', item.label));
      li.appendChild(document.createTextNode(' ' + item.how));
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
      // C-WHO-AGE
      title.textContent = 'The new rules do not apply to your age group.';
      result.appendChild(el('p', 'The work or activity rules are for adults ages 19 to 64. You can still apply for OHP.'));
      result.appendChild(para([link('apply', 'How to apply')]));
    } else if (reasons.length > 0) {
      title.textContent = notApply
        ? 'The new rules likely do not apply to you.'
        : 'You may not have to meet the new rules.';
      result.appendChild(el('p', 'Here is what you picked, and how OHP checks each one:'));
      result.appendChild(listOf(reasons, REASONS));
      if (meets.length > 0) {
        result.appendChild(el('h3', 'You may also already meet the rules'));
        result.appendChild(listOf(meets, MEETS));
      }
      result.appendChild(el('h3', 'What to do'));
      var todo = el('ol', null, 'steps');
      todo.appendChild(el('li', 'When you apply, tell OHP your reason.'));
      var already = el('li');
      already.appendChild(document.createTextNode('Already applied? Tell OHP in your ONE account at '));
      already.appendChild(link('https://benefits.oregon.gov/', 'benefits.oregon.gov'));
      already.appendChild(document.createTextNode(', or call 800-699-9075.'));
      todo.appendChild(already);
      result.appendChild(todo);
    } else if (meets.length > 0) {
      title.textContent = 'You may already meet the new rules.';
      result.appendChild(el('p', 'Here is what you picked:'));
      result.appendChild(listOf(meets, MEETS));
      result.appendChild(el('h3', 'What to do'));
      var steps2 = el('ol', null, 'steps');
      steps2.appendChild(el('li', 'When you apply, answer the questions about work, school, and volunteering.'));
      steps2.appendChild(el('li', 'If OHP asks for proof, you get a letter. You have 35 days to reply.'));
      result.appendChild(steps2);
      result.appendChild(para([link('log', 'Print an hours log')]));
    } else {
      title.textContent = 'The new rules may apply to you.';
      result.appendChild(el('p', 'You can still apply. OHP looks at the month before you apply.'));
      result.appendChild(el('h3', 'What you can do'));
      var ways = el('ul', null, 'short');
      var w1 = el('li');
      w1.appendChild(el('strong', 'Look again for a reason.'));
      w1.appendChild(document.createTextNode(' '));
      w1.appendChild(link('reasons', 'See every reason you may not have to meet the rules'));
      ways.appendChild(w1);
      var w2 = el('li');
      w2.appendChild(el('strong', 'Find work, school, or volunteer options.'));
      w2.appendChild(document.createTextNode(' '));
      w2.appendChild(link('https://ohp.oregon.gov/Resources', "OHP's job and volunteer resources"));
      ways.appendChild(w2);
      var w3 = el('li');
      w3.appendChild(el('strong', 'Talk to a free helper.'));
      w3.appendChild(document.createTextNode(' '));
      w3.appendChild(link('help', 'Free help and other languages'));
      ways.appendChild(w3);
      result.appendChild(ways);
    }

    var promise = el('div', null, 'promise');
    promise.appendChild(el('p', 'Only OHP decides. This check is not a decision.'));
    promise.appendChild(el('p', 'Nothing you picked was saved or sent.'));
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
    if (!form || !progress || !result) { return; }

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
