// SPDX-License-Identifier: GPL-3.0-or-later
using System;
using System.Collections.Generic;
using Windows.Foundation;

[assembly: System.Reflection.AssemblyVersion("1.0.0.0")]

namespace Windows.Foundation
{
    public enum AsyncStatus { Started = 0, Completed = 1, Canceled = 2, Error = 3 }

    public interface IAsyncInfo
    {
        AsyncStatus Status { get; }
        void Cancel();
    }

    public interface IAsyncOperation<T> : IAsyncInfo
    {
    }

    public interface IAsyncOperationWithProgress<TResult, TProgress> : IAsyncInfo
    {
    }
}

// Desktop 2.160 resolves these optional Lyra/MSIX dependencies during startup,
// before its feature-eligibility check. This runtime has no Windows package
// catalog: a query finds no packages, and mutations remain explicitly unsupported.
namespace Windows.Management.Deployment
{
    public sealed class PackageManager
    {
        public IEnumerable<Windows.ApplicationModel.Package> FindPackagesForUser(
            string userSecurityId, string packageName, string packagePublisher)
        {
            if (packageName == null) throw new ArgumentNullException("packageName");
            if (packagePublisher == null) throw new ArgumentNullException("packagePublisher");
            return new Windows.ApplicationModel.Package[0];
        }

        public IAsyncOperationWithProgress<DeploymentResult, DeploymentProgress> RemovePackageAsync(string packageFullName)
        {
            throw new PlatformNotSupportedException("Windows package deployment is unavailable in this runtime.");
        }
    }

    public enum DeploymentStage { Queued = 0, Processing = 1 }

    public struct DeploymentProgress
    {
        public DeploymentStage state;
        public uint percentage;
    }

    public sealed class DeploymentResult
    {
        private DeploymentResult() { }
        public Guid ActivityId { get { throw new PlatformNotSupportedException(); } }
        public Exception ExtendedErrorCode { get { throw new PlatformNotSupportedException(); } }
    }
}

namespace Windows.ApplicationModel
{
    public sealed class Package
    {
        private Package() { }
        public bool IsFramework { get { throw new PlatformNotSupportedException(); } }
        public bool IsResourcePackage { get { throw new PlatformNotSupportedException(); } }
        public PackageId Id { get { throw new PlatformNotSupportedException(); } }
    }

    public sealed class PackageId
    {
        private PackageId() { }
        public string FullName { get { throw new PlatformNotSupportedException(); } }
        public string FamilyName { get { throw new PlatformNotSupportedException(); } }
        public PackageVersion Version { get { throw new PlatformNotSupportedException(); } }
    }

    public struct PackageVersion
    {
        public ushort Major, Minor, Build, Revision;
    }
}

namespace Windows.Foundation.Metadata
{
    public static class ApiInformation
    {
        public static bool IsTypePresent(string typeName)
        {
            return false;
        }

        public static bool IsMethodPresent(string typeName, string methodName)
        {
            return false;
        }
    }
}

namespace Windows.Storage
{
    public sealed class StorageFile
    {
        public static IAsyncOperation<StorageFile> GetFileFromPathAsync(string path)
        {
            return null;
        }

        public Windows.Storage.FileProperties.StorageItemContentProperties Properties
        {
            get { return null; }
        }
    }
}

namespace Windows.Storage.FileProperties
{
    public sealed class StorageItemContentProperties
    {
        public IAsyncOperation<IDictionary<string, object>> RetrievePropertiesAsync(IEnumerable<string> propertiesToRetrieve)
        {
            return null;
        }
    }
}

namespace Windows.System
{
    public sealed class LauncherOptions
    {
        public string TargetApplicationPackageFamilyName { get; private set; }

        // Preserve the WinMD setter name used by the original Desktop assembly.
        public void put_TargetApplicationPackageFamilyName(string value)
        {
            TargetApplicationPackageFamilyName = value;
        }
    }

    public static class Launcher
    {
        public static IAsyncOperation<bool> LaunchUriAsync(Uri uri, LauncherOptions options)
        {
            throw new PlatformNotSupportedException("Windows packaged-app launch is unavailable in this runtime.");
        }

        public static IAsyncOperation<bool> LaunchUriAsync(Uri uri)
        {
            return null;
        }
    }
}
