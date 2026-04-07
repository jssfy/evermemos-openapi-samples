---
name: everos-sdk-upgrade
description: >
  Migrate EverOS SDK between versions. Auto-detects language (Python/Go/TS) and
  current version, chains rules to target. TRIGGER when: code imports
  evermemos/everos, user mentions upgrade/migrate everos, or dependencies
  contain outdated SDK version.
user-invocable: true
argument-hint: "[target-version, default: latest]"
allowed-tools: Read Grep Glob Edit Bash(python -m py_compile *) Bash(pytest *) Bash(go build *) Bash(npx tsc *)
---

# EverOS SDK Migration

Migrate from any SDK version to a target version (default: latest).
Supports multiple languages. Rules are chained per language.

## Step 1: Detect language

Scan the project to determine which SDK language is in use:

```
Glob pattern="*.py"           → Python
Glob pattern="go.mod"         → Go
Glob pattern="package.json"   → TypeScript
```

Check for SDK references in each:
- **Python**: `evermemos` or `everos` in `*.py`, `pyproject.toml`, `requirements.txt`
- **Go**: `evermemos` or `everos` in `go.mod`, `*.go`
- **TypeScript**: `evermemos` or `everos` in `package.json`, `*.ts`

If multiple languages detected, process each in sequence.

## Step 2: Detect current version

Use Grep to search for SDK usage patterns:

```
Grep pattern="evermemos|everos" glob="*.{py,toml,txt,go,mod,ts,json}"
```

Determine version from the patterns found. For Python:
- `evermemos` + `client.v0.` = **v0**
- `everos` + `client.v1.` = **v1**
- Higher versions: `client.vN.` = **vN**

Other languages follow similar namespace patterns.

## Step 3: Determine target version

- If user specified a target (e.g., `/everos-sdk-upgrade v2`), use that.
- Otherwise, find the highest version by scanning rule files (Step 4).

## Step 4: Discover migration path

Use Glob to find rule files for the detected language:

```
Glob pattern="migration/{language}/v*-to-v*.md" path="${CLAUDE_SKILL_DIR}"
```

Each file covers one version hop. Build the chain from current to target.
Example: v0 -> v3 = `v0-to-v1.md` + `v1-to-v2.md` + `v2-to-v3.md`.

If a required rule file is missing, inform the user and stop.

## Step 5: Apply each migration step

For each version hop, read the rule file and apply changes **in this order**:

1. **Package dependency** (pyproject.toml / go.mod / package.json)
2. **Environment variables** (.env, docker-compose, Dockerfile, CI, code, shell)
3. **Import statements** across all source files
4. **Client instantiation** (class/struct name + constructor params)
5. **API call signatures** (follow the rule file — these may be full rewrites)
6. **Type imports** (response/param type renames)
7. **Exception/error class references**

## Step 6: Suggest package update

After code changes, **tell the user** to update their installed package:

- Python: `pip install everos>=<version>` or `uv sync`
- Go: `go get github.com/evermemos/everos-go@latest`
- TypeScript: `npm install everos@latest`

Do NOT auto-run install commands. The user decides when and how to update.

## Step 7: Verify

Syntax-check modified files per language:

- Python: `python -m py_compile <file>`
- Go: `go build ./...`
- TypeScript: `npx tsc --noEmit`

If tests exist, run them to verify collection.

Report a summary: files modified, changes per category, warnings for removed APIs.

## Verification examples

For complete Before/After code examples to validate migration correctness:
- Python: [examples/python/test_v0_sample.py](examples/python/test_v0_sample.py) → [examples/python/test_v1_expected.py](examples/python/test_v1_expected.py)

## Rules for the migration agent

- Each rule file is self-contained with Before/After code, search patterns, and
  field mappings. Follow the rule file precisely.
- When APIs are **removed** with no replacement, FLAG to the user with a comment
  in the code. Do NOT silently delete.
- Do NOT auto-add new APIs that didn't exist in the source version.
- For complex signature rewrites, restructure carefully — NOT simple find-replace.
