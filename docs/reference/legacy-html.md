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

## Scroll bars inside Data source settings: 2026-11-18

Found on a Hyprland host with Desktop 2.159.1231.0. Once the dialog had its
size, its body showed a vertical and a horizontal scroll bar although the
content is laid out for the
dialog's width, and the vertical bar covered part of the sort button.

### Diagnosis

Probes in the shared dialog script reported the layout three seconds after the
dialog was shown:

- The body is `#dialogContent` (`.o-group-body`), a flex item of the column
  `.modal-main`. The style sheet gives it `overflow-y: auto` and a maximum
  height of 590 pixels in a dialog that cannot be resized.
- The body was 800 x 453 with a client area of 783 x 436 and a scrollable
  extent of 800 x 441. The engine gave the flex item a content height of 436,
  five pixels less than the extent of its last row of buttons.
- Those five pixels call for the vertical bar. The bar narrows the client area
  to 783, two children have a fixed width of 800
  (`.o-group-dataSourceView`, `.o-group-bottomRowContainer`), and that calls
  for the horizontal bar.
- It is not stale state: hiding the body and showing it again, which rebuilds
  its box, changed nothing. Hiding only the horizontal axis left the vertical
  bar and a body of 436.

Whether Internet Explorer's engine computes the same five pixels differently
was not measured; no Windows installation was compared.

### Correction

The source list scrolls by itself (`.o-group-dataSourceEntries`, 300 pixels
high) and the dialog is sized to its content, so the body never needs to
scroll. One more guarded step in the UI recipe sets `overflow: hidden` on the
body before the dialog is shown. It takes 55 of the 110 bytes of padding the
source list step left in `komanagedatasourcesdialog.js`; PE and resource sizes
and IL stay unchanged.

The step is applied to **2.159.1231.0 only**. The recipe verifies the hash of
the complete assembly, and the other supported builds were not available to
compute one. They keep the output of the Options step. `pbi-linux doctor`
reports the installed assembly as outdated until `pbi-linux repair` has run.

### Evidence

| Check | Before | With the step |
|---|---|---|
| Body client area | 783 x 436, both bars | No bars |
| Dialog window | 802 x 587 | 802 x 592 |
| Sort button | Partly covered | Whole |
| Recipe output | `3b0639cf...` | `426f5e88...`, same length, only the source list resource differs |

Screenshots of both views of the dialog (Global permissions and Data sources
in current file, with four and five buttons in the bottom row) were reviewed:
no bars, the sort button and every button whole. The dialog's own Close button
closed it and re-enabled the main window. The fixture has no external source,
so the list showed its empty text in both views.

Limits:

- One host. The step does not depend on the compositor, but only this one was
  used.
- The warning row for unknown data sources was not shown in the test. With
  the body no longer scrolling, content taller than 590 pixels would be cut
  off instead; nothing in this dialog comes near that height.
- Other dialogs with the same body rule were not examined for the same five
  pixels.
