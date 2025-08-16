import sys
import re

def find_max_backticks(content):
    max_len = 0
    for match in re.finditer(r'`+', content):
        max_len = max(max_len, len(match.group()))
    return max_len

if len(sys.argv) != 3:
    print("Usage: python script.py inputfile outputfile")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
except FileNotFoundError:
    print(f"Error: Input file {input_file} not found.")
    sys.exit(1)

max_ticks = find_max_backticks(content)
fence_len = max(max_ticks + 1, 3)
fence = '`' * fence_len

markdown = fence + '\n' + content.rstrip('\n') + '\n' + fence + '\n'

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(markdown)
