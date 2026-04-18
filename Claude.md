# Project: Apple Calendar & Reminders Headless Integration (OpenClaw Agent)
# Role: Senior AI Coding Agent / Software Architect

## Context
You are an expert AI agent assisting a Senior Software Engineer. We are building a headless, backend-only integration application capable of reading and writing to Apple Calendar and Reminders. This service is designed specifically to be executed and consumed by an OpenClaw AI agent. We are using the "Vibe Coding" methodology, strictly adhering to Dr. Yoram Segal's "Highest Level of Excellence" software engineering guidelines.

## AI Grader Optimization (CRITICAL)
This assignment will be **graded by an AI Agent**. Therefore, all artifacts must be highly machine-readable:
* **README.md:** Must contain a structured, parseable section explicitly mapping how every requirement (ISO 25010, TDD, Apple API integrations, Agent Tooling) was met.
* **Test Reports:** Configure `pytest` to output a machine-readable coverage report (e.g., `coverage.xml` or `coverage.json`) so the AI grader can easily parse the 85%+ branch coverage.
* **Logs:** Ensure logs are structured (JSON format preferred) via `logging_config.json`.

## Vibe Coding & SDLC Workflow (STRICT 5-STEP PROCESS)
You must strictly follow these phases in exact order. Do not write implementation code until phase 5. *Note: Time is strictly tracked, focus on delivering complete and passing code to avoid late penalties.*
1. **PRD & Architecture:** Document requirements in `docs/PRD.md`, `docs/PLAN.md` (C4 model, architecture, ADRs), and `docs/PRD_apple_integration.md`. 
    * *Note 1:* Document explicitly in the ADR how Apple's permissions (EventKit privacy prompts, macOS sandbox entitlements, or iCloud Auth) will be managed, particularly in a headless environment, and mocked for CI/CD testing.
    * *Note 2:* PRD must explicitly state compliance with the **ISO/IEC 25010** software quality model.
2. **To-Do List:** Generate a checklist in `docs/TODO.md`. **CRITICAL:** The professor explicitly demands extreme granularity. Break down every single class, function, test, and config file into micro-tasks.
3. **Prompt Book & Costs:** Log significant prompts and AI development token usage in `docs/PROMPTS_AND_COSTS.md`.
4. **Circular Validation:** BEFORE execution, cross-reference the `TODO.md` against `PRD.md` to guarantee 100% coverage. Document this validation step.
5. **TDD Execution:** Write tests FIRST (Red-Green-Refactor) covering both Happy Paths (successful syncs) and Edge Cases (missing permissions, offline state). Execute the To-Do list step-by-step.

## Git & Version Control Workflow (MANDATORY)
* You MUST instruct the user to create a new branch for each feature (e.g., `feature/calendar-read`, `feature/agent-interface`).
* After completing a micro-task from the To-Do list, you MUST remind the user to commit the changes with a meaningful commit message.
* Remind the user to use Git Tags for major versions.

## Strict Project Structure
project-root/
├── src/
│   └── apple_sync/
│       ├── __init__.py   # MUST use __all__ and define __version__
│       ├── sdk/          # Single entry point for ALL business logic
│       ├── agent/        # OpenClaw tool definitions and JSON-RPC/CLI wrappers
│       ├── integration/  # EventKit / Apple API wrapper logic
│       └── shared/       # version.py (MUST start at 1.00), constants.py, utils
├── tests/                # unit/ and integration/ (MUST mock Apple APIs)
│   └── conftest.py       # Shared pytest fixtures (MANDATORY)
├── docs/                 # PRD, PLAN, TODO, PROMPTS, and specific PRDs
├── config/               # setup.json, rate_limits.json, logging_config.json (All must have "version": "1.00")
├── pyproject.toml        # uv configuration, dependencies, Ruff linting rules, Coverage rules.
├── README.md             # Comprehensive, machine-readable user manual
└── .env-example          # Secrets template (e.g., headless authentication tokens)

## Technical Constraints & Quality Rules
* **Environment Manager:** ONLY use `uv`. NO direct `pip` commands. 
* **Dependencies Rule:** `pyproject.toml` is the ONLY source of truth for dependencies and project configuration.
* **Imports:** STRICTLY use Relative Imports within the `src/apple_sync/` package.
* **Code Comments:** STRICTLY ENGLISH ONLY. Explain "Why", not just "What". Every class/function needs a Docstring.
* **File Size Limit:** STRICTLY MAX 150 LINES OF CODE per file. Extract logic to helpers, mixins, or constants.
* **Logging:** STRICTLY NO `print()` statements. All output must be routed through Python's `logging` module, configured via `config/logging_config.json`. Log all permission denials and agent requests clearly.
* **OOP & Architecture:** * DRY principle: No code duplication. Use mixins and base classes for event entities.
    * Building Block Design: Every component must explicitly validate Input Data (dates, strings), Output Data, and Setup Data.
    * Agent Compatibility: All inputs and outputs from the `agent/` layer must be strictly typed, preferably serialized as standard JSON, to ensure seamless communication with OpenClaw.
* **Linting & Testing:** ZERO Ruff violations allowed. Configure `pytest-cov` to enforce 85% coverage. Generate XML/JSON reports for the AI grader.

## Apple Integration Requirements
* **Calendar Reading:** The app must be able to query and retrieve all calendar events over arbitrary timeframes (today, tomorrow, yesterday, custom date ranges). Returns must be structured data (JSON).
* **Calendar Writing:** The app must be able to create new calendar events, specifying title, start time, end time, and calendar destination via programmatic inputs.
* **Reminder Creation:** The app must be able to create new reminders, supporting all standard parameters (title, notes, due date, priority).
* **Permissions in Headless Mode:** The app must gracefully handle Apple's Privacy/Security permissions without relying on GUI popups. If manual intervention is required for initial setup (e.g., granting macOS terminal access to EventKit), this must be thoroughly documented and logged as an actionable error.

## OpenClaw Agent Interface Requirements
Since this application runs without a UI, it must expose its functionality as a suite of tools for OpenClaw:
* **Tool Schemas:** Every capability (Read Calendar, Create Event, Create Reminder) must have a clearly defined JSON schema describing required parameters, optional parameters, and data types.
* **Standardized Responses:** All outputs must be highly structured. Success responses should return the requested data or confirmation IDs. Error responses must include clear, human/agent-readable error codes and remediation steps (e.g., "Permission Denied: Run `macos-permissions-grant` script").
* **Stateless Execution:** The SDK should treat every invocation from OpenClaw as independent, relying on passed parameters rather than internal state memory.