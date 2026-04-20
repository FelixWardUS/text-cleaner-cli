# Text Cleaner CLI

A simple command-line tool to clean up messy text files and copied text snippets.

## Features

- Remove extra spaces
- Remove trailing whitespace
- Remove zero-width characters
- Collapse repeated blank lines
- Normalize line endings
- Normalize Unicode text
- Normalize curly quotes, dashes, and ellipses
- Clean repeated punctuation with loose or strict modes
- Preserve Markdown fenced code blocks by default
- Read from `stdin`, files, directories, or glob patterns
- Filter batch inputs with `--include` and `--exclude`
- Summarize multi-file batches with success, failure, and changed counts
- Disable or override individual cleaning rules with flags

## Installation

For local development:

```bash
python -m pip install -e .[dev]
```

If your Python environment is externally managed, create a virtual environment first or use your preferred Python package manager.

## Usage

Clean one file:

```bash
text-cleaner input.txt
```

Clean multiple files:

```bash
text-cleaner file1.txt file2.txt
```

Clean every file under a directory:

```bash
text-cleaner docs/
```

Clean files matched by a quoted glob:

```bash
text-cleaner "docs/**/*.md"
```

Filter a batch:

```bash
text-cleaner docs/ --include "*.md" --exclude "docs/drafts/*"
```

Clean text from a pipe:

```bash
cat input.txt | text-cleaner
```

Disable individual rules:

```bash
text-cleaner --no-repeated-punctuation --no-blank-lines input.txt
```

Use a preset:

```bash
text-cleaner --preset aggressive input.txt
```

Clean Markdown code blocks too:

```bash
text-cleaner --clean-code-blocks README.md
```

## Options

- `--preset minimal|normal|aggressive`: choose a rule bundle. Default: `normal`
- `--unicode-form none|NFC|NFD|NFKC|NFKD`: choose Unicode normalization. Default: `NFC`
- `--punctuation-mode loose|strict|off`: choose repeated punctuation handling
- `--no-normalize-line-endings`: keep original line endings
- `--no-repeated-punctuation`: keep repeated `!`, `?`, `.`, and `,`
- `--no-typography`: keep curly quotes, dashes, and ellipses unchanged
- `--keep-zero-width-chars`: keep zero-width characters
- `--keep-trailing-whitespace`: keep trailing spaces and tabs
- `--clean-code-blocks`: apply rules inside Markdown fenced code blocks
- `--include PATTERN`: include files matching a shell-style pattern. Can be repeated
- `--exclude PATTERN`: exclude files matching a shell-style pattern. Can be repeated
- `--no-extra-spaces`: keep repeated spaces and tabs
- `--no-blank-lines`: keep repeated blank lines

Presets:

- `minimal`: safe cleanup only; keeps repeated punctuation, typography, and internal spacing
- `normal`: default cleanup; normalizes Unicode, typography, spaces, blank lines, and loose punctuation
- `aggressive`: uses `NFKC` Unicode normalization and strict punctuation mode

## Output

Single input source writes cleaned text directly to `stdout`.

Multiple file inputs write a header before each cleaned file block:

```text
==> file1.txt <==
cleaned content...

==> file2.txt <==
cleaned content...
```

Multi-file batches also write a summary to `stderr`:

```text
Processed 2 files: 2 succeeded, 0 failed, 2 changed.
```

The CLI does not modify files in place.

## Examples

```bash
printf '  Hello!!!\n\n\nWorld...  \n' | text-cleaner
```

Output:

```text
Hello!

World.
```

## Development

Run the test suite:

```bash
pytest -q
```

## License

MIT
