# Three-sprint milestone plan

The [GitHub milestones](https://github.com/akshatha2005/Team15_SE_Project/milestones)
group the existing requirements into three sprints. This is an organization of the
current tracker, not a record of new implementation dates. Existing issue states,
assignees, story points and labels are preserved. No sprint dates have been assumed.

| Milestone | Scope | Existing issues | Story points |
| --- | --- | --- | --- |
| Sprint 1 - Core Gameplay | Menu, board, snake movement, input, food, growth, scoring, collision, restart and modular structure | #1–13, #20, #23 | 33 |
| Sprint 2 - Persistence and Advanced Gameplay | Local high scores, conditional updates, pause/resume, direct restart, difficulty and 60 FPS loop | #14–19 | 20 |
| Sprint 3 - Quality, Security and Delivery | Stability, target-platform support, security requirements and the CI/CD pull request | #21–27 | 15, plus unestimated CI/CD work |

Issue #28 (HTTPS for a future online leaderboard) stays in the backlog because it
depends on a future online feature. It is not assigned to a sprint milestone.

## Sprint 1 acceptance

- The game launches with the board and centred three-segment snake.
- Direction input, movement, food, growth and scoring work together.
- Wall/self collision ends the game; restart resets the game.
- Core gameplay and input tests pass.

## Sprint 2 acceptance

- Saved high scores load and only increase when a higher score is achieved.
- Pause/resume preserves game state; restart restores default difficulty.
- Speed changes at the documented score thresholds independently of rendering.
- Persistence, difficulty, pause and UI timing tests pass.

## Sprint 3 acceptance

- The CI/CD graph exposes validation, parallel checks, a quality gate, packaging,
  installation checks, release delivery and an overall summary.
- Full tests pass on all six OS/Python combinations and combined statement/branch
  coverage is at least 85%.
- Dependency auditing passes, and the existing security requirements are reviewed
  against their issue scope and test evidence.
- The built wheel installs and its module/console entry point runs on all three
  OSes; checked packages and reports are downloadable from GitHub Actions.
- Native window/input behavior and interactive performance are recorded through
  the manual acceptance procedure in README before desktop acceptance is claimed.

The GitHub tracker is the source for current issue status. A closed issue or an
automated headless test alone does not establish completion of manual acceptance.
