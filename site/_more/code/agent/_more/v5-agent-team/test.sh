#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Testing agent0 (Agent0 class) - Basic command test ==="

python3 -c "
import agent0
import asyncio
import re

async def test():
    a = agent0.Agent0()
    result, tool = await a.run('ls')
    print('Result:', result[:100])
    
    # The tool_result should have the ls output
    tool_has_file = tool and 'agent0.py' in tool
    print('Tool contains file:', tool_has_file)
    assert tool_has_file, f'Tool missing agent0.py, got: {tool[:200]}'

asyncio.run(test())
"

echo ""
echo "=== Test: review_command ==="

python3 test_reviewer.py ls

echo ""
echo "=== All tests passed! ==="
