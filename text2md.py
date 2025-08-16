#!/usr/bin/env python3

import argparse
import os
import re
import sys


def find_max_sequence(content, char):
    """
    Find the maximum number of consecutive instances of the given char in the content.
    This helps determine the length of the fence needed to wrap the content safely.
    """
    max_len = 0
    pattern = re.escape(char) + '+'
    for match in re.finditer(pattern, content):
        max_len = max(max_len, len(match.group()))
    return max_len


def detect_language(file_path):
    """
    Detect the programming language based on the file extension.
    Returns the extension without the dot, or None if no extension.
    """
    _, ext = os.path.splitext(file_path)
    if ext:
        return ext.lstrip('.')
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Convert a text file to a Markdown code block suitable for GitHub README.md."
    )
    parser.add_argument("input", help="Input file path (use '-' for stdin)")
    parser.add_argument("output", help="Output file path (use '-' for stdout)")
    parser.add_argument(
        "--lang",
        help="Specify the language for syntax highlighting (overrides auto-detection)",
    )
    parser.add_argument(
        "--tilde",
        action="store_true",
        help="Use tildes (~) instead of backticks for the fence",
    )
    parser.add_argument(
        "--header",
        action="store_true",
        help="Add a Markdown header with the input file name above the code block",
    )

    args = parser.parse_args()

    # Read input
    if args.input == "-":
        content = sys.stdin.read()
    else:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
            sys.exit(1)
        except PermissionError:
            print(f"Error: Permission denied for input file '{args.input}'.", file=sys.stderr)
            sys.exit(1)
        except UnicodeDecodeError:
            print(f"Error: Could not decode input file '{args.input}' as UTF-8.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error reading input: {e}", file=sys.stderr)
            sys.exit(1)

    # Determine language
    lang = args.lang
    if not lang and args.input != "-":
        lang = detect_language(args.input)
    if lang:
        lang = lang.strip()

    # Determine fence character
    fence_char = "~" if args.tilde else "`"

    # Check for invalid info string with backtick fence
    if fence_char == "`" and lang and "`" in lang:
        print("Error: Language info string cannot contain backticks when using backtick fences.", file=sys.stderr)
        sys.exit(1)

    # Calculate fence length
    max_seq = find_max_sequence(content, fence_char)
    fence_len = max(max_seq + 1, 3)

    fence = fence_char * fence_len
    opening_fence = fence + (f" {lang}" if lang else "")

    # Build Markdown
    markdown = opening_fence + "\n" + content + fence + "\n"

    # Add header if requested
    if args.header:
        header_text = f"# Code from {args.input}\n\n" if args.input != "-" else "# Code from stdin\n\n"
        markdown = header_text + markdown

    # Write output
    if args.output == "-":
        sys.stdout.write(markdown)
    else:
        try:
            output_dir = os.path.dirname(args.output)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(markdown)
        except PermissionError:
            print(f"Error: Permission denied for output file '{args.output}'.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error writing output: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
