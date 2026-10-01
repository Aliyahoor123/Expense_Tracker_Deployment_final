import sys, json
data = json.load(sys.stdin)
cmd = data.get('tool_input', {}).get('command', '')
protected = ['spendly.db', '.env', 'migrations/']
dangerous = ['rm ', 'rm -', 'unlink ', 'truncate ']
for d in dangerous:
    if d in cmd:
        for p in protected:
            if p in cmd:
                print(f'BLOCKED: Cannot run destructive command on protected file: {p}', file=sys.stderr)
                raise SystemExit(2)
