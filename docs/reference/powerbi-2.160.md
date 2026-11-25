# Power BI Desktop 2.160.1151.0 assessment

## Exact installer and recipe

On November 24, 2026, the configured Microsoft download served **2.160.1151.0**
(720,229,728 bytes; HTTP Last-Modified November 23). Its SHA-256 is:

```text
89ace9881d43a350e205c93da9681a8211a521b2ccd63211e1baf6020efdcb85
```

The source CLI registers this exact installer and selects it for fresh setup.
It retains 2.159.1231.0, 2.159.883.0 and 2.158.1177.0 for exact local installers
and maintenance of existing profiles. Older published CLI releases still reject
the new download. Setup does not upgrade an already active Desktop installation;
`update` updates the compatibility runtime, not Desktop.

The [machine-readable assessment](powerbi-2.160-assessment.json) records original,
intermediate and patched hashes. No Microsoft installer or assembly is committed.

## What was reused

The existing corrections retain their behavior:

- All five legacy HTML resources are byte-identical to the verified 2.158/2.159
  resources. Their common file-offset shift from 2.158 is **−704 bytes**. Every
  original and transformed resource hash is checked before the final DLL hash.
- The email dialog resource is unchanged. The existing serializer patch applies
  with the new exact Desktop assembly hash.
- `WebView2Resources/minerva/reportView.html` is unchanged. The existing text
  picker and title-tooltip patches apply without new patterns.
- The native `StartResize` and relocated `CreateParams` getter keep the same
  resolved instructions as the existing patched 2.158 methods. Twelve metadata
  tokens, method locations and the getter's MethodDef RVA entry were ported to
  2.160; this was checked by reading the patched DLL back with dnlib.
- Analysis Services has a new file hash and call-site location. Import-table
  inspection identified exactly one `GetCurrentThread` →
  `ImpersonateAnonymousToken` call pair. The existing local impersonation
  correction was ported to that site with exact input, instruction, import-name
  and complete output hashes.

All four application-file identities are checked as one complete recipe before
application files are replaced. Mixed-build unit cases cover every ordered pair
of the four supported recipes. Unknown installer/assembly hashes remain rejected.

## Additional WinRT compatibility

Desktop 2.160 resolves optional Lyra/MSIX dependencies during startup before
checking feature eligibility. The previous shim lacked
`Windows.Management.Deployment.PackageManager`, causing a `TypeLoadException`
that cleanup masked with a subsequent startup crash. The shim now supplies the
referenced package and asynchronous type shapes. Package queries return an empty
catalog; package removal and packaged-app launch explicitly throw
`PlatformNotSupportedException`. Native API availability remains false.

The CLI stages its reviewed `WinRTStubs.cs` over the runtime archive copy before
compilation, allowing an older runtime to use the new Desktop recipe. A regression
test checks that source selection, and a compiled probe checks the shim behavior.

## Validation

The offline recipe runner passed on unmodified files extracted from this exact
installer:

```bash
python3 tools/test-powerbi-recipe.py /path/to/unmodified/bin --version 2.160.1151.0 --output /path/to/new-evidence.json
```

The real-assembly patcher chain also passed in the pinned builder under Mono:
`PatchShared`, `PatchWinRT`, `PatchStoreRating`, `PatchCacheCompatibility`,
`PatchWindowFrame` and `PatchSavePrompt`. Existing method/signature guards were
retained. Signed helper checks passed, and temporary private signing keys were
removed. This reads and rewrites local assemblies; it does not prove Desktop
launch, visual rendering or model refresh.

A fresh native installation completed on Fedora 44 with published runtime
0.1.6-beta.1, isolated XDG directories and a separate Weston headless compositor.
Doctor passed all 20 checks. The startup shim correction was then applied through
repair using the actual prefix .NET compiler.

With the locally built integration runtime, a synthetic PBIP opened, refreshed
through the native toolbar and saved its model cache. Independent Analysis
Services queries verified 1,000 fact rows, total 300 and relationship filtering.
The captured native application frame was visually inspected: the report table,
ribbon and editor panels rendered, including the expected total. This is a
bounded synthetic check, not certification of every UI feature. Runtime hashes
are recorded in the assessment JSON. A separate session on the published default
runtime reopened the saved project without refreshing and independently verified
the same rows, total and relationship filter. Its native frame was also reviewed. A further refresh and save session passed on
that published runtime too, with the same independent data checks and native
frame review. No Wine rebuild is required for this Desktop port.

## Scope

A Desktop recipe change does not itself require recompiling Wine. The CLI owns
the exact application recipes independently of the runtime's default Desktop
version; its WebView2 recipe must still match the runtime. This port retains the
fixed WebView2 154.0.4258.62 and .NET prerequisites.

Offline patch success and isolated headless tests do not certify Fedora/GNOME
physical input, every report or connector, sign-in, publishing, a large refresh
or a prolonged session. Those remain separate release obligations.
