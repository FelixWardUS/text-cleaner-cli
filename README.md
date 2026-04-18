# Text Cleaner CLI

A simple command-line tool to clean up messy text files and copied text snippets.

## Features

- Remove extra spaces
- Collapse repeated blank lines
- Normalize line endings
- Clean repeated punctuation
- Read from `stdin`, one file, or multiple files
- Disable individual cleaning rules with `--no-*` flags

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

Clean text from a pipe:

```bash
cat input.txt | text-cleaner
```

Disable individual rules:

```bash
text-cleaner --no-repeated-punctuation --no-blank-lines input.txt
```

## Options

- `--no-normalize-line-endings`: keep original line endings
- `--no-repeated-punctuation`: keep repeated `!`, `?`, `.`, and `,`
- `--no-extra-spaces`: keep repeated spaces and tabs
- `--no-blank-lines`: keep repeated blank lines

## Output

Single input source writes cleaned text directly to `stdout`.

Multiple file inputs write a header before each cleaned file block:

```text
==> file1.txt <==
cleaned content...

==> file2.txt <==
cleaned content...
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
