// SPDX-License-Identifier: GPL-3.0-or-later
using System;
using System.Linq;
using Windows.Foundation.Metadata;
using Windows.Management.Deployment;
using Windows.System;

class WinRTStubsProbe
{
    static void Require(bool value, string message)
    {
        if (!value) throw new InvalidOperationException(message);
    }

    static void Unsupported(Action operation)
    {
        try { operation(); }
        catch (PlatformNotSupportedException) { return; }
        throw new InvalidOperationException("Unsupported package operation reported success");
    }

    static int Main()
    {
        var packages = new PackageManager();
        Require(!ApiInformation.IsTypePresent("Windows.Management.Deployment.PackageManager"), "Native package support advertised");
        Require(!ApiInformation.IsMethodPresent("Windows.System.Launcher", "LaunchUriAsync"), "Native launcher support advertised");
        Require(!packages.FindPackagesForUser("", "Microsoft.PowerBI.Lyra", "CN=Microsoft Corporation").Any(), "Synthetic installed package returned");
        var options = new LauncherOptions();
        options.put_TargetApplicationPackageFamilyName("missing-test-package");
        Require(options.TargetApplicationPackageFamilyName == "missing-test-package", "WinMD setter was not resolved");
        Unsupported(delegate { packages.RemovePackageAsync("missing-test-package"); });
        Unsupported(delegate { Launcher.LaunchUriAsync(new Uri("test-no-launch://local"), options); });
        Console.WriteLine("PASS: package catalog empty; native availability false; unsupported actions rejected");
        return 0;
    }
}
