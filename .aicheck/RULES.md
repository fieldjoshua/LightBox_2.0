# AICheck Rules (Simplified)

This document defines the governance framework for AICheck-managed projects. These rules cannot be modified without approval from Joshua Field.

> **Quick Navigation**: [Core Principles](#1-core-principles) | [Action Workflow](#2-action-workflow) | [AI Guidelines](#3-ai-assistant-guidelines) | [Testing & Deployment](#4-testing-and-deployment) | [Standards](#5-standards) | [Reference](#6-reference)

---

## 1. CORE PRINCIPLES

### 1.1 Foundation Rules
- **One ActiveAction per person** - Complete or pause before switching
- **Documentation-first approach** - PLAN.md required and approved before implementation
- **Test-driven development** - Tests created and approved before implementation
- **Production deployment verification** - "Code complete" ≠ "deployed and working"

### 1.2 Work Definition
The PROJECT creates a PROGRAM with specific functions. Each ACTION is a sub-objective contributing to program functionality. EDITORS perform ACTIONS to progress the PROGRAM.

**Value Creation**: Efficient, quality work that progresses ACTIONS toward completion has the highest value.

---

## 2. ACTION WORKFLOW

### 2.1 ACTION Lifecycle
```
Plan → Approve → Implement → Test → Deploy → Complete
```

1. **Create**: `./aicheck new [action-name]` with PLAN.md
2. **Approve**: Human approval of PLAN.md required
3. **Activate**: `./aicheck active [action-name]`
4. **Implement**: Follow approved PLAN.md
5. **Test**: All tests must pass
6. **Deploy**: Production verification required
7. **Complete**: `./aicheck complete [action-name]`

### 2.2 Required Files
Every ACTION must contain:
- **`[action-name]-plan.md`** - Detailed implementation plan
- **`todo.md`** - Task tracking and progress
- **`deployment-verification.md`** - Production test evidence (if applicable)

### 2.3 Directory Structure
```
.aicheck/actions/[action-name]/
├── [action-name]-plan.md          # Required: Implementation plan
├── todo.md                        # Required: Task tracking
├── deployment-verification.md     # Required: Production evidence
└── supporting_docs/              # Optional: Process documentation
    ├── claude-interactions/      # AI assistant logs
    ├── research/                 # Research and analysis
    └── process-tests/           # Temporary test files
```

---

## 3. AI ASSISTANT GUIDELINES

### 3.1 Scope and Boundaries
- **Follow approved PLAN.md exactly** - No scope creep without human approval
- **One ACTION focus** - Stay within current ActiveAction boundaries
- **Human approval required** for:
  - Plan modifications
  - New ACTION creation
  - Production deployments
  - Major architectural changes

### 3.2 Documentation Requirements
- **Log interactions** in `supporting_docs/claude-interactions/`
- **Update todo.md** for all task progress
- **Document decisions** with rationale
- **Capture research** in `supporting_docs/research/`

### 3.3 Quality Standards
- **Test-first approach** - Create/run tests before implementation
- **Follow code standards** - Maintain consistency with existing codebase
- **Production verification** - Test actual production URLs, not localhost
- **Evidence capture** - Document all verification steps

---

## 4. TESTING AND DEPLOYMENT

### 4.1 Test-First Requirements
- Tests must be created and approved via PLAN.md before implementation
- All tests must pass for ACTION completion
- Test files organization:
  - Process tests: `supporting_docs/process-tests/`
  - Product tests: `/tests/[category]/`

### 4.2 Production Verification Checklist
**⚠️ MANDATORY for production systems:**

- [ ] Code pushed to correct branch
- [ ] Deployment triggered successfully
- [ ] Build completed without errors
- [ ] **Production URL responds correctly**
- [ ] **All endpoints tested and documented**
- [ ] Performance acceptable
- [ ] Create `deployment-verification.md` with evidence
- [ ] Document actual production test results

### 4.3 Deployment Evidence
**Required documentation:**
- Production URLs tested with timestamps
- Response/output captured as evidence
- Error handling verified in production context
- Platform-specific configuration confirmed

---

## 5. STANDARDS

### 5.1 Code Style
- **Consistency** - Follow existing codebase patterns
- **Clarity** - Readable, maintainable code
- **Error handling** - Comprehensive error management
- **Security** - Follow security best practices

### 5.2 Documentation Format
- **Markdown** for all documentation
- **Clear headings** and consistent structure
- **Actionable content** - specific steps and requirements
- **Evidence-based** - include examples and proof

### 5.3 Git Workflow
- **Meaningful commits** - Clear, descriptive messages
- **Atomic commits** - One logical change per commit
- **Branch strategy** - Follow project conventions
- **No force push** to main/master branches

---

## 6. REFERENCE

### 6.1 Glossary
- **PROJECT** - The overall software development initiative
- **PROGRAM** - The software system being built
- **ACTION** - A specific work unit with defined objectives
- **EDITOR** - A person or AI assistant performing work
- **ActiveAction** - The currently active ACTION for an EDITOR
- **PLAN** - The detailed implementation strategy for an ACTION

### 6.2 Commands Reference
```bash
./aicheck new [action-name]      # Create new ACTION
./aicheck active [action-name]   # Set active ACTION
./aicheck status                 # Show current status
./aicheck complete              # Complete active ACTION
./aicheck focus                 # Check for scope creep
./aicheck cleanup               # Optimize and fix issues
```

### 6.3 Exception Handling
**Rule violations require:**
1. Immediate documentation in ACTION's supporting_docs
2. Human approval for any deviation
3. Corrective action plan
4. Process improvement recommendations

**Critical violations** (deployment without verification, scope creep, unapproved changes) may result in ACTION rollback.

---

## Migration from Original RULES.md

This simplified version consolidates the original 16-section, 1,012-line RULES.md into 6 focused sections. All core governance principles are preserved while eliminating redundancy and improving clarity for both human and AI users.

**Key improvements:**
- 60% reduction in length
- Eliminated redundant deployment verification content
- Consolidated AI assistant guidance
- Clearer decision trees and workflows
- Improved navigation and reference structure

For the complete original rules, see `RULES.md`. This simplified version takes precedence for day-to-day operations.