---
name: code-review
description: Multi-language code review skill with security audit and performance optimization suggestions
---

# Code Review Skill

## Overview

Comprehensive code review skill that supports:
- Code logic review and improvement suggestions
- Security audit (SQL injection, XSS, etc.)
- Performance optimization suggestions
- Multi-language support: JavaScript, TypeScript, Python, Go, Java, Rust, C++

## Usage

### Interactive Mode (Paste Code)

```bash
/spencergo:code-review
```

Or describe your review needs:
- "Review this code"
- "Check for security issues"
- "Optimize this function"

### Project Mode (Review Files)

```bash
/spencergo:code-review
/path/to/project
```

## Review Dimensions

### 1. Code Quality

- Code logic and correctness
- Readability and maintainability
- Naming conventions
- Code structure and organization
- Duplication detection
- Comment quality

### 2. Security Audit

- SQL injection vulnerabilities
- XSS (Cross-Site Scripting)
- CSRF vulnerabilities
- Authentication issues
- Authorization problems
- Sensitive data exposure
- Command injection
- Path traversal
- Deprecated APIs

### 3. Performance

- Time complexity analysis
- Space complexity analysis
- Database query optimization
- Caching suggestions
- N+1 query detection
- Memory leaks
- Unnecessary computations

### 4. Best Practices

- Language-specific best practices
- Framework conventions
- Design patterns usage
- Error handling
- Testing coverage

## Input Methods

### Method 1: Paste Code Directly

Paste code blocks and ask for review:
```
// Review this code
function getUser(id) {
  return db.query(`SELECT * FROM users WHERE id = ${id}`);
}
```

### Method 2: File Path

Provide file path for review:
```
Review /path/to/src/index.js
```

### Method 3: Project Directory

Review entire project:
```
Review my project at ./src
```

## Output Format

### Summary Section

```
## Code Review Summary

| Category | Issues | Severity |
|----------|--------|----------|
| Security | 3 | HIGH |
| Performance | 2 | MEDIUM |
| Code Quality | 5 | LOW |
| Best Practices | 4 | LOW |

Overall Score: 7/10
```

### Detailed Issues

For each issue:
```
## [HIGH] SQL Injection Vulnerability

**File:** src/db.js:15

**Code:**
```javascript
return db.query(`SELECT * FROM users WHERE id = ${id}`);
```

**Problem:** User input directly concatenated into SQL query

**Suggestion:**
```javascript
return db.query('SELECT * FROM users WHERE id = ?', [id]);
```
```

## Supported Languages

| Language | File Extensions |
|----------|-----------------|
| JavaScript | .js, .mjs |
| TypeScript | .ts, .tsx |
| Python | .py |
| Go | .go |
| Java | .java |
| Rust | .rs |
| C++ | .cpp, .cc, .h |
| C# | .cs |
| Ruby | .rb |
| PHP | .php |

## Review Process

1. **Input Recognition** - Determine review type (paste/path/project)
2. **Language Detection** - Auto-detect programming language
3. **Code Parsing** - Understand code structure
4. **Multi-dimensional Review** - Run checks in parallel:
   - Security scan
   - Performance analysis
   - Quality check
   - Best practices
5. **Result Aggregation** - Combine all findings
6. **Report Generation** - Format output with severity

## Severity Levels

- **CRITICAL** - Security vulnerabilities, potential data loss
- **HIGH** - Serious bugs, security risks
- **MEDIUM** - Performance issues, maintainability problems
- **LOW** - Style issues, minor improvements
- **INFO** - Suggestions, best practices

## Next Step Guide (MUST FOLLOW)

After code review, you may:

1. **Security issues found** → Recommend `code-review:security` for deeper security analysis
2. **Performance issues found** → Recommend `code-review:performance` for detailed performance analysis
3. **Need fixes applied** → Offer to apply fixes directly
4. **Need explanations** → Provide detailed explanations of any issue

Example transitions:
- "For more detailed security analysis, use /spencergo:code-review:security"
- "I can apply these fixes if you'd like"
- "Would you like me to explain any of these issues in more detail?"
