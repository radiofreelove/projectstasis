# 0008. The check never decides, and never asks about immigration

- Status: Accepted
- Date: 2026-11-02

## Context

A tool that says "you are exempt" could lead someone not to report an activity or not to apply. A tool that asks about immigration status could scare people away from coverage they are entitled to.

## Decision

- Results use "may" and "likely" and always end with "Only OHP decides."
- Every result names a next step.
- The check asks only about age, reasons OHA lists, and ways to meet the rules. It never asks about immigration, citizenship, names, case numbers, income amounts, or diagnoses.
- The structure lint fails the build if a form label mentions immigration or citizenship.

## Consequences

- Results are less precise than an eligibility determination, by design.
