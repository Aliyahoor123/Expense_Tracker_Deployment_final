import sys, json, subprocess
data = json.load(sys.stdin)
file = data.get('tool_input', {}).get('file_path', '')
if file.endswith('.py'):
    subprocess.run(['python3', '-m', 'black', '--quiet', file])
