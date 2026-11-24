# PDF Toolkit — UI/UX Audit & Enhancement Specification

**Date:** 2026-11-23  
**Target:** PDF Toolkit Native Desktop App (PySide6 / Qt)  
**Evaluator:** Antigravity UI/UX Specialist  
**Design Reference:** [DESIGN.md](DESIGN.md) (Vite / VitePress Dark Design System)

---

## 1. Executive Summary & Design Health Score

An in-depth UI/UX evaluation was conducted on the PDF Toolkit desktop interface against Nielsen’s 10 Usability Heuristics, accessibility standards (WCAG 2.1 AA), and cognitive ergonomics.

| # | Heuristic | Score | Assessment & Key Finding |
|---|-----------|:-----:|--------------------------|
| 1 | **Visibility of System Status** | 2/4 | Clear "OFFLINE" badge and status indicators, but empty states provide no live drag-and-drop feedback or drop target indication. |
| 2 | **Match System & Real World** | 2/4 | **Critical Flaw:** Clicking "Merge" presents an abstract config panel instead of an active document assembly workbench. Telling users to manage files in "Home Library" breaks natural task models. |
| 3 | **User Control & Freedom** | 3/4 | Responsive navigation, but zero direct controls within tool panels to add, remove, or reorder files without leaving the view. |
| 4 | **Consistency & Standards** | 2/4 | "Merge" title and subtitle appear 3 times concurrently on screen. Multiple duplicate "Open PDF" buttons compete visually. |
| 5 | **Error Prevention** | 3/4 | Action buttons disable safely when preconditions are missing, but truncated warning copy conceals operational details. |
| 6 | **Recognition Rather Than Recall** | 2/4 | Forces users to mentally track which documents are loaded in the Home Library rather than displaying the file queue in the active merge view. |
| 7 | **Flexibility & Efficiency** | 2/4 | High friction round-tripping: Home (load/reorder) → Merge (configure) → Home (review results). |
| 8 | **Aesthetic & Minimalist Design** | 2/4 | Sleek dark palette, but severe space imbalance: ~62% wasted on an empty preview void while tool options suffer severe text clipping. |
| 9 | **Error Recovery** | 3/4 | Inline notice banner provides direct action button to resolve missing file state. |
| 10 | **Help & Documentation** | 3/4 | Keyboard shortcut modal and navigation tooltips are present, but the top-right `?` button has poor contrast and visual affordance. |
| **Total** | | **24/40** | **Acceptable (60%)** — Requires structural UX and visual hierarchy improvements. |

---

## 2. Priority Issues Breakdown

### [P1] Disconnected Workflow: Merge Tool Detached from File Management
- **Problem:** When navigating to "Merge", the UI displays:
  - *"Notice: No PDF loaded. Open a PDF to configure and run this tool."*
  - *"Combines all documents currently loaded in the Home Library in top-to-bottom sequence. You can drag files in the library to adjust their merge order."*
  - Preview card: *"No PDF Selected. Load a PDF from the Home view to preview it here."*
- **User Impact:** High cognitive friction. Users expect a PDF merge tool to let them add files, arrange sequence order, remove files, and inspect page counts directly inside the Merge view.
- **Remediation:** Embed an in-place Merge File Queue and Dropzone directly inside the Merge tool panel. Users can add files, drag/drop files, reorder up/down, remove individual items, or clear all, seamlessly synchronizing with the underlying document state.

### [P1] Header Duplication & Visual Echo
- **Problem:** The word "Merge" and the subtitle "Combine multiple PDFs into one" appear redundantly in three places at once:
  1. Highlighted active item in Sidebar.
  2. Top window Header bar (`#HeaderTitle` & `#HeaderSubtitle`).
  3. Inside the central tool card (`#ToolHeaderTitle` & `#ToolHeaderDesc`).
- **User Impact:** Wastes vertical real estate (~65px) and creates repetitive visual noise.
- **Remediation:** Remove the redundant in-card title and description. Allow the window header to serve as the unified title and context bar for the active tool.

### [P1] Splitter Imbalance & Copy Truncation
- **Problem:** The central splitter ratio defaults to `[460, 740]`, allocating only 38% width to the tool configuration while granting 62% width to the preview pane. Consequently:
  - Notice label truncates against its button: `Notice: No PDF loaded. Open a PDF to configure and run...`
  - Info banner label truncates: `...in top... sequence`
  - Format support copy truncates: `...from all files are pre...`
- **User Impact:** Degraded readability and poor responsiveness.
- **Remediation:** 
  - Rebalance splitter default sizes to `[540, 660]`.
  - Set minimum widths and robust word-wrapping (`setWordWrap(True)`) on all banner labels and hints.
  - Ensure labels expand with layout geometry.

### [P2] Competing CTAs & Button Redundancy
- **Problem:** When no file is loaded, the user is presented with two identical purple solid buttons in close proximity:
  - Sidebar bottom: `+ Open PDFs…` (solid primary `#646cff`)
  - Inline notice banner: `+ Open PDF…` (solid primary `#646cff`)
- **User Impact:** Violates visual hierarchy and Hick's Law by placing competing primary actions on screen.
- **Remediation:** Style the inline notice button as a secondary action (translucent surface with subtle border) or integrate an intuitive dropzone, preserving the solid primary accent for executing the current tool's core action.

### [P2] Low Contrast on Inactive Actions & Subtle Controls
- **Problem:** Disabled primary buttons use `#252529` text on `#202127` cards with dark text (`rgba(235, 235, 245, 0.38)`). The text contrast falls below WCAG AA thresholds. Furthermore, the top-right `?` Help button is barely visible.
- **User Impact:** Difficult to read inactive action labels. Faint help button is easily missed.
- **Remediation:** 
  - Elevate disabled button text contrast to `rgba(235, 235, 245, 0.60)` with a visible border `#2e2e32`.
  - Style the `#HelpBtn` with a defined border, subtle hover state, and clear tooltip icon.

### [P2] Empty State Utility & Visual Balance
- **Problem:** When no document is loaded, the preview pane is a vast, static empty card offering minimal guidance.
- **User Impact:** Underutilized screen space.
- **Remediation:** Transform empty states into active drag-and-drop targets with clear visual cues and keyboard shortcut hints.

---

## 3. Persona Impact Analysis

- **Alex (Power User):** Frustrated by being forced to switch to "Home" to load or reorder documents before merging. Wants fast drag-and-drop into the Merge tool, quick keyboard reordering, and instantaneous execution.
- **Jordan (First-Timer):** Confused by messages referring to "Home Library" while trying to use "Merge". Needs direct, obvious inline controls: "Add PDFs here", "Reorder files", "Merge now".
- **Sam (Accessibility):** Struggles with low-contrast disabled buttons and clipped text labels. Benefits immediately from full word-wrapping and WCAG AA contrast enhancements.

---

## 4. Implementation Plan

1. **`src/ui/theme.py`:**
   - Boost disabled button contrast (`QPushButton#Primary:disabled`, text color to `rgba(235, 235, 245, 0.60)`).
   - Enhance `#HelpBtn` styling (visible border, hover background, clean circular/square pill).
   - Add styling for the inline Merge file queue (`QListWidget#MergeQueue`) with drag handles and action buttons.
   - Refine `#NoFileBanner` and its secondary action button styling.

2. **`src/ui/widgets/tool_panels.py`:**
   - Redesign `_create_merge_panel()` to include an interactive **Merge File List**:
     - Live document count.
     - Reorderable list of files showing filename, page count, and file size.
     - Move Up (`▲`), Move Down (`▼`), and Remove (`✕`) buttons.
     - Direct "Add PDFs…" button and drag-and-drop support.
   - Ensure hints and banners have proper `wordWrap` and flexible layout sizing to eliminate truncation.

3. **`src/ui/main_window.py`:**
   - Streamline tool view header: remove redundant in-card title/description (`tool_header_title` & `tool_header_desc`).
   - Wire the Merge tool's file queue directly with the window's document list (`self.files`) so additions, removals, and reordering are bidirectionally synchronized.
   - Rebalance splitter sizes (`[540, 660]`) and optimize empty preview states.
   - Restyle the inline banner button to secondary/ghost styling.

4. **Testing & Verification:**
   - Run UI checks, wiring checks, and end-to-end operation tests to verify all functionality is intact.
