# PDF Toolkit UI Context

This glossary defines the canonical names for the redesigned desktop UI. The app is a local PySide6/Qt tool; all files stay on the user's machine.

## Language

**Home Grid**:
The first screen after launch: a scrollable grid of tool cards grouped by section. It replaces the old fixed sidebar navigation.
_Avoid_: sidebar, nav list, launcher menu

**Tool Spec**:
One immutable description of a tool: key, label, icon, section, description, input mode, and settings panel key. The tool registry is the only source of truth for available tools.
_Avoid_: nav item, menu entry

**Tool Workspace**:
The screen opened from a tool card. It contains a drop zone and file queue on the left and a tabbed settings/preview panel on the right.
_Avoid_: tool view, tool page, config panel

**Drop Zone**:
The dashed target inside a workspace (and on Home) that accepts dragged files or opens a file browser. It validates file type before handing paths to the session.
_Avoid_: upload area, file dropper

**File Queue**:
The ordered list of files attached to the current tool. It supports selection, reordering, and removal; it is scoped to the workspace, not global.
_Avoid_: library, file list, merge list

**Tool Session**:
The per-tool state object holding the current tool spec, its file queue, image paths, and active file. Opening a tool creates a new session.
_Avoid_: current state, app state, library state

**Settings Panel**:
The "Options" tab in the right panel. It hosts the existing per-tool parameter widgets plus the execute action.
_Avoid_: tool form, config sidebar, right sidebar

**Preview Panel**:
The "Preview" tab in the right panel. It hosts the QtPdf document viewer for the active file.
_Avoid_: preview card, viewer pane

**Output Library**:
The in-memory list of files produced by operations and files loaded through the legacy open path. It is no longer the workspace input queue.
_Avoid_: home library, global queue, loaded files
