import asyncio
import json
import runpy
import socket
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

MODULE = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'server.py'))

class TransportTests(unittest.TestCase):
    def exchange(self, chunks, command='stats'):
        sock = MagicMock()
        sock.__enter__.return_value = sock
        sock.recv.side_effect = chunks
        factory = MagicMock(return_value=sock)
        fake = types.SimpleNamespace(socket=factory, AF_INET=socket.AF_INET,
                                     SOCK_STREAM=socket.SOCK_STREAM, timeout=socket.timeout)
        with patch.dict(MODULE['_memnet'].__globals__, {'socket': fake}):
            try:
                return MODULE['_memnet'](command)
            finally:
                sock.__exit__.assert_called_once()

    def test_fragmented_json(self):
        self.assertEqual(json.loads(self.exchange([b'{"node":', b'1}', b''])), {'node': 1})

    def test_daemon_error_is_exception(self):
        with self.assertRaisesRegex(RuntimeError, 'no capsule'):
            self.exchange([b'{"error":"no capsule"}', b''])

    def test_timeout_does_not_return_partial_success(self):
        with self.assertRaises((RuntimeError, TimeoutError)):
            self.exchange([b'{"node":', socket.timeout('synthetic timeout')])

    def test_response_limit(self):
        with self.assertRaisesRegex(RuntimeError, 'limit'):
            self.exchange([b'x' * (4 * 1024 * 1024 + 1), b''])

    def test_unsupported_quantize_never_connects(self):
        with patch.dict(MODULE['quantize'].__globals__, {'_memnet': MagicMock()}) as scope:
            with self.assertRaisesRegex(NotImplementedError, 'not support'):
                asyncio.run(MODULE['quantize']('[1, 2]'))
            scope['_memnet'].assert_not_called()

if __name__ == '__main__': unittest.main()
