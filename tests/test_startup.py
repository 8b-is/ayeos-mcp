"""Real MCP transport discovery without contacting an ayeOS daemon."""
import asyncio
import inspect
from pathlib import Path
import runpy
import sys
import types
import unittest
from unittest.mock import patch

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = """
import runpy, sys
runpy.run_path(sys.argv[1], run_name='__main__')
"""


class StartupTests(unittest.TestCase):
    def test_console_entry_is_synchronous_and_runs_stdio(self):
        module = runpy.run_path(str(ROOT / 'server.py'))
        self.assertFalse(inspect.iscoroutinefunction(module['main']))
        with patch.object(module['server'], 'run') as run:
            module['main']()
            run.assert_called_once_with(transport='stdio')

    def test_real_stdio_initialization_and_tool_discovery(self):
        async def check():
            params = StdioServerParameters(command=sys.executable,
                args=['-c', BOOTSTRAP, str(ROOT / 'server.py')])
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    result = await session.initialize()
                    self.assertEqual(result.server_info.name, 'ayeos-mcp')
                    tools = await session.list_tools()
                    self.assertEqual({tool.name for tool in tools.tools},
                        {'genesis', 'capsule', 'stats', 'quantize'})
                    unsupported = await session.call_tool('quantize', {'weights': '[1, 2]'})
                    self.assertTrue(unsupported.is_error)
        asyncio.run(asyncio.wait_for(check(), timeout=15))


if __name__ == '__main__':
    unittest.main()
