# Legacy HTML dialogs

Some Desktop dialogs still use Wine MSHTML/Gecko, including database
credentials. A refresh can wait for one of these dialogs while its progress
animation and Cancel button appear frozen. A responsive main thread or CPU
activity alone does not establish that data loading is advancing.

The Fedora reproduction on October 14 had a 2 × 2 credential window disabling
both the report and the refresh dialog. A read-only managed stack identified
`CredentialsChallengeResolver.ShowResolveDialog`. Cancelling that request
revealed the original refresh errors asking for MySQL credentials.

## Corrections

Setup/repair registers Wine's own `mshtml.dll` in both architectures after the
installers. The affected prefix had HTML COM class entries but lacked the
`about:` and `res:` protocol handlers and the `text/html` MIME handler. Installing
Gecko alone did not restore these entries. Doctor now checks the persisted
registrations and the activated UI patch version without starting Wine or
opening a browser. Upgrading only the RPM leaves this check pending until
`pbi-linux repair` applies the recipe to the existing installation.

The original credential correction in `Microsoft.Mashup.Client.UI.dll` makes two changes
to embedded JavaScript resources:

- In `ts/jquery.extensions.js`, an `E_NOTIMPL` from the DOM `textOverflow`
  setter enables a jQuery hook using `style.setProperty`. Other errors propagate.
  The credential title's SmartTip otherwise interrupts dialog initialization.
- In `ts/floatingdialog/floatingdialog.js`, a deferred pass clears the credential
  sidebar's stale inline height and repeats the existing layout calculation
  after `showDialog` assigns the final width. Error display can calculate that
  height before the final width is assigned, leaving the credential fields above
  the visible area even after HTML initializes. The pass runs only for a
  credential challenge; other legacy dialogs keep their existing sizing.

The recipe checks the exact original assembly and final output hashes, preserves
PE/resource sizes and IL, and retains the original backup. It does not replace
the credential backend, select an authentication method, supply a password,
change source permissions or approve native queries. The existing localized
HTML controls, credential scope choices and cancellation callbacks remain in use.

Updating an RPM changes the CLI recipe; it does not rewrite an existing profile
or reload assemblies in a running Desktop. Close Desktop before setup/repair.
An older CLI repair recipe does not include these corrections. Save pending work
before restarting a session that already loaded the old assembly.

## Component test

```bash
python3 tools/test-legacy-html.py
```

This opens only its own offline test window and checks rendered HTML,
JavaScript evaluation and a callback to .NET. It does not patch the installation
or interact with Desktop. It is a component test, not certification of every
Desktop HTML dialog or database connector.

See [native close confirmation](native-dialogs.md) and
[refresh cancellation](refresh-cancellation.md) for the separate close/save and
engine cancellation paths. A cancelled credential request does not establish
that cancelling an already-running database query succeeds for every connector.

## Credential dialog validation

On Fedora 44 Wayland, a fresh Desktop process opened a disposable two-table
PBIP whose MySQL source used the closed loopback address `127.0.0.1:65534`.
The first credential window measured 702 × 381, with 700 × 379 HTML content;
fields and Cancel were inside the viewport without a diagnostic sizing script.
Native mouse messages switched to the Database tab and then clicked Cancel.
The credential window disappeared within the first observation at 0.129 seconds.
After dismissing the refresh result, the main native window was enabled again.
No credential values were entered or submitted.

The diagnostic Desktop copy used a private inspection helper and test-only
cgroup limits of 10 GiB RAM / 2 GiB swap. The RAM ceiling was reached, with zero
OOM events or kills. Product defaults were unchanged, and the test process and
its browser policy were removed afterward. These checks cover first-show
layout, tab interaction and credential cancellation; they do not certify MySQL
authentication, network refresh completion or every connector.

## Data source list — RPM 7

The source-settings dialog uses a separate virtualized list. A CSV-only fixture
proved that native discovery returned one source while the HTML had zero rows:
its cached viewport and page size were both zero even after the visible container
reached 300 pixels in height. Calling the widget's original resize changed page
size to 10 and rendered the source. A fresh process with the guarded resource
patch did the same without manually invoking a resize. MySQL source rows also
appeared after the successful synthetic database refresh.

The recipe now includes a third resource, `komanagedatasourcesdialog.js`: after
showing the dialog it requests the widget's own resize if its cached page size
is zero. PE/resource sizes and IL remain unchanged. Doctor verifies the complete
updated UI assembly. No source is synthesized, and discovery, queries and
permissions remain under Desktop's original handlers. See [connectors](../user/connectors.md)
for the independent MySQL dependency and full validation scope.

Visible sources were also confirmed in the real report. A missing
cursor and unresponsive clicks initially recovered after an estimated 10–60 seconds. This observation
does not establish a cause or certify physical input latency; the resize patch
only corrects list geometry.

## Edit Permissions — RPM 8

The original getViewModel fallback traversed native host/button objects while
serializing the form, causing TargetParameterCountException after OK. The new
size-preserving resource patch supplies getJSON for its 13 original wire fields.
It preserves privacy, credential type and encryption; original handlers perform
persistence and cancellation. This is separate from runtime 0.1.1's Wayland
modal/popup correction. The synthetic compositor-input cycle passed with both.
The nested None/Delete Permissions confirmation is still limited;
see [scope](permissions-wayland.md).

## Options initialization and scrolling — runtime 0.1.2 / RPM 9

The Options dialog exposed a separate .NET Int64-to-JavaScript conversion failure
in Wine, followed by a pane-height error. The runtime and guarded local UI recipe
fix these two stages; seven numeric cases and the 22-tab synthetic navigation/
geometry audit passed. See [Options](options-dialog.md) for evidence, installation
and remaining limits. This does not certify other untested nested HTML dialogs.

## Dialogs two pixels wide on Hyprland: 2026-11-18

Observed on the two-monitor Hyprland host described in [Hyprland](hyprland.md),
with Desktop 2.159.1231.0. The unexpected error report ("Something went wrong")
and Data source settings opened as a 2 x 2 pixel window with no visible content
while the main window stayed disabled. To the user this is a frozen Desktop
with nothing to dismiss. Posting `WM_CLOSE` to the dialog restored Desktop.

### Diagnosis

These dialogs share one host (`Ux.FloatingDialog.FloatingDialog`): a borderless
owned WinForms form that starts at 2 x 2 pixels. The page measures its content
and calls the host (`ModalDialog._resizeHost` to `Js_OnResize`), which sets the
form size.

- Trace probes in the dialog script showed the page healthy: 4434 characters of
  content, measured at 460 x 242, and the host call made and returned.
- No `SetWindowPos` followed. A relay trace showed the host reading the monitor
  DPI and nothing else.
- The form carried `WS_MAXIMIZE`. Hyprland sets the maximized state on every
  toplevel when it is mapped, so that clients draw no decorations, and the
  Wayland driver mirrors that state into the window style. WinForms only
  records a new size while a form is maximized.

An earlier working diagnosis in this file blamed Internet Explorer's element
resize events, which Wine's HTML engine does not raise. Polling the size in the
dialog script instead changed nothing, which disproved it.

### Correction

`wine-11.18-wayland-fixed-dialog-maximized.patch` ignores the compositor's
maximized state for an owned window without a sizing frame, unless the window
is maximized itself. Such a window is announced with equal minimum and maximum
sizes and cannot have been maximized by the compositor. No Desktop file and no
dialog script changes.

### Evidence

`tests/e2e/dialog-size.py` opens a dialog in a diagnostics session and checks
its window. Local builds of this source tree, not published:

| Check | Without the patch | With the patch (SHA-256 `85894f9f8dc06c6153899df058edbf75b1be40e46a84cad073a701b78b6fe8d6`) |
|---|---|---|
| Unexpected error report | 2 x 2, maximized | 462 x 244, not maximized, in two runs |
| Data source settings | 2 x 2, maximized | 802 x 609, not maximized |
| Content and buttons | Nothing visible | Message and buttons drawn; Cancel and Close dismissed the dialogs and re-enabled the main window |
| Main window | Maximized style, tiled | Unchanged |
| `session.py --ui-refresh --save` | Passed on 2026-11-17 | Passed: total 300, fact rows, relationship filter, save |

Limits:

- One host. Other compositors do not report a floating dialog as maximized, so
  the patch should not act there; that was not tested.
- Only these two dialogs were opened. The navigator, credential prompts and the
  Power Query dialogs use the same host and were not exercised.
- A first version read the window style while holding the driver's window data
  lock and deadlocked Desktop during startup. The style is now read first.
- Data source settings showed scroll bars inside the dialog. Not examined.
- The error report was triggered by sending the report page's error message to
  the host with one argument missing. Desktop's own handling of that error is
  what the dialog reports.
