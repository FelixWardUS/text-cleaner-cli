# Text Cleaner CLI Design

## Summary

`text-cleaner-cli` is a small Python command-line tool for cleaning messy plain text from either standard input or one or more file paths. The first version focuses on a narrow, predictable feature set: normalize line endings, collapse repeated punctuation, remove extra spaces, and collapse repeated blank lines.

The project is intentionally scoped as a Unix-style text filter. It reads text, applies a fixed cleaning pipeline, and writes the result to standard output. It does not modify files in place in the first version.

## Goals

- Provide a simple CLI for cleaning copied text snippets and plain text files
- Support both `stdin` input and file path input
- Enable all four cleaning rules by default
- Allow each rule to be disabled with a `--no-*` flag
- Keep the implementation small, testable, and easy to extend

## Non-Goals

- In-place file editing such as `--in-place`
- Unicode normalization or language-aware cleanup
- Spelling correction, capitalization repair, or quote normalization
- Markdown- or code-aware formatting behavior
- Mixing file path arguments with `stdin` in one invocation

## User-Facing Behavior

### Input Modes

The CLI supports two input modes:

1. If one or more file paths are provided, the CLI reads those files in the order given.
2. If no file paths are provided, the CLI reads from `stdin`.

The first version does not support combining explicit file path arguments with piped `stdin` input in the same command. File arguments take precedence; when they are present, `stdin` is ignored.

### Output Modes

- For `stdin` input, the cleaned text is written directly to `stdout` with no header.
- For a single file input, the cleaned text is written directly to `stdout` with no header.
- For multiple file inputs, the cleaned content for each file is written to `stdout` in argument order with a separator header before each file:

```text
==> file1.txt <==
cleaned content...

==> file2.txt <==
cleaned content...
```

The separator is only used when more than one file path is processed in a single invocation.

To keep multi-file output unambiguous:

- Each file block starts with its separator header
- The cleaned content follows on the next line
- If a cleaned file result does not end with a newline, the CLI appends one before writing the next file block
- Separate file blocks with a single blank line

### Rule Flags

All four rules are enabled by default. Each rule can be disabled independently:

- `--no-normalize-line-endings`
- `--no-repeated-punctuation`
- `--no-extra-spaces`
- `--no-blank-lines`

The CLI does not need explicit `--enable-*` flags in the first version because the default is already “all on.”

## Cleaning Rules

The cleaning pipeline runs in a fixed order so behavior stays predictable:

1. Normalize line endings
2. Clean repeated punctuation
3. Remove extra spaces
4. Collapse repeated blank lines

### 1. Normalize Line Endings

Convert all `\r\n` and bare `\r` sequences to `\n`.

Examples:

- `"a\r\nb\r\n"` becomes `"a\nb\n"`
- `"a\rb"` becomes `"a\nb"`

### 2. Clean Repeated Punctuation

Collapse consecutive repeated punctuation characters from this set: `!`, `?`, `.`, `,`

Examples:

- `"Hello!!!"` becomes `"Hello!"`
- `"Wait....."` becomes `"Wait."`
- `"Really???"` becomes `"Really?"`

Mixed punctuation such as `"?!?!"` is left unchanged in the first version because the repeats are not the same character.

### 3. Remove Extra Spaces

For each line:

- Trim leading whitespace
- Trim trailing whitespace
- Collapse internal runs of spaces and tabs to a single ASCII space

Examples:

- `"  hello   world  "` becomes `"hello world"`
- `"a\t\tb"` becomes `"a b"`

This rule only targets horizontal whitespace inside individual lines. It does not join lines together.

### 4. Collapse Repeated Blank Lines

Collapse runs of blank lines down to a single blank line.

Examples:

- `line1\n\n\nline2` becomes `line1\n\nline2`

A blank line means a line that is empty after the extra-spaces rule has already trimmed it.

## Architecture

The implementation should use a small modular Python package rather than a single script. The goal is to keep argument parsing, orchestration, and text cleanup logic separate so each piece is easy to test.

Recommended file layout:

- `pyproject.toml`
- `src/text_cleaner_cli/__init__.py`
- `src/text_cleaner_cli/cli.py`
- `src/text_cleaner_cli/cleaner.py`
- `src/text_cleaner_cli/rules.py`
- `tests/test_rules.py`
- `tests/test_cleaner.py`
- `tests/test_cli.py`

### Module Responsibilities

#### `cli.py`

- Define the command-line interface
- Parse file arguments and `--no-*` flags
- Decide whether to read from files or `stdin`
- Emit output to `stdout`
- Emit user-facing errors to `stderr`
- Return process exit codes

#### `cleaner.py`

- Define a small configuration object representing enabled rules
- Apply the selected rules in the fixed pipeline order
- Expose one orchestrating function for “clean this text with this configuration”

#### `rules.py`

- Implement one pure function per cleaning rule
- Keep rules independent and easy to unit test

## Data Flow

For `stdin` mode:

1. CLI parses flags
2. CLI reads all text from `stdin`
3. CLI builds the rule configuration
4. Cleaner applies enabled rules in order
5. CLI writes cleaned output to `stdout`

For file mode:

1. CLI parses flags and file path arguments
2. CLI iterates through file paths in the order provided
3. CLI reads each file as text
4. Cleaner applies enabled rules in order
5. CLI writes cleaned output to `stdout`
6. If multiple files are being processed, CLI writes a separator before each file’s cleaned content

## Error Handling

The first version should keep error handling explicit and minimal.

### No Input

If no file paths are provided and `stdin` is interactive with no piped or redirected content available, the CLI should print a short usage-oriented message to `stderr` and return a non-zero exit code.

Example message:

```text
No input provided. Pipe text to stdin or pass one or more file paths.
```

### File Read Errors

If a provided file cannot be opened or read, the CLI should print an error message to `stderr` that includes the path and return a non-zero exit code.

Example message:

```text
Failed to read file: notes.txt
```

The CLI may fail fast on the first unreadable file. That behavior is acceptable for the first version.

### Decode Errors

The first version targets normal text input and may treat decode failures as read failures. No custom encoding flags are required.

## Testing Strategy

The project should be test-driven and split tests by responsibility.

### `tests/test_rules.py`

Unit tests for each rule function:

- Normalize Windows and classic Mac line endings
- Collapse repeated punctuation for supported characters
- Leave mixed punctuation unchanged
- Trim line edges and collapse internal runs of spaces and tabs
- Collapse multiple blank lines to one blank line

### `tests/test_cleaner.py`

Pipeline tests:

- All rules enabled in the expected order
- Selected rules disabled with configuration flags
- Blank-line collapsing works correctly after whitespace trimming

### `tests/test_cli.py`

CLI behavior tests:

- Reads from `stdin` and prints cleaned text
- Reads a single file and prints cleaned text with no header
- Reads multiple files and prints separator headers
- Ensures multi-file output stays separated even when an input does not end with a trailing newline
- Respects each `--no-*` flag
- Returns non-zero and prints an error when no input is provided
- Returns non-zero and prints an error for an unreadable file

## Implementation Notes

- Use the standard library where practical: `argparse`, `pathlib`, `sys`, and `re` are sufficient
- Package the CLI with a console entry point so users can run `text-cleaner`
- Keep rule functions pure and string-in/string-out
- Keep output formatting logic in the CLI layer, not in the rule layer

## Open Decisions Resolved

The following decisions were made during design and are now fixed for the first version:

- Implementation language: Python
- Inputs: `stdin` and file paths
- Output target: `stdout`
- Multiple files: separator headers enabled
- In-place writes: not supported in v1
- Rule toggles: default-on with `--no-*` disable flags

## Success Criteria

The first version is successful if:

- A user can clean piped text from `stdin`
- A user can clean one or more text files by passing paths
- The default invocation enables all four rules
- Any individual rule can be disabled with a flag
- Multi-file output is clearly separated
- Behavior is covered by automated tests
