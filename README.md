# Prompt Tools for WanGP

A small pack of quality-of-life tools for the [WanGP](https://github.com/deepbeepmeep/Wan2GP) prompt, in a single plugin. Each tool can be switched on or off from the **🧰** menu next to the prompt title.

## Tools

### 🗑 Clear button
- A small 🗑 button next to each prompt field (main prompt, wizard prompt, negative prompt…).
- One click empties the field.
- **Clicked by mistake?** For 8 seconds the button turns into **↩**: click it to get your prompt back.

### 🪟 Window counter
- Shows under the prompt how many **sliding windows** WanGP will actually generate, e.g. `🪟 4 windows detected ✓`. Updates as you type.
- Follows the WanGP setting *How to Process each Line of the Text Prompt* (one line = one window, or one paragraph = one window).
- **Warnings** (click one to jump to the line):
  - a window containing a line break, which would be cut into several windows;
  - a window starting with `overall_soundscape:` or `non_diegetic_music:`, usually an extra empty line that detached a field from its window.
- In non-sliding-window modes, it tells you how many separate videos will be queued.

### 🧰 Menu
- Turn each tool on or off. Your choice is remembered in your browser.
- English or French, automatically, based on your browser language.

## Installation

### From the WanGP Plugin Manager (recommended)
1. Open the **Plugins** tab in WanGP.
2. Paste `https://github.com/MOUGE67/wan2gp-prompt-tools` into the install-from-URL field and install.
3. Enable **Prompt Tools**, fully restart WanGP and reload the page (**Ctrl + F5**).

### Manually
1. Download this repository (green **Code** button → **Download ZIP**).
2. Extract it into `Wan2GP/plugins/` so that you get `Wan2GP/plugins/wan2gp-prompt-tools/plugin.py`.
3. Enable the plugin in the **Plugins** tab, fully restart WanGP and reload the page (**Ctrl + F5**).

### Coming from the standalone plugins?
This pack replaces **Clear Prompt Button** and **Window Counter**. If they are still enabled, Prompt Tools turns off its own copy of those tools to avoid duplicates (the 🧰 menu tells you). For a clean setup, disable or uninstall the standalone plugins.

## Troubleshooting

Open the browser console (**F12 → Console**) and reload the page. You should see `[PromptTools] plugin loaded`.

## How it works

Pure JavaScript injected through WanGP's plugin API (`add_custom_js`). The window counter reproduces WanGP's own prompt splitting rules (`shared/utils/prompt_parser.py`). Nothing touches your models or settings.

## Author

Made by **Mouge**. Feedback and suggestions welcome!
