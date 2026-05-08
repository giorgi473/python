# Modern Async CLI Workbench

A lightweight terminal productivity tool written in Python.

## Project Structure

- `main.py` - Entry point that starts the workbench.
- `workbench.py` - Contains the `ModernWorkbench` class and the interactive command palette.
- `commands.py` - Defines the `Command` dataclass used by the workbench.
- `terminal.py` - Terminal helpers and ANSI styling utilities.

## Features

- Interactive CLI command palette with modern terminal styling.
- System pulse display for environment information.
- Creative prompt generation for project inspiration.
- Focus timer with live progress feedback.
- Visual command flow preview.

## Usage

Run the workbench:

```bash
python main.py
```

Run a single command directly:

```bash
python main.py --command status
```

Available commands:

- `status` - Show system pulse and environment info
- `idea` - Generate a creative prompt
- `timer` - Run a short focus timer
- `demo` - Render a visual command palette preview

## Notes

- The project uses standard Python libraries only.
- For best terminal visuals, use a modern terminal such as Windows Terminal, PowerShell 7+, or any ANSI-compatible terminal.
