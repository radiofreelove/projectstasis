/*
  The words and links for the Utah Medicaid check.

  site/assets/js/checker.js runs the check and reads this file.
  Every line is tied to a Utah claim in data/claims.json (claim IDs in the
  comments), and the full table is in docs/checker-logic.md. The check
  never says "you are exempt" or "you qualify". Only the state decides.

  Utah checks its own records first for every reason, so most reasons need
  no "how" line. A reason has one only where Utah says something specific.
*/
window.StasisCheck = (function () {
  'use strict';

  var HARDSHIP = 'Utah calls this a short-term hardship. You must ask the state for this exception.';

  return {
    reasons: {
      pregnant: { // U-EX-PREG
        label: 'You are pregnant, or you get Medicaid for the months after a birth.'
      },
      care: { // U-EX-CARE
        label: 'You are a parent, guardian, or caregiver for a child 13 or younger, or for a person with a disability.'
      },
      health: { // U-EX-FRAIL, U-FRAIL-CLAIMS, U-FRAIL-SELF
        label: 'You are blind, or you have a disability, a mental health condition, a substance use disorder, or a condition that makes daily tasks hard.',
        how: 'Utah Medicaid checks its own health records first. If that does not confirm it, you fill out a short form about your condition.'
      },
      treatment: { // U-EX-SUD, U-FRAIL-PATHS
        label: 'You are in a drug or alcohol treatment and rehabilitation program.',
        how: 'Utah Medicaid checks its own health records first.'
      },
      medicare: { // U-NA-MEDICARE
        label: 'You have Medicare Part A or Part B.',
        how: 'Utah says the rules do not apply to people with Medicare Part A or Part B.',
        notApply: true
      },
      ssi: { // U-NA-GROUP
        label: 'You get SSI.',
        how: 'Utah says the rules do not apply to people in some other Medicaid groups, like people who get SSI.',
        notApply: true
      },
      snap: { // U-EX-SNAP
        label: 'You have to meet work rules for SNAP or TANF.'
      },
      aian: { // U-EX-AIAN, U-AIAN-PROOF
        label: 'You are American Indian or Alaska Native.',
        how: "The state must verify your status. Utah's letter says to send proof by Jan. 1, 2027."
      },
      foster: { // U-EX-FOSTER
        label: 'You are in foster care, or you were.',
        how: 'Some Utah pages say this means people in the Former Foster Care program. Ask the state which one fits you.'
      },
      veteran: { // U-EX-VET
        label: 'You are a veteran with a 100% disability.'
      },
      jail: { // U-EX-JAIL
        label: 'You got out of jail or prison in the last 90 days.'
      },
      hospital: { // U-HARD-HOSP
        label: 'You were a patient in a hospital, or you lived in a nursing home or another care facility.',
        how: HARDSHIP
      },
      travel: { // U-HARD-TRAVEL
        label: 'You had to travel outside your community for medical care for you or a dependent.',
        how: HARDSHIP
      }
    },

    meets: {
      income: { // U-MEET-INCOME, U-INCOME-WHOSE
        label: 'You earn at least $580 a month.',
        how: "Utah's pages do not say whose income counts. The federal rule counts your household's. Ask the state how it counts yours."
      },
      school: { // U-MEET-SCHOOL, U-SCHOOL-WHO
        label: 'You go to school at least half-time.',
        how: 'Your school decides what counts as half-time.'
      },
      hours: { // U-MEET-HOURS
        label: 'You spend 80 hours a month on work, job training, volunteering, or school, added together.',
        how: 'Write down your hours. You can print an hours log from this site.'
      }
    },

    // Age is not 19 to 64. U-NA-AGE
    age: {
      body: 'The work or activity rules are for adults ages 19 to 64. You can still apply for Utah Medicaid.',
      link: { href: 'utah-apply', text: 'How to apply' }
    },

    // Picked at least one reason. U-DATA-FIRST, U-TELL-HOW, U-742-NOLINK
    reasonIntro: 'Here is what you picked:',
    reasonTodo: [
      ['The state checks records it already has first. If it can confirm your reason, you do not need to do anything.'],
      ['If it cannot, you can report your reason online in myCase, on your application, or on form 742.'],
      ["Utah's page names form 742 but does not link to it. Ask the Department of Workforce Services (DWS) for it at 1-866-435-7414."],
      [{ href: 'utah-reasons', text: 'See every reason, and what proof tribal members send' }]
    ],

    // Picked only ways to meet the rules. U-DATA-FIRST, U-VERIFY-30
    meetTodo: [
      ['The state checks records it already has first, like work and school records.'],
      ['If the state needs more, you may need to send a form within 30 days, or you could lose your coverage.']
    ],
    meetLink: { href: 'utah-log', text: 'Print an hours log' },

    // Picked nothing. U-LOOKBACK-APP
    mayApply: {
      body: 'You can still apply. The state looks at the month before you apply.',
      ways: [
        { strong: 'Look again for a reason.', link: { href: 'utah-reasons', text: 'See every reason you may not have to meet the rules' } },
        { strong: 'Read what counts.', link: { href: 'utah-rules', text: 'The rules, in plain words' } },
        { strong: 'Talk to a free helper.', link: { href: 'utah-help', text: 'Free help and other languages' } }
      ]
    },

    // Shown under every result. U-ONLY-STATE, C-PRIV-NOSEND
    promise: [
      'Only the state decides. This check is not a decision.',
      'Nothing you picked was saved or sent.'
    ]
  };
}());
