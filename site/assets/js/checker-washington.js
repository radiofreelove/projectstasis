/*
  The words and links for the Apple Health check (Washington).

  site/assets/js/checker.js runs the check and reads this file.
  Every line is tied to a Washington claim in data/claims.json (claim IDs
  in the comments), and the full table is in docs/checker-logic.md. The
  check never says "you are exempt" or "you qualify". Only Washington
  decides.

  The ways to meet the rules are the six on HCA's work requirements
  page (WA22). HCA's fact sheet lists five of them and leaves out work
  itself as a way of its own; the page's list governs here
  (docs/corrections.md, Washington item 2, settled Nov. 14, 2026).
*/
window.StasisCheck = (function () {
  'use strict';

  return {
    reasons: {
      pregnant: { // WA-RSN-01
        label: 'You are pregnant, or you are in the 12 months after a pregnancy.'
      },
      care: { // WA-RSN-05, WA-RSN-07
        label: 'You are a parent, caretaker, or guardian of a child under 14, or of a person with a disability.'
      },
      health: { // WA-HLT-03, WA-RSN-10
        label: 'You are blind or have a disability, a substance use disorder, a disabling mental health condition, or a serious or complex medical condition.',
        how: 'HCA calls this medically frail. This list comes from federal law.'
      },
      treatment: { // WA-RSN-11
        label: 'You are in treatment for alcohol or substance use.'
      },
      medicare: { // WA-RSN-08, WA-CHK-01
        label: 'You have Medicare Part A or Part B.',
        how: 'The work rules are only for Apple Health for Adults. That group is for people with no Medicare.',
        notApply: true
      },
      snap: { // WA-RSN-06
        label: 'You are in a SNAP (food) household that meets SNAP\'s work rules, or you get TANF (cash) and meet TANF\'s work rules.'
      },
      aian: { // WA-RSN-04, WA-RSN-14
        label: 'You are American Indian or Alaska Native.',
        how: 'You are also left out of the shorter 6-month coverage periods.'
      },
      foster: { // WA-RSN-03
        label: 'You are a foster youth, or a former foster youth under 26.'
      },
      veteran: { // WA-RSN-12
        label: 'You are a disabled veteran with a 100 percent total disability rating.'
      },
      jail: { // WA-RSN-09
        label: 'You got out of jail or prison in the last 90 days.'
      },
      hardship: { // WA-RSN-13, WA-HARD-01, WA-HARD-02
        label: 'You had a short-term hardship.',
        how: 'HCA names four kinds: travel outside your community for care for a serious condition, and a stay in a hospital or care facility (you must ask for these two); and living where the President declared a disaster, or in a county with unemployment 1.5 times the national rate (these two are automatic).'
      }
    },

    meets: {
      income: { // WA-CHK-02, WA-RULE-02
        label: 'Your household has at least $580 in income a month.',
        how: 'This is the household income HCA already counts for Apple Health (called MAGI). It does not have to come from a job. Seasonal workers may use an average of $580 a month over 6 months.'
      },
      work: { // WA-CHK-06
        label: 'You work at least 80 hours a month.',
        how: 'The work can be for pay, for goods or services, or unpaid.'
      },
      school: { // WA-CHK-03, WA-RULE-03
        label: 'You are in an educational program at least half-time.',
        how: 'Under the federal rule, this includes high school and GED programs.'
      },
      program: { // WA-CHK-04
        label: 'You are in a work program at least 80 hours a month.'
      },
      service: { // WA-CHK-04
        label: 'You do community service at least 80 hours a month.'
      },
      hours: { // WA-CHK-04, WA-RULE-04
        label: 'You do a mix of activities that adds up to at least 80 hours a month.',
        how: 'You may add up hours of work, community service, a work program, and school. You can print an hours log from this site.'
      }
    },

    // Age is not 19 to 64. WA-CHK-01, WA-RSN-02
    age: {
      body: 'The work rules are only for Apple Health for Adults. That group is ages 19 to 64. You can still apply for coverage.',
      link: { href: 'washington-apply', text: 'How to apply' }
    },

    // Picked at least one reason. WA-RULE-06, WA-RULE-05, WA-HOME-02
    reasonIntro: 'Here is what you picked:',
    reasonTodo: [
      ['The state checks its own data first.'],
      ['You may state your own exemption status. The state accepts this.'],
      ['HCA says there is nothing you need to do right now.'],
      [{ href: 'washington-reasons', text: 'See every reason you may not have to meet the rules' }]
    ],

    // Picked only ways to meet the rules. WA-RULE-06, WA-RULE-05, WA-APP-09
    meetTodo: [
      ['The state checks its own data first.'],
      ['You may state your own income or work status. The state accepts this.'],
      ['After you apply, a letter may ask for proof. It gives you 15 days. Coverage may close if the proof does not arrive.']
    ],
    meetLink: { href: 'washington-log', text: 'Print an hours log' },

    // Picked nothing. WA-APP-06, WA-RULE-08
    mayApply: {
      body: 'You can still apply. Enrollment is open all year. The rule looks at the month before you apply.',
      ways: [
        { strong: 'Look again for a reason.', link: { href: 'washington-reasons', text: 'See every reason you may not have to meet the rules' } },
        { strong: 'Read what counts.', link: { href: 'washington-rules', text: 'The rules, in plain words' } },
        { strong: 'Talk to a free helper.', link: { href: 'washington-help', text: 'Free help and other languages' } }
      ]
    },

    // Shown under every result. WA-HOME-06, C-PRIV-NOSEND
    promise: [
      'Only the state decides. This check is not a decision.',
      'Nothing you picked was saved or sent.'
    ]
  };
}());
