# ayeos-mcp

**MCP server for [ternary matrix inference](https://github.com/8b-is/ayeos)**
over [Model Context Protocol](https://modelcontextprotocol.io) using the protocol version negotiated by the installed SDK.

## Tools

- `genesis`
- ` capsule`
- ` stats`
- ` quantize`

## Usage

```bash
python -m pip install .
ayeos-mcp
```

Requires: ayeosd running on localhost:9876 for tool calls.
Test startup and discovery without a daemon: `python -m unittest discover -s tests -v`.
These tests do not validate matrix operations or the daemon command protocol.

## The 8b-is MCP Ecosystem

| MCP Server | Purpose |
|------------|---------|
| **honest-irc-mcp** | Quantum-proof messaging + honesty-auth |
| **ayeos-mcp** | Ternary matrix inference (LINOSV seed) |
| **mlx-quant-mcp** | Ternary quantization (BitNet b1.58) |
| **bluesky-mcp** | AT Protocol (24 tools) |

**[axiomquant.org](https://axiomquant.org)** · **[pocoo.vaked.dev](https://pocoo.vaked.dev)**

The current daemon has no `quantize` command, so that tool returns an MCP error without connecting. `stats` returns node address metadata. Responses must be valid JSON, finish within five seconds, and fit within 4 MiB; incomplete or daemon-error responses are tool errors.
