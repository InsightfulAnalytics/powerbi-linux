# Report blank behind a modal dialog: 2026-11-22

Observed with Options on Hyprland (Omarchy, Arch Linux), on a physical monitor
and on a headless output, with Desktop 2.159.1231.0: while Options was open,
the main window showed only its empty background (WinForms `WhiteSmoke`, RGB
245, 245, 245) instead of the report. The report came back when Options closed.
Export template looked unaffected.

## Diagnosis

- WebView2 draws in the browser process; the runtime's frame receiver in
  Desktop's process (`pbi_transport.c`, part of the Wine composition patch)
  copies each frame into its host window. It copies a frame only while the
  host is exposed, which it tests with `WindowFromPoint` at nine points of the
  host.
- `WindowFromPoint` stops at a disabled window and never looks at its
  children. Desktop disables its main window while any modal dialog is open,
  so every point resolved to the main window itself, the hosts counted as
  covered, and no frame was delivered. A probe in the running session read the
  main window at seven points and the Options page at the other two; with
  Options closed, all nine resolved to the report's browser window.
- What was on screen therefore depended on whether anything repainted the main
  window while the dialog was open. Export template left the last frame in
  place; opening Options repainted the main window, leaving the empty
  background. Page visibility stayed `visible` throughout, so the browser was
  not throttled.
- Nothing here is specific to Hyprland: any compositor shows the same gap
  whenever a modal dialog causes the main window to repaint.

## Correction

The receiver now descends from the window `WindowFromPoint` returns to the
deepest visible child at the point (`ChildWindowFromPointEx` with
`CWP_SKIPINVISIBLE`), as `WindowFromPoint` itself does for an enabled window,
before it looks for the host. `CWP_SKIPTRANSPARENT` is not used because the
browser hosts are `WS_EX_TRANSPARENT`. A point under a dialog still counts as
covered, and hidden sibling hosts are still never painted. The change is in
`runtime/ports/pbi_transport.c` and the copy of that file in
`wine-11.18-composition.patch`; it needs a rebuilt runtime.

## Evidence

`python3 tools/test-modal-frames.py --runtime /path/to/runtime` compiles
`tests/e2e/modal-frames-probe.c`, creates its own Wine-only prefix and a small
disposable window with a browser-like host, runs the runtime's frame receiver,
and checks that a published frame reaches the host with the main window
enabled, disabled, and disabled under an owned dialog. It opens no Desktop and
removes its prefix.

| Check | Without the correction | With the correction |
|---|---|---|
| `tools/test-modal-frames.py` | 1 passed, 2 failed on published 0.1.7-pr-integration.1 (SHA-256 `0128b0f2...e482`): the host kept the previous frame while its main window was disabled | 3 passed on a runtime built from this source tree (local label 0.1.7-hyprland-fixes.1, SHA-256 `7712ab97...e941`) |
| Options from the Settings button, Hyprland headless output, Desktop 2.159.1231.0, local runtimes | Main window empty | Report, ribbon and panes shown behind Options |
| Export template, same session | Last frame kept | Report shown |
| A page change made while Export template is open | Not tried | Reached the screen |

The Desktop rows used local runtimes built from a fork of this tree; they show
the effect on one host and do not certify any published archive.
