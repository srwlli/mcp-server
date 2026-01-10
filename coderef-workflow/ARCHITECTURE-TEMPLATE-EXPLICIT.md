# Architecture Reference

---
## METADATA (Required for Planning Validation)

**Entry Point:** server.py
**Main Components:** PlanningAnalyzer, PlanGenerator, WorkorderValidator
**Architecture Pattern:** MCP Server
**Framework:** Python + MCP Protocol
**Primary Language:** Python
**Secondary Languages:** None

---

## Purpose

This document describes the architectural design of the {PROJECT_NAME}, including system patterns, component interactions, data flow, and key design decisions.

---

## Overview

{High-level project description}

**Core Principles:**
1. Principle 1
2. Principle 2
3. Principle 3

---

## System Architecture

### Entry Point Analysis

**File:** server.py
**Type:** MCP Server
**Initialization Flow:**
1. Load MCP protocol handler
2. Register 13 tools
3. Start stdio server

**Critical Components:**
- PlanningAnalyzer (generators/planning_analyzer.py) - Analyzes project structure
- PlanGenerator (generators/plan_generator.py) - Creates implementation plans
- WorkorderValidator (generators/workorder_validator.py) - Validates workorder format

---

## Component Layers

(Rest of architecture doc...)

---

## EXPLICIT CONTEXT RULES

**REQUIRED sections for planning validation:**
1. METADATA section with Entry Point
2. Main Components list (3-10 components)
3. Architecture Pattern (MCP Server, REST API, CLI Tool, etc.)

**This structured format enables:**
- Machine-readable entry point extraction
- Validation that explicits exist before planning
- Zero-guessing context provision to AI agents
