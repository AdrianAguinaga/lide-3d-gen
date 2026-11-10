@AGENTS.md

## Claude Code specifics
- Skill discovered from `.claude/skills/lide-3d-gen/` (generated copy; edit `agent-capabilities/`).
- Live Blender via the `blender` MCP server (`execute_blender_code`, `look`, `search_assets`, `import_asset`, `generate_3d`).
  If it is not connected, work headless and say so.
- Windows shell: forward slashes, quote paths with spaces (the Blender path has spaces).
