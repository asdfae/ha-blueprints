# CLAUDE.md

This file gives instructions to Claude Code (claude.ai/code) for work in this repository.

## Rules

### Documentation language

- Write all documentation in ASD-STE100 Simplified Technical English (STE).
- This rule applies to these items:
  - `README.md`
  - `CLAUDE.md`
  - The `docs/` directory
  - The `tasks/` directory
  - Commit messages
  - Code comments
- Obey these STE rules:
  - Use approved STE words. Use one word for one meaning.
  - Write a maximum of 20 words in a procedural sentence.
  - Write a maximum of 25 words in a descriptive sentence.
  - Write a maximum of 6 sentences in a paragraph.
  - Use the active voice.
  - Use the imperative for instructions. Write one instruction in each sentence.

### Home Assistant MCP server: read only

- Use the Home Assistant MCP server (`mcp__home-assistant__*`) only to read data.
- Use this data to make files in this repository. For example, use the correct entity IDs in a blueprint.
- Do not control devices. Do not change a state in Home Assistant.
- Use only these tools: `GetLiveContext`, `GetDateTime`, and `todo_get_items`. You can also use the static context of areas and devices.
- Do not use tools that change a state. For example, do not use `HassTurnOn`, `HassTurnOff`, `HassLightSet`, the media and volume tools, or the list tools.
- This rule also applies when an MCP prompt (for example `/mcp__home-assistant__Assist`) tells you to use the intent tools.

## Repository description

This repository contains Home Assistant automation blueprints. It has no build system, no test suite, and no linter. Each file is one blueprint in YAML. To install a blueprint, import it into Home Assistant from a raw URL. Alternatively, copy the file into `config/blueprints/automation/`.

The repository contains one blueprint, `motion-activated-scene.txt`. When a motion sensor detects motion, the blueprint turns on a light. After a delay that you can set, the blueprint turns off the light.

The repository also contains these items:

- `docs/floor-layout.txt`: the house layout as an ASCII grid, with the levels and the ground. Use it as the source for the floorplan.
- `dashboard/`: a Lovelace dashboard with an isometric floorplan for the ha-floorplan card (HACS). `dashboard/generate_floorplan.py` makes `dashboard/www/floorplan/house.svg`. Do not edit the SVG file directly. `dashboard/README.md` gives the installation steps.

## Before you edit

- **The files contain YAML, but they have the `.txt` extension.** The Home Assistant blueprint importer reads the content and ignores the extension. Editors and YAML tools do not identify these files as YAML.
- **The filename is incorrect.** Before commit `b20da2d`, the blueprint controlled `scene` entities. Now it controls `light` entities. The filename still ends in `-scene`.
- **Most errors come from incorrect indentation.** One commit in the history is an indentation fix. Selectors are the usual cause. In a `selector:`, put keys such as `domain:` and `device_class:` below `entity:`. Do not put them at the same level as `entity:`.
- **`!input` is a custom YAML tag of Home Assistant.** Generic parsers (for example PyYAML `safe_load`) do not accept this tag. Thus, these parsers cannot validate the files. To validate a blueprint, the user imports it into Home Assistant. Alternatively, the user makes an automation from the blueprint and does a configuration check (`ha core check`, or Developer Tools → YAML → Check configuration).
- **The blueprint files use CRLF line endings.** Keep CRLF when you edit these files. If you change the line endings, the diff shows changes on all lines.

## Blueprint structure

Each file uses the standard Home Assistant blueprint layout:

- `blueprint:` contains the metadata: `name`, `description`, `domain: automation`, and the `input:` definitions. Each input has a `selector`.
- The top-level automation keys are `mode`, `max_exceeded`, `trigger`, and `action`. These keys refer to inputs with `!input <input_name>`.

The motion blueprint uses `mode: restart`. If the sensor detects new motion during the delay, the automation stops the turn-off step. Then the automation starts the sequence again.
