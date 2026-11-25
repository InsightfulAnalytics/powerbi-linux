# Experimental DEB: Debian and Ubuntu

> [!WARNING]
> **Experimental, not certified support.** The DEB enables Ubuntu 24.04/26.04 and
> Debian 13 on x86_64 with native Wayland, a systemd user session and an appropriate
> Vulkan driver. Fedora 44 remains the tested baseline. Other versions and derived
> distributions are not automatically accepted. Back up projects and start with
> copies. Microsoft does not support this community installation.

## Install

The published **0.1.0-20 beta** supports Ubuntu 24.04/26.04 and Debian 13
experimentally. Download these two files into the same directory:

- [powerbi-linux_0.1.0-20.experimental1_amd64.deb](https://github.com/cavallaro88/powerbi-linux/releases/download/v0.1.0-20/powerbi-linux_0.1.0-20.experimental1_amd64.deb)
- [SHA256SUMS](https://github.com/cavallaro88/powerbi-linux/releases/download/v0.1.0-20/SHA256SUMS)

The [release page](https://github.com/cavallaro88/powerbi-linux/releases/tag/v0.1.0-20)
also provides corresponding project sources and provenance. The downloaded DEB
filename uses `.experimental1`; its internal package version is
`0.1.0-20~experimental1`.

From the download directory, verify the files before installing:

```bash
sha256sum --check --ignore-missing SHA256SUMS
sudo apt update
sudo apt install ./powerbi-linux_0.1.0-20.experimental1_amd64.deb
pbi-linux setup
```

The checksum check must report `OK` for the DEB. `--ignore-missing` skips the
other release assets listed in SHA256SUMS that you did not download.

Automatic setup is available in this release. It selects **Power BI Desktop
2.160.1151.0**, runtime **0.1.7-pr-integration.1**, WebView2 and .NET; you do not
need to build or select those components yourself.

APT resolves Linux dependencies; setup separately downloads and verifies the
pinned runtime, Power BI, .NET and WebView2 after terms acceptance. Installing the
DEB does not run Wine or download/install Microsoft software. Do not install a
system Wine package as a substitute for the project's managed runtime.

Allow approximately 9 GiB for Desktop plus components, downloads and working
files. Setup may take several minutes without new terminal output. The existing
[installation guide](install.md) describes setup, exact-version checks and recovery.

After setup, open **Power BI Desktop (Wine)** from the application menu, or:

```bash
pbi-linux open
pbi-linux open '/path/to/report.pbix'
pbi-linux doctor
```

The ordinary packaged launcher handles the installation: no QA wrapper or source
checkout is required. The doctor labels the distribution experimental; a passing
diagnostic does not certify every report, connector or desktop environment.
Default file associations remain opt-in (`pbi-linux setup --make-default`).

## User-controlled resource policy

The DEB does not choose a resource preset or change RAM, swap, CPU, browser heap
or renderer settings. The project's existing defaults are unchanged, and package
installation, upgrade and removal do not edit per-user settings. Users can choose
optional settings later through the existing [resource commands](resources.md).
No setting from the development VM is copied into the package.

## Update and remove

Repair and runtime update work **in place**, without copying the complete prefix
or retaining a rollback snapshot. Back up important files yourself: interruption
or failure can require repair or reinstallation. Old profile directories are
not automatically deleted. See the [maintenance policy](updates.md).

For an existing installation, close Power BI, download and verify the release
files as above, then update the tools and managed runtime:

```bash
sudo apt install ./powerbi-linux_0.1.0-20.experimental1_amd64.deb
pbi-linux update
pbi-linux doctor
```

Updating the DEB changes the project tools; `pbi-linux update` changes the managed
runtime. Both preserve the installed Desktop version. `pbi-linux setup` creates a
fresh installation and does not upgrade an existing Desktop installation. See
[updates](updates.md).

```bash
sudo apt remove powerbi-linux
# Or remove the package and its system package configuration:
sudo apt purge powerbi-linux
```

Neither command deletes per-user prefixes, settings, credentials, caches or
reports. User-created menu entries from setup may remain; before removing the
package, `pbi-linux uninstall` removes that user integration while preserving
managed data. The separate `pbi-linux uninstall --purge` is destructive and is
not run by package hooks.
