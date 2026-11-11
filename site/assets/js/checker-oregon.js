/*
  The words and links for the Oregon Health Plan check.

  site/assets/js/checker.js runs the check and reads this file.
  Every line is tied to a claim in data/claims.json (claim IDs in the
  comments), and the full table is in docs/checker-logic.md. The check
  never says "you are exempt" or "you qualify". Only OHP decides.
*/
window.StasisCheck = (function () {
  'use strict';

  return {
    reasons: {
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
    },

    meets: {
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
    },

    // Age is not 19 to 64. C-WHO-AGE
    age: {
      body: 'The work or activity rules are for adults ages 19 to 64. You can still apply for OHP.',
      link: { href: 'apply', text: 'How to apply' }
    },

    // Picked at least one reason.
    reasonIntro: 'Here is what you picked, and how OHP checks each one:',
    reasonTodo: [
      ['When you apply, tell OHP your reason.'],
      ['Already applied? Tell OHP in your ONE account at ', { href: 'https://benefits.oregon.gov/', text: 'benefits.oregon.gov' }, ', or call 800-699-9075.']
    ],

    // Picked only ways to meet the rules.
    meetTodo: [
      ['When you apply, answer the questions about work, school, and volunteering.'],
      ['If OHP asks for proof, you get a letter. You have 35 days to reply.']
    ],
    meetLink: { href: 'log', text: 'Print an hours log' },

    // Picked nothing. C-LOOKBACK-APP, C-FIND-ACTIVITIES
    mayApply: {
      body: 'You can still apply. OHP looks at the month before you apply.',
      ways: [
        { strong: 'Look again for a reason.', link: { href: 'reasons', text: 'See every reason you may not have to meet the rules' } },
        { strong: 'Find work, school, or volunteer options.', link: { href: 'https://ohp.oregon.gov/Resources', text: "OHP's job and volunteer resources" } },
        { strong: 'Talk to a free helper.', link: { href: 'help', text: 'Free help and other languages' } }
      ]
    },

    // Shown under every result. C-ONLY-OHP, C-PRIV-NOSEND
    promise: [
      'Only OHP decides. This check is not a decision.',
      'Nothing you picked was saved or sent.'
    ]
  };
}());
