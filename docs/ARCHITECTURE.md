# High-Level Architecture & Refactoring Roadmap

This document outlines the desired target architecture for GAVATCore and a staged plan to refactor the existing codebase incrementally.

## 🚩 Current Challenges
- Monolithic structure with tightly coupled modules
- Fragmented configuration and logging patterns
- Inconsistent error handling and ad-hoc prints
- Missing clear boundaries between domains (API, core engine, bots, pipelines)
- Sparse documentation and uneven test coverage

## 🏛 Target Architecture
We will adopt a layered, modular structure inspired by Clean Architecture / Hexagonal principles:

```
┌───────────────────────────────────────────┐
│             Presentation Layer           │  # Web APIs, CLI, Bot launchers
├───────────────────────────────────────────┤
│             Application Layer            │  # Orchestrators, Use Cases, Handlers
├───────────────────────────────────────────┤
│               Domain Layer               │  # Entities, Core Business Logic
├───────────────────────────────────────────┤
│             Infrastructure Layer         │  # Persistence, External Services, Config
└───────────────────────────────────────────┘
```

**Logical grouping of modules:**
- Presentation: `apis/`, `launchers/`, `services/telegram/bot_manager/`, `web/`
- Application: `pipelines/`, `handlers/`, `modules/*` as orchestrators and handlers
- Domain: `core/`, `gavatcore_engine/`, `character_engine/`, `deep_bait_classifier.py`
- Infrastructure: `config/`, `data/`, `utils/`, `tools/`, external client wrappers

## 🚀 Refactoring Phases
1. **Discovery & Documentation** (current)
   - Audit existing modules, clean up READMEs and module docstrings
   - Establish baseline for tests and CI workflows
2. **Modularization & Dependency Isolation**
   - Create explicit package boundaries for each layer
   - Refactor imports to invert dependencies (application → domain, infra only at edges)
3. **Configuration & Logging Standardization**
   - Centralize all configuration in `infrastructure/config`
   - Replace ad-hoc prints with structured logging conventions
4. **API & Bot Launcher Decoupling**
   - Define common interfaces for bots and launchers
   - Plug implementations via factories and dependency injection
5. **Testing & CI Enhancements**
   - Expand unit tests around domain logic
   - Integrate linting (black/isort/flake8), type checking (mypy), and security scans
   - Automate workflows in CI (GitHub Actions or similar)
6. **Performance & Monitoring Instrumentation**
   - Add standardized metrics collection and health endpoints
   - Implement service-level and application-level monitoring hooks
7. **Iterate & Extend**
   - Continue migrating modules incrementally, verifying through regression tests

## Next Steps
- Review this roadmap with the team and adjust priorities.
- Kick off Phase 1 by integrating this document and updating the top-level README.
- Choose a pilot module (e.g., `character_engine/deep_bait_classifier.py`) for Phase 2 proof-of-concept.
