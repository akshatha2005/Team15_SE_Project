# Project Deviations & Scope Adjustments — Team 15 (Snake Game)

This document records any variances or adjustments from the initial project scope throughout the development of the Snake Game project.

---

## 1. Scope & Deliverables Status
* **All Major Artifacts Completed:** All core deliverables—including the System Requirements Specification (SRS), Software Architecture Document (SAD), Test Plan, automated test suite (`pytest`), code coverage reports, project task tracking, and video demonstrations—have been successfully implemented, recorded, and pushed to the repository.
* **Minor Adjustments:** 
  * **Test Case Presentation:** The Test Plan was expanded to incorporate robust automated test-driven validation (95 passing tests) alongside the structured functional/non-functional coverage.
  * **Architecture Refinement:** The SAD was tailored specifically to document the modular event-driven structure of the Pygame engine (`game_engine.py`, `ui.py`, `storage.py`) rather than generic enterprise microservice patterns.

## 2. Sprint organization
The existing tracker is organized into three GitHub milestones: Core Gameplay;
Persistence and Advanced Gameplay; and Quality, Security and Delivery. Existing
issue states are retained, and future online-leaderboard work remains in the backlog.
See [the sprint plan](sprints.md) for the issue mapping and acceptance criteria.
CI/CD now produces current test and coverage evidence on each run. Native desktop
acceptance still requires the manual checks documented in README.
