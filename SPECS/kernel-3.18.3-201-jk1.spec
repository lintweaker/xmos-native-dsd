# We have to override the new %%install behavior because, well... the kernel is special.
%global __spec_install_pre %{___build_pre}

Summary: The Linux kernel

# For a stable, released kernel, released_kernel should be 1. For rawhide
# and/or a kernel built from an rc or git snapshot, released_kernel should
# be 0.
%global released_kernel 1

%global aarch64patches 1

# Sign modules on x86.  Make sure the config files match this setting if more
# architectures are added.
%ifarch %{ix86} x86_64
%global signmodules 1
%global zipmodules 1
%else
%global signmodules 0
%global zipmodules 0
%endif

%if %{zipmodules}
%global zipsed -e 's/\.ko$/\.ko.xz/'
%endif

%define buildid .jk1

# baserelease defines which build revision of this kernel version we're
# building.  We used to call this fedora_build, but the magical name
# baserelease is matched by the rpmdev-bumpspec tool, which you should use.
#
# We used to have some extra magic weirdness to bump this automatically,
# but now we don't.  Just use: rpmdev-bumpspec -c 'comment for changelog'
# When changing base_sublevel below or going from rc to a final kernel,
# reset this by hand to 1 (or to 0 and then use rpmdev-bumpspec).
# scripts/rebase.sh should be made to do that for you, actually.
#
# NOTE: baserelease must be > 0 or bad things will happen if you switch
#       to a released kernel (released version will be < rc version)
#
# For non-released -rc kernels, this will be appended after the rcX and
# gitX tags, so a 3 here would become part of release "0.rcX.gitX.3"
#
%global baserelease 201
%global fedora_build %{baserelease}

# base_sublevel is the kernel version we're starting with and patching
# on top of -- for example, 3.1-rc7-git1 starts with a 3.0 base,
# which yields a base_sublevel of 0.
%define base_sublevel 18

## If this is a released kernel ##
%if 0%{?released_kernel}

# Do we have a -stable update to apply?
%define stable_update 3
# Set rpm version accordingly
%if 0%{?stable_update}
%define stablerev %{stable_update}
%define stable_base %{stable_update}
%endif
%define rpmversion 3.%{base_sublevel}.%{stable_update}

## The not-released-kernel case ##
%else
# The next upstream release sublevel (base_sublevel+1)
%define upstream_sublevel %(echo $((%{base_sublevel} + 1)))
# The rc snapshot level
%define rcrev 0
# The git snapshot level
%define gitrev 0
# Set rpm version accordingly
%define rpmversion 3.%{upstream_sublevel}.0
%endif
# Nb: The above rcrev and gitrev values automagically define Patch00 and Patch01 below.

# What parts do we want to build?  We must build at least one kernel.
# These are the kernels that are built IF the architecture allows it.
# All should default to 1 (enabled) and be flipped to 0 (disabled)
# by later arch-specific checks.

# The following build options are enabled by default.
# Use either --without <opt> in your rpmbuild command or force values
# to 0 in here to disable them.
#
# standard kernel
%define with_up        %{?_without_up:        0} %{?!_without_up:        1}
# kernel PAE (only valid for i686 (PAE) and ARM (lpae))
%define with_pae       %{?_without_pae:       0} %{?!_without_pae:       1}
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{?!_without_debug:     1}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
# perf
%define with_perf      %{?_without_perf:      0} %{?!_without_perf:      1}
# tools
%define with_tools     %{?_without_tools:     0} %{?!_without_tools:     1}
# kernel-debuginfo
%define with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 1}
# kernel-bootwrapper (for creating zImages from kernel + initrd)
%define with_bootwrapper %{?_without_bootwrapper: 0} %{?!_without_bootwrapper: 1}
# Want to build a the vsdo directories installed
%define with_vdso_install %{?_without_vdso_install: 0} %{?!_without_vdso_install: 1}
#
# Additional options for user-friendly one-off kernel building:
#
# Only build the base kernel (--with baseonly):
%define with_baseonly  %{?_with_baseonly:     1} %{?!_with_baseonly:     0}
# Only build the pae kernel (--with paeonly):
%define with_paeonly   %{?_with_paeonly:      1} %{?!_with_paeonly:      0}
# Only build the debug kernel (--with dbgonly):
%define with_dbgonly   %{?_with_dbgonly:      1} %{?!_with_dbgonly:      0}
#
# should we do C=1 builds with sparse
%define with_sparse    %{?_with_sparse:       1} %{?!_with_sparse:       0}
#
# Cross compile requested?
%define with_cross    %{?_with_cross:         1} %{?!_with_cross:        0}
#
# build a release kernel on rawhide
%define with_release   %{?_with_release:      1} %{?!_with_release:      0}

# Set debugbuildsenabled to 1 for production (build separate debug kernels)
#  and 0 for rawhide (all kernels are debug kernels).
# See also 'make debug' and 'make release'.
%define debugbuildsenabled 1

# Want to build a vanilla kernel build without any non-upstream patches?
%define with_vanilla %{?_with_vanilla: 1} %{?!_with_vanilla: 0}

# pkg_release is what we'll fill in for the rpm Release: field
%if 0%{?released_kernel}

%define pkg_release %{fedora_build}%{?buildid}%{?dist}

%else

# non-released_kernel
%if 0%{?rcrev}
%define rctag .rc%rcrev
%else
%define rctag .rc0
%endif
%if 0%{?gitrev}
%define gittag .git%gitrev
%else
%define gittag .git0
%endif
%define pkg_release 0%{?rctag}%{?gittag}.%{fedora_build}%{?buildid}%{?dist}

%endif

# The kernel tarball/base version
%define kversion 3.%{base_sublevel}

%define make_target bzImage

%define KVERREL %{version}-%{release}.%{_target_cpu}
%define hdrarch %_target_cpu
%define asmarch %_target_cpu

%if 0%{!?nopatches:1}
%define nopatches 0
%endif

%if %{with_vanilla}
%define nopatches 1
%endif

%if %{nopatches}
%define with_bootwrapper 0
%define variant -vanilla
%endif

%if !%{debugbuildsenabled}
%define with_debug 0
%endif

%if !%{with_debuginfo}
%define _enable_debug_packages 0
%endif
%define debuginfodir /usr/lib/debug

# kernel PAE is only built on i686 and ARMv7.
%ifnarch i686 armv7hl
%define with_pae 0
%endif

# if requested, only build base kernel
%if %{with_baseonly}
%define with_pae 0
%define with_debug 0
%endif

# if requested, only build pae kernel
%if %{with_paeonly}
%define with_up 0
%define with_debug 0
%endif

# if requested, only build debug kernel
%if %{with_dbgonly}
%if %{debugbuildsenabled}
%define with_up 0
%define with_pae 0
%endif
%define with_pae 0
%define with_tools 0
%define with_perf 0
%endif

%define all_x86 i386 i686

%if %{with_vdso_install}
# These arches install vdso/ directories.
%define vdso_arches %{all_x86} x86_64 %{power64} s390 s390x aarch64
%endif

# Overrides for generic default options

# don't do debug builds on anything but i686 and x86_64
%ifnarch i686 x86_64
%define with_debug 0
%endif

# don't build noarch kernels or headers (duh)
%ifarch noarch
%define with_up 0
%define with_headers 0
%define with_tools 0
%define with_perf 0
%define all_arch_configs kernel-%{version}-*.config
%endif

# bootwrapper is only on ppc
# sparse blows up on ppc
%ifnarch %{power64}
%define with_bootwrapper 0
%define with_sparse 0
%endif

# Per-arch tweaks

%ifarch %{all_x86}
%define asmarch x86
%define hdrarch i386
%define pae PAE
%define all_arch_configs kernel-%{version}-i?86*.config
%define image_install_path boot
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch x86_64
%define asmarch x86
%define all_arch_configs kernel-%{version}-x86_64*.config
%define image_install_path boot
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch %{power64}
%define asmarch powerpc
%define hdrarch powerpc
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%ifarch ppc64 ppc64p7
%define all_arch_configs kernel-%{version}-ppc64*.config
%endif
%ifarch ppc64le
%define all_arch_configs kernel-%{version}-ppc64le.config
%endif
%endif

%ifarch s390x
%define asmarch s390
%define hdrarch s390
%define all_arch_configs kernel-%{version}-s390x.config
%define image_install_path boot
%define make_target image
%define kernel_image arch/s390/boot/image
%define with_tools 0
%endif

%ifarch %{arm}
%define all_arch_configs kernel-%{version}-arm*.config
%define image_install_path boot
%define asmarch arm
%define hdrarch arm
%define pae lpae
%define make_target bzImage
%define kernel_image arch/arm/boot/zImage
# http://lists.infradead.org/pipermail/linux-arm-kernel/2012-March/091404.html
%define kernel_mflags KALLSYMS_EXTRA_PASS=1
# we only build headers/perf/tools on the base arm arches
# just like we used to only build them on i386 for x86
%ifnarch armv7hl
%define with_headers 0
%define with_perf 0
%define with_tools 0
%endif
%endif

%ifarch aarch64
%define all_arch_configs kernel-%{version}-aarch64*.config
%define asmarch arm64
%define hdrarch arm64
%define make_target Image.gz
%define kernel_image arch/arm64/boot/Image.gz
%define image_install_path boot
%endif

# Should make listnewconfig fail if there's config options
# printed out?
%if %{nopatches}
%define listnewconfig_fail 0
%else
%define listnewconfig_fail 1
%endif

# To temporarily exclude an architecture from being built, add it to
# %%nobuildarches. Do _NOT_ use the ExclusiveArch: line, because if we
# don't build kernel-headers then the new build system will no longer let
# us use the previous build of that package -- it'll just be completely AWOL.
# Which is a BadThing(tm).

# We only build kernel-headers on the following...
%if 0%{?aarch64patches}
%define nobuildarches i386 s390
%else
%define nobuildarches i386 s390 aarch64
%endif

%ifarch %nobuildarches
%define with_up 0
%define with_pae 0
%define with_debuginfo 0
%define with_perf 0
%define with_tools 0
%define _enable_debug_packages 0
%endif

%define with_pae_debug 0
%if %{with_pae}
%define with_pae_debug %{with_debug}
%endif

# Architectures we build tools/cpupower on
%define cpupowerarchs %{ix86} x86_64 %{power64} %{arm} aarch64 

#
# Packages that need to be installed before the kernel is, because the %%post
# scripts use them.
#
%define kernel_prereq  fileutils, systemd >= 203-2
%define initrd_prereq  dracut >= 038-29


Name: kernel%{?variant}
Group: System Environment/Kernel
License: GPLv2 and Redistributable, no modification permitted
URL: http://www.kernel.org/
Version: %{rpmversion}
Release: %{pkg_release}
# DO NOT CHANGE THE 'ExclusiveArch' LINE TO TEMPORARILY EXCLUDE AN ARCHITECTURE BUILD.
# SET %%nobuildarches (ABOVE) INSTEAD
ExclusiveArch: %{all_x86} x86_64 ppc64 ppc64p7 s390 s390x %{arm} aarch64 ppc64le
ExclusiveOS: Linux
%ifnarch %{nobuildarches}
Requires: kernel-%{?variant:%{variant}-}core-uname-r = %{KVERREL}%{?variant}
Requires: kernel-%{?variant:%{variant}-}modules-uname-r = %{KVERREL}%{?variant}
%endif


#
# List the packages used during the kernel build
#
BuildRequires: kmod, patch, bash, sh-utils, tar
BuildRequires: bzip2, xz, findutils, gzip, m4, perl, perl-Carp, make, diffutils, gawk
BuildRequires: gcc, binutils, redhat-rpm-config, hmaccalc
BuildRequires: net-tools, hostname, bc
%if %{with_sparse}
BuildRequires: sparse
%endif
%if %{with_perf}
BuildRequires: elfutils-devel zlib-devel binutils-devel newt-devel python-devel perl(ExtUtils::Embed) bison flex
BuildRequires: audit-libs-devel
%endif
%if %{with_tools}
BuildRequires: pciutils-devel gettext ncurses-devel
%endif
BuildConflicts: rhbuildsys(DiskFree) < 500Mb
%if %{with_debuginfo}
BuildRequires: rpm-build, elfutils
%define debuginfo_args --strict-build-id -r
%endif

%if %{signmodules}
BuildRequires: openssl
BuildRequires: pesign >= 0.10-4
%endif

%if %{with_cross}
BuildRequires: binutils-%{_build_arch}-linux-gnu, gcc-%{_build_arch}-linux-gnu
%define cross_opts CROSS_COMPILE=%{_build_arch}-linux-gnu-
%endif

Source0: ftp://ftp.kernel.org/pub/linux/kernel/v3.0/linux-%{kversion}.tar.xz

Source10: perf-man-%{kversion}.tar.gz
Source11: x509.genkey

Source15: merge.pl
Source16: mod-extra.list
Source17: mod-extra.sh
Source18: mod-sign.sh
Source90: filter-x86_64.sh
Source91: filter-armv7hl.sh
Source92: filter-i686.sh
Source93: filter-aarch64.sh
Source95: filter-ppc64.sh
Source96: filter-ppc64le.sh
Source97: filter-s390x.sh
Source98: filter-ppc64p7.sh
Source99: filter-modules.sh
%define modsign_cmd %{SOURCE18}

Source19: Makefile.release
Source20: Makefile.config
Source21: config-debug
Source22: config-nodebug
Source23: config-generic
Source24: config-no-extra

Source30: config-x86-generic
Source31: config-i686-PAE
Source32: config-x86-32-generic

Source40: config-x86_64-generic

Source50: config-powerpc-generic
Source53: config-powerpc64
Source54: config-powerpc64p7
Source55: config-powerpc64le

Source70: config-s390x

Source100: config-arm-generic

# Unified ARM kernels
Source101: config-armv7-generic
Source102: config-armv7
Source103: config-armv7-lpae

Source110: config-arm64

# This file is intentionally left empty in the stock kernel. Its a nicety
# added for those wanting to do custom rebuilds with altered config opts.
Source1000: config-local

# Sources for kernel-tools
Source2000: cpupower.service
Source2001: cpupower.config

# Here should be only the patches up to the upstream canonical Linus tree.

# For a stable release kernel
%if 0%{?stable_update}
%if 0%{?stable_base}
%define    stable_patch_00  patch-3.%{base_sublevel}.%{stable_base}.xz
Patch00: %{stable_patch_00}
%endif

# non-released_kernel case
# These are automagically defined by the rcrev and gitrev values set up
# near the top of this spec file.
%else
%if 0%{?rcrev}
Patch00: patch-3.%{upstream_sublevel}-rc%{rcrev}.xz
%if 0%{?gitrev}
Patch01: patch-3.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}.xz
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
Patch00: patch-3.%{base_sublevel}-git%{gitrev}.xz
%endif
%endif
%endif

# we also need compile fixes for -vanilla
Patch04: compile-fixes.patch

# build tweak for build ID magic, even for -vanilla
Patch05: kbuild-AFTER_LINK.patch

%if !%{nopatches}


# revert upstream patches we get via other methods
Patch09: upstream-reverts.patch
# Git trees.

# Standalone patches

Patch450: input-kill-stupid-messages.patch
Patch452: no-pcspkr-modalias.patch

Patch470: die-floppy-die.patch

Patch500: Revert-Revert-ACPI-video-change-acpi-video-brightnes.patch

Patch510: input-silence-i8042-noise.patch
Patch530: silence-fbcon-logo.patch

Patch600: lib-cpumask-Make-CPUMASK_OFFSTACK-usable-without-deb.patch

#rhbz 1126580
Patch601: Kbuild-Add-an-option-to-enable-GCC-VTA.patch

Patch800: crash-driver.patch

# crypto/

# secure boot
Patch1000: Add-secure_modules-call.patch
Patch1001: PCI-Lock-down-BAR-access-when-module-security-is-ena.patch
Patch1002: x86-Lock-down-IO-port-access-when-module-security-is.patch
Patch1003: ACPI-Limit-access-to-custom_method.patch
Patch1004: asus-wmi-Restrict-debugfs-interface-when-module-load.patch
Patch1005: Restrict-dev-mem-and-dev-kmem-when-module-loading-is.patch
Patch1006: acpi-Ignore-acpi_rsdp-kernel-parameter-when-module-l.patch
Patch1007: kexec-Disable-at-runtime-if-the-kernel-enforces-modu.patch
Patch1008: x86-Restrict-MSR-access-when-module-loading-is-restr.patch
Patch1009: Add-option-to-automatically-enforce-module-signature.patch
Patch1010: efi-Disable-secure-boot-if-shim-is-in-insecure-mode.patch
Patch1011: efi-Make-EFI_SECURE_BOOT_SIG_ENFORCE-depend-on-EFI.patch
Patch1012: efi-Add-EFI_SECURE_BOOT-bit.patch
Patch1013: hibernate-Disable-in-a-signed-modules-environment.patch

Patch1014: Add-EFI-signature-data-types.patch
Patch1015: Add-an-EFI-signature-blob-parser-and-key-loader.patch
Patch1016: KEYS-Add-a-system-blacklist-keyring.patch
Patch1017: MODSIGN-Import-certificates-from-UEFI-Secure-Boot.patch
Patch1018: MODSIGN-Support-not-importing-certs-from-db.patch

Patch1019: Add-sysrq-option-to-disable-secure-boot-mode.patch

# virt + ksm patches

# DRM

# nouveau + drm fixes
# intel drm is all merged upstream
Patch1826: drm-i915-hush-check-crtc-state.patch
Patch1827: drm-i915-Don-t-WARN-in-edp_panel_vdd_off.patch

# Quiet boot fixes

# fs fixes

# NFSv4

# patches headed upstream
Patch12016: disable-i8042-check-on-apple-mac.patch

Patch14000: hibernate-freeze-filesystems.patch

Patch14010: lis3-improve-handling-of-null-rate.patch

Patch15000: watchdog-Disable-watchdog-on-virtual-machines.patch

# PPC

# ARM64

# ARMv7
Patch21020: ARM-tegra-usb-no-reset.patch
Patch21021: arm-dts-am335x-boneblack-lcdc-add-panel-info.patch
Patch21022: arm-dts-am335x-boneblack-add-cpu0-opp-points.patch
Patch21023: arm-dts-am335x-bone-common-enable-and-use-i2c2.patch
Patch21024: arm-dts-am335x-bone-common-setup-default-pinmux-http.patch
Patch21025: arm-dts-am335x-bone-common-add-uart2_pins-uart4_pins.patch
Patch21026: pinctrl-pinctrl-single-must-be-initialized-early.patch

Patch21028: arm-i.MX6-Utilite-device-dtb.patch
Patch21029: arm-dts-sun7i-bananapi.patch

Patch21100: arm-highbank-l2-reverts.patch

#rhbz 754518
Patch21235: scsi-sd_revalidate_disk-prevent-NULL-ptr-deref.patch

# https://fedoraproject.org/wiki/Features/Checkpoint_Restore
Patch21242: criu-no-expert.patch

#rhbz 892811
Patch21247: ath9k-rx-dma-stop-check.patch

Patch22000: weird-root-dentry-name-debug.patch

# Patch series from Hans for various backlight and platform driver fixes
Patch26002: samsung-laptop-Add-broken-acpi-video-quirk-for-NC210.patch

#rhbz 1089731
Patch26058: asus-nb-wmi-Add-wapf4-quirk-for-the-X550VB.patch

#rhbz 1135338
Patch26090: HID-add-support-for-MS-Surface-Pro-3-Type-Cover.patch

#rhbz 1164945
Patch26092: xhci-Add-broken-streams-quirk-for-Fresco-Logic-FL100.patch
Patch26093: uas-Add-US_FL_NO_ATA_1X-for-Seagate-devices-with-usb.patch
Patch26094: uas-Add-US_FL_NO_REPORT_OPCODES-for-JMicron-JMS566-w.patch

#rhbz 1172543
Patch26096: cfg80211-don-t-WARN-about-two-consecutive-Country-IE.patch

#rhbz 1173806
Patch26101: powerpc-powernv-force-all-CPUs-to-be-bootable.patch

Patch26107: uapi-linux-target_core_user.h-fix-headers_install.sh.patch

#rhbz 1163927
Patch26121: Set-UID-in-sess_auth_rawntlmssp_authenticate-too.patch

#CVE-2014-9428 rhbz 1178826,1178833
Patch26122: batman-adv-Calculate-extra-tail-size-based-on-queued.patch

#CVE-2014-9529 rhbz 1179813 1179853
Patch26124: KEYS-close-race-between-key-lookup-and-freeing.patch

#rhbz 1124119
Patch26126: uas-Do-not-blacklist-ASM1153-disk-enclosures.patch
Patch26127: uas-Add-US_FL_NO_ATA_1X-for-2-more-Seagate-disk-encl.patch
Patch26128: uas-Add-no-report-opcodes-quirk-for-Simpletech-devic.patch

#rhbz 1115713
Patch26129: samsung-laptop-Add-use_native_backlight-quirk-and-en.patch
#rhbz 1163574
Patch26130: acpi-video-Add-disable_native_backlight-quirk-for-De.patch
#rhbz 1094948
Patch26131: acpi-video-Add-disable_native_backlight-quirk-for-Sa.patch

# git clone ssh://git.fedorahosted.org/git/kernel-arm64.git, git diff master...devel
Patch30000: kernel-arm64.patch

# Fix for big-endian arches, already upstream
Patch30001: mpssd-x86-only.patch

# Patches from 3.18.4 stable queue (should fix i915 issues)
Patch30002: stable-3.18.4-queue.patch
Patch30003: xhci-check-if-slot-is-already-in-default-state.patch

# JK DSD enhancements
Patch31004: alsa-usb-add-marantz-dsd-quirk-v2.patch
Patch31005: alsa-usb-marantz-select-mode-quirk-v6.patch
Patch31006: alsa-usb-add-matrix-audio-native-dsd-v2.patch


# END OF PATCH DEFINITIONS

%endif

BuildRoot: %{_tmppath}/kernel-%{KVERREL}-root

%description
The kernel meta package

#
# This macro does requires, provides, conflicts, obsoletes for a kernel package.
#	%%kernel_reqprovconf <subpackage>
# It uses any kernel_<subpackage>_conflicts and kernel_<subpackage>_obsoletes
# macros defined above.
#
%define kernel_reqprovconf \
Provides: kernel = %{rpmversion}-%{pkg_release}\
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{pkg_release}%{?1:+%{1}}\
Provides: kernel-drm-nouveau = 16\
Provides: kernel-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires(pre): %{kernel_prereq}\
Requires(pre): %{initrd_prereq}\
Requires(pre): linux-firmware >= 20130724-29.git31f6b30\
Requires(preun): systemd >= 200\
%{expand:%%{?kernel%{?1:_%{1}}_conflicts:Conflicts: %%{kernel%{?1:_%{1}}_conflicts}}}\
%{expand:%%{?kernel%{?1:_%{1}}_obsoletes:Obsoletes: %%{kernel%{?1:_%{1}}_obsoletes}}}\
%{expand:%%{?kernel%{?1:_%{1}}_provides:Provides: %%{kernel%{?1:_%{1}}_provides}}}\
# We can't let RPM do the dependencies automatic because it'll then pick up\
# a correct but undesirable perl dependency from the module headers which\
# isn't required for the kernel proper to function\
AutoReq: no\
AutoProv: yes\
%{nil}

%package headers
Summary: Header files for the Linux kernel for use by glibc
Group: Development/System
Obsoletes: glibc-kernheaders < 3.0-46
Provides: glibc-kernheaders = 3.0-46
%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package bootwrapper
Summary: Boot wrapper files for generating combined kernel + initrd images
Group: Development/System
Requires: gzip binutils
%description bootwrapper
Kernel-bootwrapper contains the wrapper code which makes bootable "zImage"
files combining both kernel and initial ramdisk.

%package debuginfo-common-%{_target_cpu}
Summary: Kernel source files used by %{name}-debuginfo packages
Group: Development/Debug
%description debuginfo-common-%{_target_cpu}
This package is required by %{name}-debuginfo subpackages.
It provides the kernel source files common to all builds.

%if %{with_perf}
%package -n perf
Summary: Performance monitoring for the Linux kernel
Group: Development/System
License: GPLv2
%description -n perf
This package contains the perf tool, which enables performance monitoring
of the Linux kernel.

%package -n perf-debuginfo
Summary: Debug information for package perf
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n perf-debuginfo
This package provides debug information for the perf package.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/perf(\.debug)?|.*%%{_libexecdir}/perf-core/.*|.*%%{_libdir}/traceevent/plugins/.*|XXX' -o perf-debuginfo.list}

%package -n python-perf
Summary: Python bindings for apps which will manipulate perf events
Group: Development/Libraries
%description -n python-perf
The python-perf package contains a module that permits applications
written in the Python programming language to use the interface
to manipulate perf events.

%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%package -n python-perf-debuginfo
Summary: Debug information for package perf python bindings
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n python-perf-debuginfo
This package provides debug information for the perf python bindings.

# the python_sitearch macro should already be defined from above
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{python_sitearch}/perf.so(\.debug)?|XXX' -o python-perf-debuginfo.list}


%endif # with_perf

%if %{with_tools}
%package -n kernel-tools
Summary: Assortment of tools for the Linux kernel
Group: Development/System
License: GPLv2
Provides:  cpupowerutils = 1:009-0.6.p1
Obsoletes: cpupowerutils < 1:009-0.6.p1
Provides:  cpufreq-utils = 1:009-0.6.p1
Provides:  cpufrequtils = 1:009-0.6.p1
Obsoletes: cpufreq-utils < 1:009-0.6.p1
Obsoletes: cpufrequtils < 1:009-0.6.p1
Obsoletes: cpuspeed < 1:1.5-16
Requires: kernel-tools-libs = %{version}-%{release}
%description -n kernel-tools
This package contains the tools/ directory from the kernel source
and the supporting documentation.

%package -n kernel-tools-libs
Summary: Libraries for the kernels-tools
Group: Development/System
License: GPLv2
%description -n kernel-tools-libs
This package contains the libraries built from the tools/ directory
from the kernel source.

%package -n kernel-tools-libs-devel
Summary: Assortment of tools for the Linux kernel
Group: Development/System
License: GPLv2
Requires: kernel-tools = %{version}-%{release}
Provides:  cpupowerutils-devel = 1:009-0.6.p1
Obsoletes: cpupowerutils-devel < 1:009-0.6.p1
Requires: kernel-tools-libs = %{version}-%{release}
Provides: kernel-tools-devel
%description -n kernel-tools-libs-devel
This package contains the development files for the tools/ directory from
the kernel source.

%package -n kernel-tools-debuginfo
Summary: Debug information for package kernel-tools
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n kernel-tools-debuginfo
This package provides debug information for package kernel-tools.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/centrino-decode(\.debug)?|.*%%{_bindir}/powernow-k8-decode(\.debug)?|.*%%{_bindir}/cpupower(\.debug)?|.*%%{_libdir}/libcpupower.*|.*%%{_bindir}/turbostat(\.debug)?|.*%%{_bindir}/x86_energy_perf_policy(\.debug)?|.*%%{_bindir}/tmon(\.debug)?|XXX' -o kernel-tools-debuginfo.list}

%endif # with_tools


#
# This macro creates a kernel-<subpackage>-debuginfo package.
#	%%kernel_debuginfo_package <subpackage>
#
%define kernel_debuginfo_package() \
%package %{?1:%{1}-}debuginfo\
Summary: Debug information for package %{name}%{?1:-%{1}}\
Group: Development/Debug\
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}\
Provides: %{name}%{?1:-%{1}}-debuginfo-%{_target_cpu} = %{version}-%{release}\
AutoReqProv: no\
%description -n %{name}%{?1:-%{1}}-debuginfo\
This package provides debug information for package %{name}%{?1:-%{1}}.\
This is required to use SystemTap with %{name}%{?1:-%{1}}-%{KVERREL}.\
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '/.*/%%{KVERREL}%{?1:[+]%{1}}/.*|/.*%%{KVERREL}%{?1:\+%{1}}(\.debug)?' -o debuginfo%{?1}.list}\
%{nil}

#
# This macro creates a kernel-<subpackage>-devel package.
#	%%kernel_devel_package <subpackage> <pretty-name>
#
%define kernel_devel_package() \
%package %{?1:%{1}-}devel\
Summary: Development package for building kernel modules to match the %{?2:%{2} }kernel\
Group: System Environment/Kernel\
Provides: kernel%{?1:-%{1}}-devel-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel-devel = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel-devel-uname-r = %{KVERREL}%{?1:+%{1}}\
AutoReqProv: no\
Requires(pre): /usr/bin/find\
Requires: perl\
%description -n kernel%{?variant}%{?1:-%{1}}-devel\
This package provides kernel headers and makefiles sufficient to build modules\
against the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-<subpackage>-modules-extra package.
#	%%kernel_modules_extra_package <subpackage> <pretty-name>
#
%define kernel_modules_extra_package() \
%package %{?1:%{1}-}modules-extra\
Summary: Extra kernel modules to match the %{?2:%{2} }kernel\
Group: System Environment/Kernel\
Provides: kernel%{?1:-%{1}}-modules-extra-%{_target_cpu} = %{version}-%{release}\
Provides: kernel%{?1:-%{1}}-modules-extra-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel%{?1:-%{1}}-modules-extra = %{version}-%{release}%{?1:+%{1}}\
Provides: installonlypkg(kernel-module)\
Provides: kernel%{?1:-%{1}}-modules-extra-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: kernel-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: kernel%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?1:+%{1}}\
AutoReq: no\
AutoProv: yes\
%description -n kernel%{?variant}%{?1:-%{1}}-modules-extra\
This package provides less commonly used kernel modules for the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-<subpackage>-modules package.
#	%%kernel_modules_package <subpackage> <pretty-name>
#
%define kernel_modules_package() \
%package %{?1:%{1}-}modules\
Summary: kernel modules to match the %{?2:%{2}-}core kernel\
Group: System Environment/Kernel\
Provides: kernel%{?1:-%{1}}-modules-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-modules-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel-modules = %{version}-%{release}%{?1:+%{1}}\
Provides: installonlypkg(kernel-module)\
Provides: kernel%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: kernel-uname-r = %{KVERREL}%{?1:+%{1}}\
AutoReq: no\
AutoProv: yes\
%description -n kernel%{?variant}%{?1:-%{1}}-modules\
This package provides commonly used kernel modules for the %{?2:%{2}-}core kernel package.\
%{nil}

#
# this macro creates a kernel-<subpackage> meta package.
#	%%kernel_meta_package <subpackage>
#
%define kernel_meta_package() \
%package %{1}\
summary: kernel meta-package for the %{1} kernel\
group: system environment/kernel\
Requires: kernel-%{1}-%{?variant:%{variant}-}core-uname-r = %{KVERREL}%{?variant}+%{1}\
Requires: kernel-%{1}-%{?variant:%{variant}-}modules-uname-r = %{KVERREL}%{?variant}+%{1}\
%description %{1}\
The meta-package for the %{1} kernel\
%{nil}

#
# This macro creates a kernel-<subpackage> and its -devel and -debuginfo too.
#	%%define variant_summary The Linux kernel compiled for <configuration>
#	%%kernel_variant_package [-n <pretty-name>] <subpackage>
#
%define kernel_variant_package(n:) \
%package %{?1:%{1}-}core\
Summary: %{variant_summary}\
Group: System Environment/Kernel\
Provides: kernel-%{?1:%{1}-}core-uname-r = %{KVERREL}%{?1:+%{1}}\
%{expand:%%kernel_reqprovconf}\
%if %{?1:1} %{!?1:0} \
%{expand:%%kernel_meta_package %{?1:%{1}}}\
%endif\
%{expand:%%kernel_devel_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_modules_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_modules_extra_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_debuginfo_package %{?1:%{1}}}\
%{nil}

# Now, each variant package.

%ifnarch armv7hl
%define variant_summary The Linux kernel compiled for PAE capable machines
%kernel_variant_package %{pae}
%description %{pae}-core
This package includes a version of the Linux kernel with support for up to
64GB of high memory. It requires a CPU with Physical Address Extensions (PAE).
The non-PAE kernel can only address up to 4GB of memory.
Install the kernel-PAE package if your machine has more than 4GB of memory.
%else
%define variant_summary The Linux kernel compiled for Cortex-A15
%kernel_variant_package %{pae}
%description %{pae}-core
This package includes a version of the Linux kernel with support for
Cortex-A15 devices with LPAE and HW virtualisation support
%endif


%define variant_summary The Linux kernel compiled with extra debugging enabled for PAE capable machines
%kernel_variant_package %{pae}debug
Obsoletes: kernel-PAE-debug
%description %{pae}debug-core
This package includes a version of the Linux kernel with support for up to
64GB of high memory. It requires a CPU with Physical Address Extensions (PAE).
The non-PAE kernel can only address up to 4GB of memory.
Install the kernel-PAE package if your machine has more than 4GB of memory.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.


%define variant_summary The Linux kernel compiled with extra debugging enabled
%kernel_variant_package debug
%description debug-core
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system:  memory allocation, process allocation, device
input and output, etc.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.

# And finally the main -core package

%define variant_summary The Linux kernel
%kernel_variant_package 
%description core
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system: memory allocation, process allocation, device
input and output, etc.


%prep
# do a few sanity-checks for --with *only builds
%if %{with_baseonly}
%if !%{with_up}%{with_pae}
echo "Cannot build --with baseonly, up build is disabled"
exit 1
%endif
%endif

%if "%{baserelease}" == "0"
echo "baserelease must be greater than zero"
exit 1
%endif

# more sanity checking; do it quietly
if [ "%{patches}" != "%%{patches}" ] ; then
  for patch in %{patches} ; do
    if [ ! -f $patch ] ; then
      echo "ERROR: Patch  ${patch##/*/}  listed in specfile but is missing"
      exit 1
    fi
  done
fi 2>/dev/null

patch_command='patch -p1 -F1 -s'
ApplyPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  if ! grep -E "^Patch[0-9]+: $patch\$" %{_specdir}/${RPM_PACKAGE_NAME%%%%%{?variant}}.spec ; then
    if [ "${patch:0:8}" != "patch-3." ] ; then
      echo "ERROR: Patch  $patch  not listed as a source patch in specfile"
      exit 1
    fi
  fi 2>/dev/null
  case "$patch" in
  *.bz2) bunzip2 < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *.gz)  gunzip  < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *.xz)  unxz    < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *) $patch_command ${1+"$@"} < "$RPM_SOURCE_DIR/$patch" ;;
  esac
}

# don't apply patch if it's empty
ApplyOptionalPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  local C=$(wc -l $RPM_SOURCE_DIR/$patch | awk '{print $1}')
  if [ "$C" -gt 9 ]; then
    ApplyPatch $patch ${1+"$@"}
  fi
}

# First we unpack the kernel tarball.
# If this isn't the first make prep, we use links to the existing clean tarball
# which speeds things up quite a bit.

# Update to latest upstream.
%if 0%{?released_kernel}
%define vanillaversion 3.%{base_sublevel}
# non-released_kernel case
%else
%if 0%{?rcrev}
%define vanillaversion 3.%{upstream_sublevel}-rc%{rcrev}
%if 0%{?gitrev}
%define vanillaversion 3.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
%define vanillaversion 3.%{base_sublevel}-git%{gitrev}
%else
%define vanillaversion 3.%{base_sublevel}
%endif
%endif
%endif

# %%{vanillaversion} : the full version name, e.g. 2.6.35-rc6-git3
# %%{kversion}       : the base version, e.g. 2.6.34

# Use kernel-%%{kversion}%%{?dist} as the top-level directory name
# so we can prep different trees within a single git directory.

# Build a list of the other top-level kernel tree directories.
# This will be used to hardlink identical vanilla subdirs.
sharedirs=$(find "$PWD" -maxdepth 1 -type d -name 'kernel-3.*' \
            | grep -x -v "$PWD"/kernel-%{kversion}%{?dist}) ||:

# Delete all old stale trees.
if [ -d kernel-%{kversion}%{?dist} ]; then
  cd kernel-%{kversion}%{?dist}
  for i in linux-*
  do
     if [ -d $i ]; then
       # Just in case we ctrl-c'd a prep already
       rm -rf deleteme.%{_target_cpu}
       # Move away the stale away, and delete in background.
       mv $i deleteme-$i
       rm -rf deleteme* &
     fi
  done
  cd ..
fi

# Generate new tree
if [ ! -d kernel-%{kversion}%{?dist}/vanilla-%{vanillaversion} ]; then

  if [ -d kernel-%{kversion}%{?dist}/vanilla-%{kversion} ]; then

    # The base vanilla version already exists.
    cd kernel-%{kversion}%{?dist}

    # Any vanilla-* directories other than the base one are stale.
    for dir in vanilla-*; do
      [ "$dir" = vanilla-%{kversion} ] || rm -rf $dir &
    done

  else

    rm -f pax_global_header
    # Look for an identical base vanilla dir that can be hardlinked.
    for sharedir in $sharedirs ; do
      if [[ ! -z $sharedir  &&  -d $sharedir/vanilla-%{kversion} ]] ; then
        break
      fi
    done
    if [[ ! -z $sharedir  &&  -d $sharedir/vanilla-%{kversion} ]] ; then
%setup -q -n kernel-%{kversion}%{?dist} -c -T
      cp -al $sharedir/vanilla-%{kversion} .
    else
%setup -q -n kernel-%{kversion}%{?dist} -c
      mv linux-%{kversion} vanilla-%{kversion}
    fi

  fi

%if "%{kversion}" != "%{vanillaversion}"

  for sharedir in $sharedirs ; do
    if [[ ! -z $sharedir  &&  -d $sharedir/vanilla-%{vanillaversion} ]] ; then
      break
    fi
  done
  if [[ ! -z $sharedir  &&  -d $sharedir/vanilla-%{vanillaversion} ]] ; then

    cp -al $sharedir/vanilla-%{vanillaversion} .

  else

    # Need to apply patches to the base vanilla version.
    cp -al vanilla-%{kversion} vanilla-%{vanillaversion}
    cd vanilla-%{vanillaversion}

# Update vanilla to the latest upstream.
# (non-released_kernel case only)
%if 0%{?rcrev}
    ApplyPatch patch-3.%{upstream_sublevel}-rc%{rcrev}.xz
%if 0%{?gitrev}
    ApplyPatch patch-3.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}.xz
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
    ApplyPatch patch-3.%{base_sublevel}-git%{gitrev}.xz
%endif
%endif

    cd ..

  fi

%endif

else

  # We already have all vanilla dirs, just change to the top-level directory.
  cd kernel-%{kversion}%{?dist}

fi

# Now build the fedora kernel tree.
cp -al vanilla-%{vanillaversion} linux-%{KVERREL}

cd linux-%{KVERREL}

# released_kernel with possible stable updates
%if 0%{?stable_base}
ApplyPatch %{stable_patch_00}
%endif

# Drop some necessary files from the source dir into the buildroot
cp $RPM_SOURCE_DIR/config-* .
cp %{SOURCE15} .

%if !%{debugbuildsenabled}
%if %{with_release}
# The normal build is a really debug build and the user has explicitly requested
# a release kernel. Change the config files into non-debug versions.
make -f %{SOURCE19} config-release
%endif
%endif

# Dynamically generate kernel .config files from config-* files
make -f %{SOURCE20} VERSION=%{version} configs

# Merge in any user-provided local config option changes
%ifnarch %nobuildarches
for i in %{all_arch_configs}
do
  mv $i $i.tmp
  ./merge.pl %{SOURCE1000} $i.tmp > $i
  rm $i.tmp
done
%endif

ApplyPatch kbuild-AFTER_LINK.patch

#
# misc small stuff to make things compile
#
ApplyOptionalPatch compile-fixes.patch

%if !%{nopatches}

# revert patches from upstream that conflict or that we get via other means
ApplyOptionalPatch upstream-reverts.patch -R

# Architecture patches
# x86(-64)
ApplyPatch lib-cpumask-Make-CPUMASK_OFFSTACK-usable-without-deb.patch

# PPC

# ARM64

#
# ARM
#
ApplyPatch ARM-tegra-usb-no-reset.patch

ApplyPatch arm-dts-am335x-boneblack-lcdc-add-panel-info.patch
ApplyPatch arm-dts-am335x-boneblack-add-cpu0-opp-points.patch
ApplyPatch arm-dts-am335x-bone-common-enable-and-use-i2c2.patch
ApplyPatch arm-dts-am335x-bone-common-setup-default-pinmux-http.patch
ApplyPatch arm-dts-am335x-bone-common-add-uart2_pins-uart4_pins.patch
ApplyPatch pinctrl-pinctrl-single-must-be-initialized-early.patch

ApplyPatch arm-i.MX6-Utilite-device-dtb.patch
ApplyPatch arm-dts-sun7i-bananapi.patch

ApplyPatch arm-highbank-l2-reverts.patch

#
# bugfixes to drivers and filesystems
#

# ext4

# xfs

# btrfs

# eCryptfs

# NFSv4

# USB

# WMI

# ACPI

#
# PCI
#

#
# SCSI Bits.
#

# ACPI

ApplyPatch Revert-Revert-ACPI-video-change-acpi-video-brightnes.patch

# ALSA
ApplyPatch alsa-usb-add-marantz-dsd-quirk-v2.patch
ApplyPatch alsa-usb-marantz-select-mode-quirk-v6.patch
ApplyPatch alsa-usb-add-matrix-audio-native-dsd-v2.patch

# Networking

# Misc fixes
# The input layer spews crap no-one cares about.
ApplyPatch input-kill-stupid-messages.patch

# stop floppy.ko from autoloading during udev...
ApplyPatch die-floppy-die.patch

ApplyPatch no-pcspkr-modalias.patch

# Silence some useless messages that still get printed with 'quiet'
ApplyPatch input-silence-i8042-noise.patch

# Make fbcon not show the penguins with 'quiet'
ApplyPatch silence-fbcon-logo.patch

# Changes to upstream defaults.
#rhbz 1126580
ApplyPatch Kbuild-Add-an-option-to-enable-GCC-VTA.patch

# /dev/crash driver.
ApplyPatch crash-driver.patch

# crypto/

# secure boot
ApplyPatch Add-secure_modules-call.patch
ApplyPatch PCI-Lock-down-BAR-access-when-module-security-is-ena.patch
ApplyPatch x86-Lock-down-IO-port-access-when-module-security-is.patch
ApplyPatch ACPI-Limit-access-to-custom_method.patch
ApplyPatch asus-wmi-Restrict-debugfs-interface-when-module-load.patch
ApplyPatch Restrict-dev-mem-and-dev-kmem-when-module-loading-is.patch
ApplyPatch acpi-Ignore-acpi_rsdp-kernel-parameter-when-module-l.patch
ApplyPatch kexec-Disable-at-runtime-if-the-kernel-enforces-modu.patch
ApplyPatch x86-Restrict-MSR-access-when-module-loading-is-restr.patch
ApplyPatch Add-option-to-automatically-enforce-module-signature.patch
ApplyPatch efi-Disable-secure-boot-if-shim-is-in-insecure-mode.patch
ApplyPatch efi-Make-EFI_SECURE_BOOT_SIG_ENFORCE-depend-on-EFI.patch
ApplyPatch efi-Add-EFI_SECURE_BOOT-bit.patch
ApplyPatch hibernate-Disable-in-a-signed-modules-environment.patch

ApplyPatch Add-EFI-signature-data-types.patch
ApplyPatch Add-an-EFI-signature-blob-parser-and-key-loader.patch
ApplyPatch KEYS-Add-a-system-blacklist-keyring.patch
ApplyPatch MODSIGN-Import-certificates-from-UEFI-Secure-Boot.patch
ApplyPatch MODSIGN-Support-not-importing-certs-from-db.patch

ApplyPatch Add-sysrq-option-to-disable-secure-boot-mode.patch

# Assorted Virt Fixes

# DRM core

# Nouveau DRM

# Intel DRM
ApplyPatch drm-i915-hush-check-crtc-state.patch
ApplyPatch drm-i915-Don-t-WARN-in-edp_panel_vdd_off.patch

# Radeon DRM

# Patches headed upstream
ApplyPatch disable-i8042-check-on-apple-mac.patch

# FIXME: REBASE
#ApplyPatch hibernate-freeze-filesystems.patch

ApplyPatch lis3-improve-handling-of-null-rate.patch

# Disable watchdog on virtual machines.
ApplyPatch watchdog-Disable-watchdog-on-virtual-machines.patch

#rhbz 754518
ApplyPatch scsi-sd_revalidate_disk-prevent-NULL-ptr-deref.patch

#pplyPatch weird-root-dentry-name-debug.patch

# https://fedoraproject.org/wiki/Features/Checkpoint_Restore
ApplyPatch criu-no-expert.patch

#rhbz 892811
ApplyPatch ath9k-rx-dma-stop-check.patch

# Patch series from Hans for various backlight and platform driver fixes
ApplyPatch samsung-laptop-Add-broken-acpi-video-quirk-for-NC210.patch

#rhbz 1089731
ApplyPatch asus-nb-wmi-Add-wapf4-quirk-for-the-X550VB.patch

#rhbz 1135338
ApplyPatch HID-add-support-for-MS-Surface-Pro-3-Type-Cover.patch

#rhbz 1164945
ApplyPatch xhci-Add-broken-streams-quirk-for-Fresco-Logic-FL100.patch
ApplyPatch uas-Add-US_FL_NO_ATA_1X-for-Seagate-devices-with-usb.patch
ApplyPatch uas-Add-US_FL_NO_REPORT_OPCODES-for-JMicron-JMS566-w.patch

#rhbz 1172543
ApplyPatch cfg80211-don-t-WARN-about-two-consecutive-Country-IE.patch

#rhbz 1173806
ApplyPatch powerpc-powernv-force-all-CPUs-to-be-bootable.patch

ApplyPatch uapi-linux-target_core_user.h-fix-headers_install.sh.patch

#rhbz 1163927
ApplyPatch Set-UID-in-sess_auth_rawntlmssp_authenticate-too.patch

#CVE-2014-9428 rhbz 1178826,1178833
ApplyPatch batman-adv-Calculate-extra-tail-size-based-on-queued.patch

#CVE-2014-9529 rhbz 1179813 1179853
ApplyPatch KEYS-close-race-between-key-lookup-and-freeing.patch

#rhbz 1124119
ApplyPatch uas-Do-not-blacklist-ASM1153-disk-enclosures.patch
ApplyPatch uas-Add-US_FL_NO_ATA_1X-for-2-more-Seagate-disk-encl.patch
ApplyPatch uas-Add-no-report-opcodes-quirk-for-Simpletech-devic.patch

#rhbz 1115713
ApplyPatch samsung-laptop-Add-use_native_backlight-quirk-and-en.patch
#rhbz 1163574
ApplyPatch acpi-video-Add-disable_native_backlight-quirk-for-De.patch
#rhbz 1094948
ApplyPatch acpi-video-Add-disable_native_backlight-quirk-for-Sa.patch

# Fix for big-endian arches, already upstream
ApplyPatch mpssd-x86-only.patch

# Patches from 3.18.4 stable queue (should fix i915 issues)
ApplyPatch stable-3.18.4-queue.patch
ApplyPatch xhci-check-if-slot-is-already-in-default-state.patch

%if 0%{?aarch64patches}
ApplyPatch kernel-arm64.patch
%ifnarch aarch64 # this is stupid, but i want to notice before secondary koji does.
ApplyPatch kernel-arm64.patch -R
%else
#  solved with SPCR in future
%endif
%endif

# END OF PATCH APPLICATIONS

%endif

# Any further pre-build tree manipulations happen here.

chmod +x scripts/checkpatch.pl

# This Prevents scripts/setlocalversion from mucking with our version numbers.
touch .scmversion

# only deal with configs if we are going to build for the arch
%ifnarch %nobuildarches

mkdir configs

%if !%{debugbuildsenabled}
rm -f kernel-%{version}-*debug.config
%endif

%define make make %{?cross_opts}

# now run oldconfig over all the config files
for i in *.config
do
  mv $i .config
  Arch=`head -1 .config | cut -b 3-`
  make ARCH=$Arch listnewconfig | grep -E '^CONFIG_' >.newoptions || true
%if %{listnewconfig_fail}
  if [ -s .newoptions ]; then
    cat .newoptions
    exit 1
  fi
%endif
  rm -f .newoptions
  make ARCH=$Arch oldnoconfig
  echo "# $Arch" > configs/$i
  cat .config >> configs/$i
done
# end of kernel config
%endif

# get rid of unwanted files resulting from patch fuzz
find . \( -name "*.orig" -o -name "*~" \) -exec rm -f {} \; >/dev/null

# remove unnecessary SCM files
find . -name .gitignore -exec rm -f {} \; >/dev/null

cd ..

###
### build
###
%build

%if %{with_sparse}
%define sparse_mflags	C=1
%endif

%if %{with_debuginfo}
# This override tweaks the kernel makefiles so that we run debugedit on an
# object before embedding it.  When we later run find-debuginfo.sh, it will
# run debugedit again.  The edits it does change the build ID bits embedded
# in the stripped object, but repeating debugedit is a no-op.  We do it
# beforehand to get the proper final build ID bits into the embedded image.
# This affects the vDSO images in vmlinux, and the vmlinux image in bzImage.
export AFTER_LINK=\
'sh -xc "/usr/lib/rpm/debugedit -b $$RPM_BUILD_DIR -d /usr/src/debug \
    				-i $@ > $@.id"'
%endif

cp_vmlinux()
{
  eu-strip --remove-comment -o "$2" "$1"
}

BuildKernel() {
    MakeTarget=$1
    KernelImage=$2
    Flavour=$3
    Flav=${Flavour:++${Flavour}}
    InstallName=${4:-vmlinuz}

    # Pick the right config file for the kernel we're building
    Config=kernel-%{version}-%{_target_cpu}${Flavour:+-${Flavour}}.config
    DevelDir=/usr/src/kernels/%{KVERREL}${Flav}

    # When the bootable image is just the ELF kernel, strip it.
    # We already copy the unstripped file into the debuginfo package.
    if [ "$KernelImage" = vmlinux ]; then
      CopyKernel=cp_vmlinux
    else
      CopyKernel=cp
    fi

    KernelVer=%{version}-%{release}.%{_target_cpu}${Flav}
    echo BUILDING A KERNEL FOR ${Flavour} %{_target_cpu}...

    %if 0%{?stable_update}
    # make sure SUBLEVEL is incremented on a stable release.  Sigh 3.x.
    perl -p -i -e "s/^SUBLEVEL.*/SUBLEVEL = %{?stablerev}/" Makefile
    %endif

    # make sure EXTRAVERSION says what we want it to say
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}.%{_target_cpu}${Flav}/" Makefile

    # if pre-rc1 devel kernel, must fix up PATCHLEVEL for our versioning scheme
    %if !0%{?rcrev}
    %if 0%{?gitrev}
    perl -p -i -e 's/^PATCHLEVEL.*/PATCHLEVEL = %{upstream_sublevel}/' Makefile
    %endif
    %endif

    # and now to start the build process

    make -s mrproper
    cp configs/$Config .config

    %if %{signmodules}
    cp %{SOURCE11} .
    %endif

    chmod +x scripts/sign-file

    Arch=`head -1 .config | cut -b 3-`
    echo USING ARCH=$Arch

    make -s ARCH=$Arch oldnoconfig >/dev/null
    %{make} -s ARCH=$Arch V=1 %{?_smp_mflags} $MakeTarget %{?sparse_mflags} %{?kernel_mflags}
    %{make} -s ARCH=$Arch V=1 %{?_smp_mflags} modules %{?sparse_mflags} || exit 1

%ifarch %{arm} aarch64
    %{make} -s ARCH=$Arch V=1 dtbs
    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}/dtb-$KernelVer
    install -m 644 arch/$Arch/boot/dts/*.dtb $RPM_BUILD_ROOT/%{image_install_path}/dtb-$KernelVer/
    rm -f arch/$Arch/boot/dts/*.dtb
%endif

    # Start installing the results
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/boot
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/%{image_install_path}
%endif
    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}
    install -m 644 .config $RPM_BUILD_ROOT/boot/config-$KernelVer
    install -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-$KernelVer

    # We estimate the size of the initramfs because rpm needs to take this size
    # into consideration when performing disk space calculations. (See bz #530778)
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-$KernelVer.img bs=1M count=20

    if [ -f arch/$Arch/boot/zImage.stub ]; then
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/%{image_install_path}/zImage.stub-$KernelVer || :
    fi
    %if %{signmodules}
    # Sign the image if we're using EFI
    %pesign -s -i $KernelImage -o vmlinuz.signed
    if [ ! -s vmlinuz.signed ]; then
        echo "pesigning failed"
        exit 1
    fi
    mv vmlinuz.signed $KernelImage
    %endif
    $CopyKernel $KernelImage \
    		$RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    chmod 755 $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer

    # hmac sign the kernel for FIPS
    echo "Creating hmac file: $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac"
    ls -l $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    sha512hmac $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer | sed -e "s,$RPM_BUILD_ROOT,," > $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac;

    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
    # Override $(mod-fw) because we don't want it to install any firmware
    # we'll get it from the linux-firmware package and we don't want conflicts
    %{make} -s ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=$KernelVer mod-fw=

%ifarch %{vdso_arches}
    %{make} -s ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=$KernelVer
    if [ ! -s ldconfig-kernel.conf ]; then
      echo > ldconfig-kernel.conf "\
# Placeholder file, no vDSO hwcap entries used in this kernel."
    fi
    %{__install} -D -m 444 ldconfig-kernel.conf \
        $RPM_BUILD_ROOT/etc/ld.so.conf.d/kernel-$KernelVer.conf
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/vdso/.build-id
%endif

    # And save the headers/makefiles etc for building modules against
    #
    # This all looks scary, but the end result is supposed to be:
    # * all arch relevant include/ files
    # * all Makefile/Kconfig files
    # * all script/ files

    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/source
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    (cd $RPM_BUILD_ROOT/lib/modules/$KernelVer ; ln -s build source)
    # dirs for additional modules per module-init-tools, kbuild/modules.txt
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/extra
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/updates
    # first copy everything
    cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp Module.symvers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp System.map $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -s Module.markers ]; then
      cp Module.markers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    fi
    # then drop all but the needed Makefiles/Kconfig files
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Documentation
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    cp .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -d arch/$Arch/scripts ]; then
      cp -a arch/$Arch/scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch} || :
    fi
    if [ -f arch/$Arch/*lds ]; then
      cp -a arch/$Arch/*lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch}/ || :
    fi
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*.o
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*/*.o
%ifarch %{power64}
    cp -a --parents arch/powerpc/lib/crtsavres.[So] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    if [ -d arch/%{asmarch}/include ]; then
      cp -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
%ifarch aarch64
    # arch/arm64/include/asm/xen references arch/arm
    cp -a --parents arch/arm/include/asm/xen $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    # include the machine specific headers for ARM variants, if available.
%ifarch %{arm}
    if [ -d arch/%{asmarch}/mach-${Flavour}/include ]; then
      cp -a --parents arch/%{asmarch}/mach-${Flavour}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
%endif
    cp -a include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include

    # Make sure the Makefile and version.h have a matching timestamp so that
    # external modules can be built
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/generated/uapi/linux/version.h

    # Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
    cp $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/config/auto.conf

%if %{with_debuginfo}
    if test -s vmlinux.id; then
      cp vmlinux.id $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/vmlinux.id
    else
      echo >&2 "*** ERROR *** no vmlinux build ID! ***"
      exit 1
    fi

    #
    # save the vmlinux file for kernel debugging into the kernel-debuginfo rpm
    #
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
    cp vmlinux $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
%endif

    find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name "*.ko" -type f >modnames

    # mark modules executable so that strip-to-file can strip them
    xargs --no-run-if-empty chmod u+x < modnames

    # Generate a list of modules for block and networking.

    grep -F /drivers/ modnames | xargs --no-run-if-empty nm -upA |
    sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

    collect_modules_list()
    {
      sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef |
        LC_ALL=C sort -u > $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
      if [ ! -z "$3" ]; then
        sed -r -e "/^($3)\$/d" -i $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
      fi
    }

    collect_modules_list networking \
    			 'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register|rt(l_|2x00)(pci|usb)_probe|register_netdevice'
    collect_modules_list block \
    			 'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_alloc_queue|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler|blk_queue_physical_block_size' 'pktcdvd.ko|dm-mod.ko'
    collect_modules_list drm \
    			 'drm_open|drm_init'
    collect_modules_list modesetting \
    			 'drm_crtc_init'

    # detect missing or incorrect license tags
    ( find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name '*.ko' | xargs /sbin/modinfo -l | \
        grep -E -v 'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' ) && exit 1

    # remove files that will be auto generated by depmod at rpm -i time
    pushd $RPM_BUILD_ROOT/lib/modules/$KernelVer/
        rm -f modules.{alias*,builtin.bin,dep*,*map,symbols*,devname,softdep}
    popd

    # Call the modules-extra script to move things around
    %{SOURCE17} $RPM_BUILD_ROOT/lib/modules/$KernelVer %{SOURCE16}

    #
    # Generate the kernel-core and kernel-modules files lists
    #

    # Copy the System.map file for depmod to use, and create a backup of the
    # full module tree so we can restore it after we're done filtering
    cp System.map $RPM_BUILD_ROOT/.
    pushd $RPM_BUILD_ROOT
    mkdir restore
    cp -r lib/modules/$KernelVer/* restore/.

    # don't include anything going into k-m-e in the file lists
    rm -rf lib/modules/$KernelVer/extra

    # Find all the module files and filter them out into the core and modules
    # lists.  This actually removes anything going into -modules from the dir.
    find lib/modules/$KernelVer/kernel -name *.ko | sort -n > modules.list
	cp $RPM_SOURCE_DIR/filter-*.sh .
    %{SOURCE99} modules.list %{_target_cpu}
	rm filter-*.sh

    # Run depmod on the resulting module tree and make sure it isn't broken
    depmod -b . -aeF ./System.map $KernelVer &> depmod.out
    if [ -s depmod.out ]; then
        echo "Depmod failure"
        cat depmod.out
        exit 1
    else
        rm depmod.out
    fi
    # remove files that will be auto generated by depmod at rpm -i time
    pushd $RPM_BUILD_ROOT/lib/modules/$KernelVer/
        rm -f modules.{alias*,builtin.bin,dep*,*map,symbols*,devname,softdep}
    popd

    # Go back and find all of the various directories in the tree.  We use this
    # for the dir lists in kernel-core
    find lib/modules/$KernelVer/kernel -type d | sort -n > module-dirs.list

    # Cleanup
    rm System.map
    cp -r restore/* lib/modules/$KernelVer/.
    rm -rf restore
    popd

    # Make sure the files lists start with absolute paths or rpmbuild fails.
    # Also add in the dir entries
    sed -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/k-d.list > ../kernel${Flavour:+-${Flavour}}-modules.list
    sed -e 's/^lib*/%dir \/lib/' %{?zipsed} $RPM_BUILD_ROOT/module-dirs.list > ../kernel${Flavour:+-${Flavour}}-core.list
    sed -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/modules.list >> ../kernel${Flavour:+-${Flavour}}-core.list

    # Cleanup
    rm -f $RPM_BUILD_ROOT/k-d.list
    rm -f $RPM_BUILD_ROOT/modules.list
    rm -f $RPM_BUILD_ROOT/module-dirs.list

%if %{signmodules}
    # Save the signing keys so we can sign the modules in __modsign_install_post
    cp signing_key.priv signing_key.priv.sign${Flav}
    cp signing_key.x509 signing_key.x509.sign${Flav}
%endif

    # Move the devel headers out of the root file system
    mkdir -p $RPM_BUILD_ROOT/usr/src/kernels
    mv $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT/$DevelDir

    # This is going to create a broken link during the build, but we don't use
    # it after this point.  We need the link to actually point to something
    # when kernel-devel is installed, and a relative link doesn't work across
    # the F17 UsrMove feature.
    ln -sf $DevelDir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

    # prune junk from kernel-devel
    find $RPM_BUILD_ROOT/usr/src/kernels -name ".*.cmd" -exec rm -f {} \;
}

###
# DO it...
###

# prepare directories
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/boot
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}

cd linux-%{KVERREL}

%if %{with_debug}
BuildKernel %make_target %kernel_image debug
%endif

%if %{with_pae_debug}
BuildKernel %make_target %kernel_image %{pae}debug
%endif

%if %{with_pae}
BuildKernel %make_target %kernel_image %{pae}
%endif

%if %{with_up}
BuildKernel %make_target %kernel_image
%endif

%global perf_make \
  make -s %{?cross_opts} %{?_smp_mflags} -C tools/perf V=1 WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_LIBNUMA=1 NO_STRLCPY=1 NO_BIONIC=1 prefix=%{_prefix}
%if %{with_perf}
# perf
%{perf_make} DESTDIR=$RPM_BUILD_ROOT all
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
# cpupower
# make sure version-gen.sh is executable.
chmod +x tools/power/cpupower/utils/version-gen.sh
%{make} %{?_smp_mflags} -C tools/power/cpupower CPUFREQ_BENCH=false
%ifarch %{ix86}
    pushd tools/power/cpupower/debug/i386
    %{make} %{?_smp_mflags} centrino-decode powernow-k8-decode
    popd
%endif
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    %{make} %{?_smp_mflags} centrino-decode powernow-k8-decode
    popd
%endif
%ifarch %{ix86} x86_64
   pushd tools/power/x86/x86_energy_perf_policy/
   %{make}
   popd
   pushd tools/power/x86/turbostat
   %{make}
   popd
%endif #turbostat/x86_energy_perf_policy
%endif
pushd tools/thermal/tmon/
%{make}
popd
%endif

# In the modsign case, we do 3 things.  1) We check the "flavour" and hard
# code the value in the following invocations.  This is somewhat sub-optimal
# but we're doing this inside of an RPM macro and it isn't as easy as it
# could be because of that.  2) We restore the .tmp_versions/ directory from
# the one we saved off in BuildKernel above.  This is to make sure we're
# signing the modules we actually built/installed in that flavour.  3) We
# grab the arch and invoke mod-sign.sh command to actually sign the modules.
#
# We have to do all of those things _after_ find-debuginfo runs, otherwise
# that will strip the signature off of the modules.

%define __modsign_install_post \
  if [ "%{signmodules}" -eq "1" ]; then \
    if [ "%{with_pae}" -ne "0" ]; then \
      %{modsign_cmd} signing_key.priv.sign+%{pae} signing_key.x509.sign+%{pae} $RPM_BUILD_ROOT/lib/modules/%{KVERREL}+%{pae}/ \
    fi \
    if [ "%{with_debug}" -ne "0" ]; then \
      %{modsign_cmd} signing_key.priv.sign+debug signing_key.x509.sign+debug $RPM_BUILD_ROOT/lib/modules/%{KVERREL}+debug/ \
    fi \
    if [ "%{with_pae_debug}" -ne "0" ]; then \
      %{modsign_cmd} signing_key.priv.sign+%{pae}debug signing_key.x509.sign+%{pae}debug $RPM_BUILD_ROOT/lib/modules/%{KVERREL}+%{pae}debug/ \
    fi \
    if [ "%{with_up}" -ne "0" ]; then \
      %{modsign_cmd} signing_key.priv.sign signing_key.x509.sign $RPM_BUILD_ROOT/lib/modules/%{KVERREL}/ \
    fi \
  fi \
  if [ "%{zipmodules}" -eq "1" ]; then \
    find $RPM_BUILD_ROOT/lib/modules/ -type f -name '*.ko' | xargs xz; \
  fi \
%{nil}

###
### Special hacks for debuginfo subpackages.
###

# This macro is used by %%install, so we must redefine it before that.
%define debug_package %{nil}

%if %{with_debuginfo}

%define __debug_install_post \
  /usr/lib/rpm/find-debuginfo.sh %{debuginfo_args} %{_builddir}/%{?buildsubdir}\
%{nil}

%ifnarch noarch
%global __debug_package 1
%files -f debugfiles.list debuginfo-common-%{_target_cpu}
%defattr(-,root,root)
%endif

%endif

#
# Disgusting hack alert! We need to ensure we sign modules *after* all
# invocations of strip occur, which is in __debug_install_post if
# find-debuginfo.sh runs, and __os_install_post if not.
#
%define __spec_install_post \
  %{?__debug_package:%{__debug_install_post}}\
  %{__arch_install_post}\
  %{__os_install_post}\
  %{__modsign_install_post}

###
### install
###

%install

cd linux-%{KVERREL}

# We have to do the headers install before the tools install because the
# kernel headers_install will remove any header files in /usr/include that
# it doesn't install itself.

%if %{with_headers}
# Install kernel headers
make ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

find $RPM_BUILD_ROOT/usr/include \
     \( -name .install -o -name .check -o \
     	-name ..install.cmd -o -name ..check.cmd \) | xargs rm -f

%endif

%if %{with_perf}
# perf tool binary and supporting scripts/binaries
%{perf_make} DESTDIR=$RPM_BUILD_ROOT lib=%{_lib} install-bin install-traceevent-plugins
# remove the 'trace' symlink.
rm -f %{buildroot}%{_bindir}/trace

# python-perf extension
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-python_ext

# perf man pages (note: implicit rpm magic compresses them later)
mkdir -p %{buildroot}/%{_mandir}/man1
pushd %{buildroot}/%{_mandir}/man1
tar -xf %{SOURCE10}
popd
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
%{make} -C tools/power/cpupower DESTDIR=$RPM_BUILD_ROOT libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install
rm -f %{buildroot}%{_libdir}/*.{a,la}
%find_lang cpupower
mv cpupower.lang ../
%ifarch %{ix86}
    pushd tools/power/cpupower/debug/i386
    install -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
    install -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
    popd
%endif
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    install -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
    install -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
    popd
%endif
chmod 0755 %{buildroot}%{_libdir}/libcpupower.so*
mkdir -p %{buildroot}%{_unitdir} %{buildroot}%{_sysconfdir}/sysconfig
install -m644 %{SOURCE2000} %{buildroot}%{_unitdir}/cpupower.service
install -m644 %{SOURCE2001} %{buildroot}%{_sysconfdir}/sysconfig/cpupower
%endif
%ifarch %{ix86} x86_64
   mkdir -p %{buildroot}%{_mandir}/man8
   pushd tools/power/x86/x86_energy_perf_policy
   make DESTDIR=%{buildroot} install
   popd
   pushd tools/power/x86/turbostat
   make DESTDIR=%{buildroot} install
   popd
%endif #turbostat/x86_energy_perf_policy
pushd tools/thermal/tmon
make INSTALL_ROOT=%{buildroot} install
popd
%endif

%if %{with_bootwrapper}
make DESTDIR=$RPM_BUILD_ROOT bootwrapper_install WRAPPER_OBJDIR=%{_libdir}/kernel-wrapper WRAPPER_DTSDIR=%{_libdir}/kernel-wrapper/dts
%endif


###
### clean
###

%clean
rm -rf $RPM_BUILD_ROOT

###
### scripts
###

%if %{with_tools}
%post -n kernel-tools
/sbin/ldconfig

%postun -n kernel-tools
/sbin/ldconfig
%endif

#
# This macro defines a %%post script for a kernel*-devel package.
#	%%kernel_devel_post [<subpackage>]
#
%define kernel_devel_post() \
%{expand:%%post %{?1:%{1}-}devel}\
if [ -f /etc/sysconfig/kernel ]\
then\
    . /etc/sysconfig/kernel || exit $?\
fi\
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ]\
then\
    (cd /usr/src/kernels/%{KVERREL}%{?1:+%{1}} &&\
     /usr/bin/find . -type f | while read f; do\
       hardlink -c /usr/src/kernels/*.fc*.*/$f $f\
     done)\
fi\
%{nil}

#
# This macro defines a %%post script for a kernel*-modules-extra package.
# It also defines a %%postun script that does the same thing.
#	%%kernel_modules_extra_post [<subpackage>]
#
%define kernel_modules_extra_post() \
%{expand:%%post %{?1:%{1}-}modules-extra}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}\
%{expand:%%postun %{?1:%{1}-}modules-extra}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}

#
# This macro defines a %%post script for a kernel*-modules package.
# It also defines a %%postun script that does the same thing.
#	%%kernel_modules_post [<subpackage>]
#
%define kernel_modules_post() \
%{expand:%%post %{?1:%{1}-}modules}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}\
%{expand:%%postun %{?1:%{1}-}modules}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}

# This macro defines a %%posttrans script for a kernel package.
#	%%kernel_variant_posttrans [<subpackage>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_posttrans() \
%{expand:%%posttrans %{?1:%{1}-}core}\
/bin/kernel-install add %{KVERREL}%{?1:+%{1}} /%{image_install_path}/vmlinuz-%{KVERREL}%{?1:+%{1}} || exit $?\
%{nil}

#
# This macro defines a %%post script for a kernel package and its devel package.
#	%%kernel_variant_post [-v <subpackage>] [-r <replace>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_post(v:r:) \
%{expand:%%kernel_devel_post %{?-v*}}\
%{expand:%%kernel_modules_post %{?-v*}}\
%{expand:%%kernel_modules_extra_post %{?-v*}}\
%{expand:%%kernel_variant_posttrans %{?-v*}}\
%{expand:%%post %{?-v*:%{-v*}-}core}\
%{-r:\
if [ `uname -i` == "x86_64" -o `uname -i` == "i386" ] &&\
   [ -f /etc/sysconfig/kernel ]; then\
  /bin/sed -r -i -e 's/^DEFAULTKERNEL=%{-r*}$/DEFAULTKERNEL=kernel%{?-v:-%{-v*}}/' /etc/sysconfig/kernel || exit $?\
fi}\
%{nil}

#
# This macro defines a %%preun script for a kernel package.
#	%%kernel_variant_preun <subpackage>
#
%define kernel_variant_preun() \
%{expand:%%preun %{?1:%{1}-}core}\
/bin/kernel-install remove %{KVERREL}%{?1:+%{1}} /%{image_install_path}/vmlinuz-%{KVERREL}%{?1:+%{1}} || exit $?\
%{nil}

%kernel_variant_preun
%kernel_variant_post -r kernel-smp

%kernel_variant_preun %{pae}
%kernel_variant_post -v %{pae} -r (kernel|kernel-smp)

%kernel_variant_post -v %{pae}debug -r (kernel|kernel-smp)
%kernel_variant_preun %{pae}debug

%kernel_variant_preun debug
%kernel_variant_post -v debug

if [ -x /sbin/ldconfig ]
then
    /sbin/ldconfig -X || exit $?
fi

###
### file lists
###

%if %{with_headers}
%files headers
%defattr(-,root,root)
/usr/include/*
%endif

%if %{with_bootwrapper}
%files bootwrapper
%defattr(-,root,root)
/usr/sbin/*
%{_libdir}/kernel-wrapper
%endif

%if %{with_perf}
%files -n perf
%defattr(-,root,root)
%{_bindir}/perf
%dir %{_libdir}/traceevent/plugins
%{_libdir}/traceevent/plugins/*
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_mandir}/man[1-8]/perf*
%{_sysconfdir}/bash_completion.d/perf
%doc linux-%{KVERREL}/tools/perf/Documentation/examples.txt

%files -n python-perf
%defattr(-,root,root)
%{python_sitearch}

%if %{with_debuginfo}
%files -f perf-debuginfo.list -n perf-debuginfo
%defattr(-,root,root)

%files -f python-perf-debuginfo.list -n python-perf-debuginfo
%defattr(-,root,root)
%endif
%endif # with_perf

%if %{with_tools}
%files -n kernel-tools -f cpupower.lang
%defattr(-,root,root)
%ifarch %{cpupowerarchs}
%{_bindir}/cpupower
%ifarch %{ix86} x86_64
%{_bindir}/centrino-decode
%{_bindir}/powernow-k8-decode
%endif
%{_unitdir}/cpupower.service
%{_mandir}/man[1-8]/cpupower*
%config(noreplace) %{_sysconfdir}/sysconfig/cpupower
%ifarch %{ix86} x86_64
%{_bindir}/x86_energy_perf_policy
%{_mandir}/man8/x86_energy_perf_policy*
%{_bindir}/turbostat
%{_mandir}/man8/turbostat*
%endif
%{_bindir}/tmon
%endif

%if %{with_debuginfo}
%files -f kernel-tools-debuginfo.list -n kernel-tools-debuginfo
%defattr(-,root,root)
%endif

%ifarch %{cpupowerarchs}
%files -n kernel-tools-libs
%{_libdir}/libcpupower.so.0
%{_libdir}/libcpupower.so.0.0.0

%files -n kernel-tools-libs-devel
%{_libdir}/libcpupower.so
%{_includedir}/cpufreq.h
%endif
%endif # with_perf

# empty meta-package
%files
%defattr(-,root,root)

# This is %%{image_install_path} on an arch where that includes ELF files,
# or empty otherwise.
%define elf_image_install_path %{?kernel_image_elf:%{image_install_path}}

#
# This macro defines the %%files sections for a kernel package
# and its devel and debuginfo packages.
#	%%kernel_variant_files [-k vmlinux] <condition> <subpackage>
#
%define kernel_variant_files(k:) \
%if %{1}\
%{expand:%%files -f kernel-%{?2:%{2}-}core.list %{?2:%{2}-}core}\
%defattr(-,root,root)\
%{!?_licensedir:%global license %%doc}\
%license linux-%{KVERREL}/COPYING\
/%{image_install_path}/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVERREL}%{?2:+%{2}}\
/%{image_install_path}/.vmlinuz-%{KVERREL}%{?2:+%{2}}.hmac \
%ifarch %{arm} aarch64\
/%{image_install_path}/dtb-%{KVERREL}%{?2:+%{2}} \
%endif\
%attr(600,root,root) /boot/System.map-%{KVERREL}%{?2:+%{2}}\
/boot/config-%{KVERREL}%{?2:+%{2}}\
%ghost /boot/initramfs-%{KVERREL}%{?2:+%{2}}.img\
%dir /lib/modules\
%dir /lib/modules/%{KVERREL}%{?2:+%{2}}\
%dir /lib/modules/%{KVERREL}%{?2:+%{2}}/kernel\
/lib/modules/%{KVERREL}%{?2:+%{2}}/build\
/lib/modules/%{KVERREL}%{?2:+%{2}}/source\
/lib/modules/%{KVERREL}%{?2:+%{2}}/updates\
%ifarch %{vdso_arches}\
/lib/modules/%{KVERREL}%{?2:+%{2}}/vdso\
/etc/ld.so.conf.d/kernel-%{KVERREL}%{?2:+%{2}}.conf\
%endif\
/lib/modules/%{KVERREL}%{?2:+%{2}}/modules.*\
%{expand:%%files -f kernel-%{?2:%{2}-}modules.list %{?2:%{2}-}modules}\
%defattr(-,root,root)\
%{expand:%%files %{?2:%{2}-}devel}\
%defattr(-,root,root)\
/usr/src/kernels/%{KVERREL}%{?2:+%{2}}\
%{expand:%%files %{?2:%{2}-}modules-extra}\
%defattr(-,root,root)\
/lib/modules/%{KVERREL}%{?2:+%{2}}/extra\
%if %{with_debuginfo}\
%ifnarch noarch\
%{expand:%%files -f debuginfo%{?2}.list %{?2:%{2}-}debuginfo}\
%defattr(-,root,root)\
%endif\
%endif\
%if %{?2:1} %{!?2:0}\
%{expand:%%files %{2}}\
%defattr(-,root,root)\
%endif\
%endif\
%{nil}


%kernel_variant_files %{with_up}
%kernel_variant_files %{with_debug} debug
%kernel_variant_files %{with_pae} %{pae}
%kernel_variant_files %{with_pae_debug} %{pae}debug

# plz don't put in a version string unless you're going to tag
# and build.
#
# 
#                        ___________________________________________________________
#                       / This branch is for Fedora 21. You probably want to commit \
#  _____ ____  _        \ to the F-20 branch instead, or in addition to this one.   /
# |  ___|___ \/ |        -----------------------------------------------------------
# | |_    __) | |             \   ^__^
# |  _|  / __/| |              \  (@@)\_______
# |_|   |_____|_|                 (__)\       )\/\
#                                    ||----w |
#                                    ||     ||
%changelog
* Mon Jan 19 2015 Justin M. Forbes <jforbes@fedoraproject.org> - 3.18.3-201
- Add fixes from 3.18.4 queue to fix i915 issues (rhbz 1183232)
- xhci: Check if slot is already in default state before moving it there (rhbz 1183289)

* Fri Jan 16 2015 Justin M. Forbes <jforbes@fedoraproject.org> - 3.18.3-200
- Linux v3.18.3

* Thu Jan 15 2015 Justin M. Forbes <jforbes@fedoraproject.org>
- Build fixes for big-endian arches

* Tue Jan 13 2015 Justin M. Forbes <jforbes@fedoraproject.org> - 3.18.2-200
- Linux v3.18.2

* Mon Jan 12 2015 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-9585 ASLR brute-force possible for vdso (rhbz 1181054 1181056)
- Backlight fixes for Samsung and Dell machines (rhbz 1094948 1115713 1163574)
- Add various UAS quirks (rhbz 1124119)
- Add patch to fix loop in VDSO (rhbz 1178975)

* Thu Jan 08 2015 Justin M. Forbes <jforbes@fedoraproject.org> - 3.17.8-300
- Linux v3.17.8

* Wed Jan 07 2015 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-9529 memory corruption or panic during key gc (rhbz 1179813 1179853)
- Enable POWERCAP and INTEL_RAPL

* Tue Jan 06 2015 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-9419 partial ASLR bypass through TLS base addr leak (rhbz 1177260 1177263)
- CVE-2014-9428 remote DoS via batman-adv (rhbz 1178826 1178833)
- Fix CIFS login issue (rhbz 1163927)

* Mon Dec 29 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Enable F2FS (rhbz 972446)

* Thu Dec 18 2014 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-8989 userns can bypass group restrictions (rhbz 1170684 1170688)
- Fix dm-cache crash (rhbz 1168434)
- Fix blk-mq crash on CPU hotplug (rhbz 1175261)

* Wed Dec 17 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Enable USBIP in modules-extra from Johnathan Dieter (rhbz 1169478)
- CVE-2014-XXXX isofs: infinite loop in CE record entries (rhbz 1175235 1175250)

* Tue Dec 16 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Linux v3.17.7
- CVE-2014-8559 deadlock due to incorrect usage of rename_lock (rhbz 1159313 1173814)
- Add patch from Josh Stone to restore var-tracking via Kconfig (rhbz 1126580)

* Mon Dec 15 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix ppc64 boot with smt-enabled=off (rhbz 1173806)
- CVE-2014-8133 x86: espfix(64) bypass via set_thread_area and CLONE_SETTLS (rhbz 1172797 1174374)

* Fri Dec 12 2014 Kyle McMartin <kyle@fedoraproject.org>
- build in ahci_platform on aarch64 temporarily.

* Fri Dec 12 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Remove pointless warning in cfg80211 (rhbz 1172543)

* Wed Dec 10 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix MSI issues on another Samsung pci-e SSD (rhbz 1084928)
- Fix UAS crashes with Seagate and Fresco Logic drives (rhbz 1164945)
- CVE-2014-8134 fix espfix for 32-bit KVM paravirt guests (rhbz 1172765 1172769)

* Mon Dec 08 2014 Justin M. Forbes <jforbes@fedoraproject.org> - 3.17.6-300
- Linux v3.17.6

* Fri Dec 05 2014 Kyle McMartin <kyle@fedoraproject.org> - 3.17.4-303
- arm64-fix-xgene_enet_process_ring.patch: fix a panic under load.

* Thu Dec 04 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.4-302
- CVE-2014-9090 local DoS via do_double_fault due to improper SS faults (rhbz 1170691)

* Thu Dec 04 2014 Kyle McMartin <kyle@fedoraproject.org>
- kernel-arm64.patch: update.
- arm64-force-serial-to-be-active-consdev.patch: force serial consoles
  to be the primary console device instead of defaulting to tty0. No
  changes to drivers outside of ARM-land.
- arm64-vgic-error-to-info.patch: change an error to a warning so that
  kvm will work.

* Mon Dec 01 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to quiet i915 driver on long hdps
- Add patch to fix oops when using xpad (rhbz 1094048)

* Thu Nov 27 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.4-301
- Add patch to fix radeon HDMI issues (rhbz 1167511)

* Mon Nov 24 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add quirk for Laser Mouse 6000 (rhbz 1165206)

* Fri Nov 21 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.4-300
- Linux v3.17.4
- Move TPM drivers to main kernel package (rhbz 1164937)

* Wed Nov 19 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.3-301
- Disable SERIAL_8250 on s390x (rhbz 1158848)

* Fri Nov 14 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.3-300
- Linux v3.17.3
- Quiet WARN in i915 edp VDD handling
- Enable I40EVF driver (rhbz 1164029)

* Thu Nov 13 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch for MS Surface Pro 3 Type Cover (rhbz 1135338)
- CVE-2014-7843 aarch64: copying from /dev/zero causes local DoS (rhbz 1163744 1163745)
- CVE-2014-7842 kvm: reporting emulation failures to userspace (rhbz 1163762 1163767)

* Wed Nov 12 2014 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-7841 sctp: NULL ptr deref on malformed packet (rhbz 1163087 1163095)

* Mon Nov 10 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.2-301
- Fix Samsung pci-e SSD handling on some macbooks (rhbz 1161805)
- Add patch to fix crypto allocation issues on PAGE_SIZE > 4k

* Fri Nov 07 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix iwlwifi oops (rhbz 1151836)
- CVE-2014-7826 CVE-2014-7825 insufficient syscall number validation in perf and ftrace subsystems (rhbz 1161565 1161572)

* Mon Nov 03 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix early ucode crash on 32-bit AMD machines (rhbz 1159592)

* Thu Oct 30 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.2-300
- Linux v3.17.2

* Tue Oct 28 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add quirk for rfkill on Yoga 3 machines (rhbz 1157327)

* Fri Oct 24 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.1-304.fc21
- CVE-2014-3610 kvm: noncanonical MSR writes (rhbz 1144883 1156543)
- CVE-2014-3611 kvm: PIT timer race condition (rhbz 1144878 1156537)
- CVE-2014-3646 kvm: vmx: invvpid vm exit not handled (rhbz 1144825 1156534)
- CVE-2014-8369 kvm: excessive pages un-pinning in kvm_iommu_map error path (rhbz 1156518 1156522)
- CVE-2014-8480 CVE-2014-8481 kvm: NULL pointer dereference during rip relative instruction emulation (rhbz 1156615 1156616)
- Add touchpad quirk for Fujitsu Lifebook A544/AH544 models (rhbz 1111138)

* Wed Oct 22 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.1-303
- CVE-2014-3688 sctp: remote memory pressure from excessive queuing (rhbz 1155745 1155751)
- CVE-2014-3687 sctp: panic on duplicate ASCONF chunks (rhbz 1155731 1155738)
- CVE-2014-3673 sctp: panic with malformed ASCONF chunks (rhbz 1147850 1155727)
- CVE-2014-3690 kvm: invalid host cr4 handling (rhbz 1153322 1155372)
- Add patch to fix synaptics forcepad issues (rhbz 1153381)
- Add patch to fix wifi on X550VB machines (rhbz 1089731)

* Fri Oct 17 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.1-302
- CVE-2014-8086 ext4: race condition (rhbz 1151353 1152608)

* Fri Oct 17 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.1-301
- Enable B43_PHY_G to fix b43 driver regression (rhbz 1152502)
- Add even more btrfs corruption/error fixes

* Wed Oct 15 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.1-300
- Linux v3.17.1
- Revert Btrfs ro snapshot commit that causes filesystem corruption

* Mon Oct 13 2014 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-7975 fs: umount DoS (rhbz 1151108 1152025)

* Sun Oct 12 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Enable CONFIG_I2C_DESIGNWARE_PCI (rhbz 1045821)

* Fri Oct 10 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add patches to fix elantech touchscreens (rhbz 1149509)
- CVE-2014-7970 VFS: DoS with USER_NS (rhbz 1151095 1151484)
- Drop doubly applied ACPI video quirk patches

* Wed Oct 08 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-301
- Add patch to fix ATA blacklist

* Tue Oct 07 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix GFS2 regression (from Bob Peterson)

* Mon Oct 06 2014 Kyle McMartin <kyle@fedoraproject.org>
- enable 64K pages on arm64... (presently) needed to boot on amd seattle
  platforms due to physical memory being unreachable.

* Mon Oct 06 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-300
- Linux v3.17

* Thu Sep 25 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.3-302
- Enable early microcode loading (rhbz 1083716)
- Bump prereq on dracut that defaults to early microcode

* Tue Sep 23 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix XPS 13 touchpad issue (rhbz 1123584)

* Mon Sep 22 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix i2c-hid touchpad resume (rhbz 1143812)

* Wed Sep 17 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.3-300
- Linux v3.16.3

* Mon Sep 15 2014 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-6410 udf: avoid infinite loop on indirect ICBs (rhbz 1141809 1141810)
- CVE-2014-3186 HID: memory corruption via OOB write (rhbz 1141407 1141410)

* Fri Sep 12 2014 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-3181 HID: OOB write in magicmouse driver (rhbz 1141173 1141179)

* Thu Sep 11 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add support for touchpad in Asus X450 and X550 (rhbz 1110011)

* Wed Sep 10 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.2-301
- CVE-2014-3631 Add patch to fix oops on keyring gc (rhbz 1116347)

* Mon Sep  8 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Build tools on ppc64le (rhbz 1138884)
- Some minor ppc64 cleanups

* Fri Sep 05 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.2-300
- Linux v3.16.2

* Thu Sep 04 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add support for Wacom Cintiq Companion from Benjamin Tissoires (rhbz 1134969)

* Tue Sep 02 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Remove with_extra switch

* Thu Aug 28 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix NFSv3 ACL regression (rhbz 1132786)
- Don't enable CONFIG_DEBUG_WW_MUTEX_SLOWPATH (rhbz 1114160)

* Wed Aug 27 2014 Justin M. Forbes <jforbes@fedoraproject.org>
- CVE-2014-{5471,5472} isofs: Fix unbounded recursion when processing relocated
  directories (rhbz 1134099 1134101)

* Wed Aug 27 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Disable streams on via XHCI (rhbz 1132666)

* Tue Aug 26 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor generic ARMv7 updates
- Build tegra on both LPAE and general ARMv7 kernels (thank srwarren RHBZ 1110963)
- Set CMA to 64mb on LPAE kernel (RHBZ 1127000)

* Fri Aug 22 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.1-301
- Drop userns revert patch (rhbz 917708)

* Tue Aug 19 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix NFSv3 oops (rhbz 1131551)

* Fri Aug 15 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- ARM updates for 3.16
- Cleanup some old removed options
- Disable legacy USB OTG (using new configfs equivilents)
- Upstream patch to fix display on qemu (VExpress A9)

* Thu Aug 14 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.1-300
- Linux v3.16.1

* Thu Aug 14 2014 Hans de Goede <hdegoede@redhat.com>
- Blacklist usb bulk streams on Etron EJ168 xhci controllers (rhbz#1121288)
- UAS: Limit max number of requests over USB-2 to 32 (rhbz#1128472)

* Wed Aug 13 2014 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-{5206,5207} ro bind mount bypass with namespaces (rhbz 1129662 1129669)

* Mon Aug 04 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-1
- Linux v3.16
- Disable debugging options.

* Sun Aug  3 2014 Peter Robinson <pbrobinson@redhat.com>
- Minor config updates for Armada and Sunxi ARM devices

* Fri Aug 01 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc7.git4.1
- Linux v3.16-rc7-84-g6f0928036bcb

* Thu Jul 31 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc7.git3.1
- Linux v3.16-rc7-76-g3a1122d26c62

* Wed Jul 30 2014 Kyle McMartin <kyle@fedoraproject.org>
- kernel-arm64.patch: fix up merge conflict and re-enable

* Wed Jul 30 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc7.git2.1
- Linux v3.16-rc7-64-g26bcd8b72563
- Temporarily disable aarch64patches

* Wed Jul 30 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Apply different patch from Milan Broz to fix LUKS partitions (rhbz 1115120)

* Tue Jul 29 2014 Kyle McMartin <kyle@fedoraproject.org>
- kernel-arm64.patch: update from upstream git.

* Tue Jul 29 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc7.git1.1
- Linux v3.16-rc7-7-g31dab719fa50
- Reenable debugging options.

* Mon Jul 28 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Make sure acpi brightness_switch is disabled (like forever in Fedora)
- CVE-2014-5077 sctp: fix NULL ptr dereference (rhbz 1122982 1123696)

* Mon Jul 28 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc7.git0.1
- Linux v3.16-rc7
- Disable debugging options.

* Mon Jul 28 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Add patch to fix loading of tegra drm using device tree

* Sat Jul 26 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc6.git3.1
- Linux v3.16-rc6-139-g9c5502189fa0

* Fri Jul 25 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc6.git2.1
- Linux v3.16-rc6-118-g82e13c71bc65
- Fix selinux sock_graft hook for AF_ALG address family (rhbz 1115120)

* Thu Jul 24 2014 Kyle McMartin <kyle@fedoraproject.org>
- kernel-arm64.patch: update from upstream git.
- arm64: update config-arm64 to include PCI support.

* Thu Jul 24 2014 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-5045 vfs: refcount issues during lazy umount on symlink (rhbz 1122471 1122482)
- Fix regression in sched_setparam (rhbz 1117942)

* Tue Jul 22 2014 Justin M. Forbes <jforbes@fedoraproject.org> - 3.16.0-0.rc6.git1.1
- Linux v3.16-rc6-75-g15ba223
- Reenable debugging options.

* Mon Jul 21 2014 Justin M. Forbes <jforbes@fedoraproject.org> - 3.16.0-0.rc6.git0.1
- Linux v3.16-rc6
- Disable debugging options.

* Mon Jul 21 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARMv7 config update

* Thu Jul 17 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc5.git2.1
- Linux v3.16-rc5-143-gb6603fe574af

* Wed Jul 16 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Enable hermes prism driver (rhbz 1120393)

* Wed Jul 16 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc5.git1.1
- Linux v3.16-rc5-130-g2da294474093
- Reenable debugging options.

* Mon Jul 14 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc5.git0.1
- Linux v3.16-rc5
- Fix i915 regression with external monitors (rhbz 1117008)
- Disable debugging options.

* Sat Jul 12 2014 Tom Callaway <spot@fedoraproject.org>
- Fix license handling (I hope)

* Fri Jul 11 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc4.git3.1
- Linux v3.16-rc4-120-g85d90faed31e

* Thu Jul 10 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Rebase Utilute and BeagleBone patches
- Minor ARM updates
- Enable ISL12057 RTC for ARM (NetGear ReadyNAS)

* Wed Jul 09 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc4.git2.1
- Linux v3.16-rc4-28-g163e40743f73
- Fix bogus vdso .build-id links (rhbz 1117563)

* Tue Jul 08 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc4.git1.1
- Linux v3.16-rc4-20-g448bfad8a185
- Reenable debugging options.

* Sun Jul 06 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc4.git0.1
- Linux v3.16-rc4
- Disable debugging options.

* Fri Jul 04 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc3.git3.1
- Linux v3.16-rc3-149-g034a0f6b7db7

* Wed Jul 02 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc3.git2.1
- Linux v3.16-rc3-62-gd92a333a65a1
- Add patch to fix virt_blk oops (rhbz 1113805)

* Wed Jul 02 2014 Kyle McMartin <kyle@fedoraproject.org>
- arm64: build-in ahci, ethernet, and rtc drivers.

* Tue Jul 01 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc3.git1.1
- Linux v3.16-rc3-6-g16874b2cb867
- Reenable debugging options.

* Tue Jul  1 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARMv7 cleanup

* Mon Jun 30 2014 Kyle McMartin <kyle@fedoraproject.org>
- kernel-arm64.patch, update from git.

* Mon Jun 30 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc3.git0.1.1
- Linux v3.16-rc3
- Enable USB rtsx drivers (rhbz 1114229)
- Disable debugging options.

* Fri Jun 27 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc2.git4.1
- Linux v3.16-rc2-222-g3493860c76eb

* Fri Jun 27 2014 Hans de Goede <hdegoede@redhat.com>
- Add patch to fix wifi on lenove yoga 2 series (rhbz#1021036)

* Thu Jun 26 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Enable rtl8192ee (rhbz 1113422)

* Thu Jun 26 2014 Kyle McMartin <kyle@fedoraproject.org> - 3.16.0-0.rc2.git3.2
- Add kernel-arm64.patch, which contains AArch64 support destined for upstream.
  ssh://git.fedorahosted.org/git/kernel-arm64.git is Mark Salter's source tree
  integrating these patches on the devel branch. I've added a twiddle to the
  top of the spec file to disable the aarch64 patchset, and also set aarch64
  to nobuildarches, so we still get kernel-headers, but no one accidentally
  installs a non-booting kernel if the patchset causes rejects during a
  rebase.

* Thu Jun 26 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Trimmed changelog, see fedpkg git for earlier history.

* Thu Jun 26 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc2.git3.1
- Linux v3.16-rc2-211-gd7933ab727ed

* Wed Jun 25 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc2.git2.1
- Linux v3.16-rc2-69-gd91d66e88ea9

* Wed Jun 25 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Revert commit that breaks Wacom Intuos4 from Benjamin Tissoires

* Tue Jun 24 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc2.git1.1
- Linux v3.16-rc2-35-g8b8f5d971584
- Reenable debugging options.

* Mon Jun 23 2014 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-4508 BUG in x86_32 syscall auditing (rhbz 1111590 1112073)

* Mon Jun 23 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc2.git0.1
- Linux v3.16-rc2
- Disable debugging options.

* Sun Jun 22 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable Exynos now it's finally multi platform capable
- Minor TI Keystone update
- ARM config cleanups

* Fri Jun 20 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Bring in intel_pstate regression fixes for BayTrail (rhbz 1111920)

* Fri Jun 20 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc1.git4.1
- Linux v3.16-rc1-215-g3c8fb5044583

* Thu Jun 19 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc1.git3.1
- Linux v3.16-rc1-112-g894e552cfaa3

* Thu Jun 19 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Add missing bits for NVIDIA Jetson TK1 (thanks Stephen Warren)

* Wed Jun 18 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc1.git2.1
- Linux v3.16-rc1-17-ge99cfa2d0634

* Tue Jun 17 2014 Dennis Gilmore <dennis@ausil.us>
- when ipuv3 moved out of staging the config was renamed
- adjust the config to suit

* Tue Jun 17 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc1.git1.1
- Linux v3.16-rc1-2-gebe06187bf2a
- Reenable debugging options.

* Mon Jun 16 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable Qualcomm SoCs on ARM

* Mon Jun 16 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc1.git0.1
- Linux v3.16-rc1
- Disable debugging options.

* Mon Jun 16 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- ARM config updates for 3.16

* Sat Jun 14 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc0.git11.1
- Linux v3.15-9930-g0e04c641b199
- Enable CONFIG_RCU_NOCB_CPU(_ALL) (rbhz 1109113)

* Fri Jun 13 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Add patch to fix build failure on aarch64

* Fri Jun 13 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc0.git10.1
- Linux v3.15-9837-g682b7c1c8ea8

* Fri Jun 13 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc0.git9.1
- Linux v3.15-8981-g5c02c392cd23

* Fri Jun 13 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc0.git8.1
- Linux v3.15-8835-g859862ddd2b6

* Fri Jun 13 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc0.git7.1
- Linux v3.15-8556-gdfb945473ae8

* Fri Jun 13 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc0.git6.1
- Linux v3.15-8351-g9ee4d7a65383

* Thu Jun 12 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc0.git5.1
- Linux v3.15-8163-g5b174fd6472b

* Thu Jun 12 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc0.git4.1
- Linux v3.15-7926-gd53b47c08d8f

* Thu Jun 12 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc0.git3.1
- Linux v3.15-7378-g14208b0ec569

* Wed Jun 11 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc0.git2.1
- Linux v3.15-7283-gda85d191f58a

* Tue Jun 10 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc0.git1.1
- Linux v3.15-7218-g3f17ea6dea8b
- Reenable debugging options.

* Mon Jun 09 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-1
- Linux v3.15
- Disable debugging options.

* Mon Jun  9 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable USB_EHCI_HCD_ORION to fix USB on Marvell (fix boot for some devices)

* Fri Jun 06 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc8.git4.1
- CVE-2014-3940 missing check during hugepage migration (rhbz 1104097 1105042)
- Linux v3.15-rc8-81-g951e273060d1

* Thu Jun 05 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc8.git3.1
- Linux v3.15-rc8-72-g54539cd217d6

* Wed Jun 04 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc8.git2.1
- Linux v3.15-rc8-58-gd2cfd3105094

* Tue Jun 03 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add filter-ppc64p7.sh because ppc64p7 is an entirely separate RPM arch

* Tue Jun 03 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc8.git1.2
- Fixes from Hans de Goede for backlight and platform drivers on various
  machines.  (rhbz 1025690 1012674 1093171 1097436 861573)

* Tue Jun 03 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc8.git1.1
- Add patch to install libtraceevent plugins from Kyle McMartin
- Linux v3.15-rc8-53-gcae61ba37b4c
- Reenable debugging options.

* Mon Jun  2 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM MMC config updates

* Mon Jun 02 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc8.git0.1
- Linux v3.15-rc8
- Disable debugging options.

* Sat May 31 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc7.git4.2
- Add patch to fix dentry lockdep splat

* Sat May 31 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc7.git4.1
- Linux v3.15-rc7-102-g1487385edb55

* Fri May 30 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc7.git3.1
- Linux v3.15-rc7-79-gfe45736f4134
- Disable CARL9170 on ppc64le

* Thu May 29 2014 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-3917 DoS with syscall auditing (rhbz 1102571 1102715)

* Wed May 28 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc7.git2.1
- Linux v3.15-rc7-53-g4efdedca9326

* Wed May 28 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc7.git1.1
- Linux v3.15-rc7-40-gcd79bde29f00
- Reenable debugging options.

* Mon May 26 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc7.git0.1
- Linux v3.15-rc7
- Disable debugging options.

* Sun May 25 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc6.git1.1
- Linux v3.15-rc6-213-gdb1003f23189
- Reenable debugging options.

* Thu May 22 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Enable CONFIG_R8723AU (rhbz 1100162)

* Thu May 22 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc6.git0.1
- Linux v3.15-rc6
- Disable debugging options.

* Wed May 21 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc5.git4.1
- Linux v3.15-rc5-270-gfba69f042ad9

* Tue May 20 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc5.git3.1
- Linux v3.15-rc5-157-g60b5f90d0fac

* Mon May 19 2014 Dan Horák <dan@danny.cz>
- kernel metapackage shouldn't depend on subpackages we don't build

* Thu May 15 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc5.git2.9
- Fix build fail on s390x

* Wed May 14 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc5.git2.8
- Enable autoprov for kernel module Provides (rhbz 1058331)
- Enable xz compressed modules (from Kyle McMartin)

* Tue May 13 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Don't try and merge local config changes on arches we aren't building

* Tue May 13 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc5.git2.1
- Linux v3.15-rc5-77-g14186fea0cb0

* Mon May 12 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc5.git1.1
- Linux v3.15-rc5-9-g7e338c9991ec
- Reenable debugging options.

* Sat May 10 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable Marvell Dove support
- Minor ARM cleanups
- Disable some unneed drivers on ARM

* Sat May 10 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc5.git0.1
- Linux v3.15-rc5
- Disable debugging options.

* Fri May 09 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Move isofs to kernel-core

* Fri May 09 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc4.git4.1
- Linux v3.15-rc4-320-gafcf0a2d9289

* Thu May 08 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc4.git3.1
- Linux v3.15-rc4-298-g9f1eb57dc706

* Wed May 07 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc4.git2.1
- Linux v3.15-rc4-260-g38583f095c5a

* Tue May 06 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc4.git1.1
- Linux v3.15-rc4-202-g30321c7b658a
- Reenable debugging options.

* Mon May  5 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Fix some USB on ARM LPAE kernels

* Mon May 05 2014 Kyle McMartin <kyle@fedoraproject.org>
- Install arch/arm/include/asm/xen headers on aarch64, since the headers in
  arch/arm64/include/asm/xen reference them.

* Mon May 05 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc4.git0.1
- Linux v3.15-rc4
- Disable debugging options.

* Mon May  5 2014 Hans de Goede <hdegoede@redhat.com>
- Add use_native_brightness quirk for the ThinkPad T530 (rhbz 1089545)

* Sun May  4 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- General minor ARM cleanups

* Sun May 04 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix k-m-e requires on k-m-uname-r provides
- ONE MORE TIME WITH FEELING

* Sat May  3 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Disable OMAP-3 boards (use DT) and some minor omap3 config updates

* Sat May 03 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc3.git5.1
- Linux v3.15-rc3-159-g6c6ca9c2a5b9

* Sat May 03 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix HID rmi driver from Benjamin Tissoires (rhbz 1090161)

* Sat May 03 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix up Provides on kernel-module variant packages
- Enable CONFIG_USB_UAS unconditionally per Hans

* Fri May 02 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc3.git4.1
- Linux v3.15-rc3-121-gb7270cce7db7

* Thu May 01 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Rename kernel-drivers to kernel-modules
- Add kernel metapackages for all flavors, not just debug

* Thu May  1 2014 Hans de Goede <hdegoede@redhat.com>
- Add use_native_backlight quirk for 4 laptops (rhbz 983342 1093120)

* Wed Apr 30 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc3.git3.1
- Linux v3.15-rc3-82-g8aa9e85adac6

* Wed Apr 30 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add kernel-debug metapackage when debugbuildsenabled is set

* Wed Apr 30 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc3.git2.1
- Linux v3.15-rc3-62-ged8c37e158cb
- Drop noarch from ExclusiveArch.  Nothing is built as noarch

* Tue Apr 29 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc3.git1.10
- Make depmod call fatal if it errors or warns

* Tue Apr 29 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Introduce kernel-core/kernel-drivers split for F21 Feature work

* Tue Apr 29 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc3.git1.1
- Linux v3.15-rc3-41-g2aafe1a4d451
- Reenable debugging options.

* Mon Apr 28 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc3.git0.1
- Linux v3.15-rc3
- Disable debugging options.

* Fri Apr 25 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Drop obsolete ARM LPAE patches

* Fri Apr 25 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch from Will Woods to fix fanotify EOVERFLOW issue (rhbz 696821)
- Fix ACPI issue preventing boot on AMI firmware (rhbz 1090746)

* Fri Apr 25 2014 Hans de Goede <hdegoede@redhat.com>
- Add synaptics min-max quirk for ThinkPad Edge E431 (rhbz#1089689)

* Fri Apr 25 2014 Hans de Goede <hdegoede@redhat.com>
- Add a patch to add support for the mmc controller on sunxi ARM SoCs

* Thu Apr 24 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc2.git3.1
- Linux v3.15-rc2-107-g76429f1dedbc

* Wed Apr 23 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc2.git2.1
- Linux v3.15-rc2-69-g1aae31c8306e

* Tue Apr 22 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc2.git1.1
- Linux v3.15-rc2-42-g4d0fa8a0f012
- Reenable debugging options.

* Tue Apr 22 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix Synaptics touchscreens and HID rmi driver (rhbz 1089583)

* Mon Apr 21 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc2.git0.1
- Linux v3.15-rc2
- Disable debugging options.

* Fri Apr 18 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc1.git4.1
- Linux v3.15-rc1-137-g81cef0fe19e0

* Thu Apr 17 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc1.git3.1
- Linux v3.15-rc1-113-g6ca2a88ad820
- Build perf with unwind support via libdw (rhbz 1025603)

* Thu Apr 17 2014 Hans de Goede <hdegoede@redhat.com>
- Update min/max quirk patch to add a quirk for the ThinkPad L540 (rhbz1088588)

* Thu Apr 17 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Drop OMAP DRM hack to load encoder module now it fully supports DT (YAY!)

* Wed Apr 16 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc1.git2.1
- Linux v3.15-rc1-49-g10ec34fcb100

* Tue Apr 15 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc1.git1.1
- Linux v3.15-rc1-12-g55101e2d6ce1
- Reenable debugging options.

* Mon Apr 14 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc1.git0.1
- Linux v3.15-rc1
- Disable debugging options.
- Turn SLUB_DEBUG off

* Mon Apr 14 2014 Hans de Goede <hdegoede@redhat.com>
- Add min/max quirks for various new Thinkpad touchpads (rhbz 1085582 1085697)

* Mon Apr 14 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config changes and cleanups for 3.15 merge window

* Mon Apr 14 2014 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-2851 net ipv4 ping refcount issue in ping_init_sock (rhbz 1086730 1087420)

* Sun Apr 13 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git13.1
- Linux v3.14-12812-g321d03c86732

* Fri Apr 11 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git12.1
- Linux v3.14-12380-g9e897e13bd46
- Add queued urgent efi fixes (rhbz 1085349)

* Thu Apr 10 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git11.1
- Linux v3.14-12376-g4ba85265790b

* Thu Apr 10 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Backported HID RMI driver for Haswell Dell XPS machines from Benjamin Tissoires (rhbz 1048314)

* Wed Apr 09 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git10.1
- Linux v3.14-12042-g69cd9eba3886

* Wed Apr 09 2014 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-0155 KVM: BUG caused by invalid guest ioapic redirect table (rhbz 1081589 1085016)

* Thu Apr 03 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git9.1
- Linux v3.14-7333-g59ecc26004e7

* Thu Apr 03 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git8.1
- Linux v3.14-7247-gcd6362befe4c

* Wed Apr 02 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git7.1
- Linux v3.14-5146-g0f1b1e6d73cb

* Wed Apr 02 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git6.1
- Linux v3.14-4600-g467cbd207abd

* Wed Apr 02 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git5.1
- Linux v3.14-4555-gb33ce4429938

* Wed Apr 02 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git4.1
- Linux v3.14-4227-g3e75c6de1ac3

* Wed Apr 02 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git3.1
- Linux v3.14-3893-gc12e69c6aaf7

* Tue Apr 01 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git2.1
- CVE-2014-2678 net: rds: deref of NULL dev in rds_iw_laddr_check (rhbz 1083274 1083280)

* Tue Apr 01 2014 Josh Boyer <jwboyer@fedoraproject.org> 
- Linux v3.14-751-g683b6c6f82a6

* Tue Apr 01 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git1.1
- Linux v3.14-313-g918d80a13643
- Reenable debugging options.
- Turn on SLUB_DEBUG

* Mon Mar 31 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-1
- Linux v3.14
- Disable debugging options.

* Mon Mar 31 2014 Hans de Goede <hdegoede@redhat.com>
- Fix clicks getting lost with cypress_ps2 touchpads with recent
  xorg-x11-drv-synaptics versions (bfdo#76341)

* Fri Mar 28 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc8.git1.1
- CVE-2014-2580 xen: netback crash trying to disable due to malformed packet (rhbz 1080084 1080086)
- CVE-2014-0077 vhost-net: insufficent big packet handling in handle_rx (rhbz 1064440 1081504)
- CVE-2014-0055 vhost-net: insufficent error handling in get_rx_bufs (rhbz 1062577 1081503)
- CVE-2014-2568 net: potential info leak when ubuf backed skbs are zero copied (rhbz 1079012 1079013)

* Fri Mar 28 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Linux v3.14-rc8-12-g75c5a52
- Reenable debugging options.

* Fri Mar 28 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable Tegra 114/124 SoCs
- Re-enable OMAP cpufreq
- Re-enable CPSW PTP option

* Thu Mar 27 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Switch to CONFIG_TRANSPARENT_HUGEPAGE_MADVISE instead of always on

* Tue Mar 25 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc8.git0.1
- Linux v3.14-rc8
- Disable debugging options.

* Mon Mar 24 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Update some generic ARM config options
- Build in TPS65217 for ARM non lpae kernels (fixes BBW booting)

* Fri Mar 21 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc7.git2.1
- Linux v3.14-rc7-59-g08edb33

* Wed Mar 19 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc7.git1.1
- Linux v3.14-rc7-26-g4907cdc
- Reenable debugging options.

* Tue Mar 18 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Enable TEGRA_FBDEV (rhbz 1073960)

* Mon Mar 17 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add bootwrapper for ppc64le

* Mon Mar 17 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc7.git0.1
- Linux v3.14-rc7
- Disable debugging options.

* Mon Mar 17 2014 Peter Robinson <pbrobinson@fedoraproject.org> 
- Build in Palmas regulator on ARM to fix ext MMC boot on OMAP5

* Fri Mar 14 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc6.git4.1
- Linux v3.14-rc6-133-gc60f7d5

* Thu Mar 13 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc6.git3.1
- Linux v3.14-rc6-41-gac9dc67

* Wed Mar 12 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc6.git2.1
- Fix locking issue in iwldvm (rhbz 1046495)
- Linux v3.14-rc6-26-g33807f4

* Wed Mar 12 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Add some general missing ARM drivers (mostly sound)
- ARM config tweaks and cleanups
- Update i.MX6 dtb

* Tue Mar 11 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc6.git1.1
- CVE-2014-2309 ipv6: crash due to router advertisment flooding (rhbz 1074471 1075064)
- Linux v3.14-rc6-17-g8712a00
- Reenable debugging options.

* Mon Mar 10 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc6.git0.1
- Linux v3.14-rc6
- Disable debugging options.

* Fri Mar 07 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Revert two xhci fixes that break USB mass storage (rhbz 1073180)

* Thu Mar 06 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix stale EC events on Samsung systems (rhbz 1003602)
- Add ppc64le support from Brent Baude (rhbz 1073102)
- Fix depmod error message from hci_vhci module (rhbz 1051748)
- Fix bogus WARN in iwlwifi (rhbz 1071998)

* Wed Mar 05 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc5.git2.1
- Linux v3.14-rc5-185-gc3bebc7

* Tue Mar 04 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc5.git1.1
- Linux v3.14-rc5-43-g0c0bd34
- Reenable debugging options.

* Mon Mar 03 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc5.git0.1
- Linux v3.14-rc5
- Disable debugging options.

* Fri Feb 28 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc4.git3.1
- Linux v3.14-rc4-78-gd8efcf3

* Fri Feb 28 2014 Kyle McMartin <kyle@fedoraproject.org>
- Enable appropriate CONFIG_XZ_DEC_$arch options to ensure we can mount
  squashfs images on supported architectures.

* Fri Feb 28 2014 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-0102 keyctl_link can be used to cause an oops (rhbz 1071396)

* Thu Feb 27 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc4.git2.1
- Linux v3.14-rc4-45-gd2a0476

* Wed Feb 26 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc4.git1.1
- Linux v3.14-rc4-34-g6dba6ec
- Reenable debugging options.

* Wed Feb 26 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Re-enable KVM on aarch64 now it builds again

* Tue Feb 25 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix mounting issues on cifs (rhbz 1068862)

* Mon Feb 24 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix lockdep issue in EHCI when using threaded IRQs (rhbz 1056170)

* Mon Feb 24 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc4.git0.1
- Linux v3.14-rc4
- Disable debugging options.

* Thu Feb 20 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc3.git5.1
- Linux v3.14-rc3-219-gd158fc7

* Thu Feb 20 2014 Kyle McMartin <kyle@fedoraproject.org>
- armv7: disable CONFIG_DEBUG_SET_MODULE_RONX until debugged (rhbz#1067113)

* Thu Feb 20 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc3.git4.1
- Linux v3.14-rc3-184-ge95003c

* Wed Feb 19 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc3.git3.1
- Linux v3.14-rc3-168-g960dfc4

* Tue Feb 18 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc3.git2.1
- Linux v3.14-rc3-43-g805937c

* Tue Feb 18 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc3.git1.1
- Linux v3.14-rc3-20-g60f76ea
- Reenable debugging options.
- Fix r8169 ethernet after suspend (rhbz 1054408)
- Enable INTEL_MIC drivers (rhbz 1064086)

* Mon Feb 17 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc3.git0.1
- Linux v3.14-rc3
- Disable debugging options.
- Enable CONFIG_PPC_DENORMALIZATION (from Tony Breeds)

* Fri Feb 14 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc2.git4.1
- Linux v3.14-rc2-342-g5e57dc8
- CVE-2014-0069 cifs: incorrect handling of bogus user pointers (rhbz 1064253 1062578)

* Thu Feb 13 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc2.git3.1
- Linux v3.14-rc2-271-g4675348

* Wed Feb 12 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc2.git2.1
- Linux v3.14-rc2-267-g9398a10

* Wed Feb 12 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix cgroup destroy oops (rhbz 1045755)
- Fix backtrace in amd_e400_idle (rhbz 1031296)

* Tue Feb 11 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc2.git1.1
- Linux v3.14-rc2-26-g6792dfe
- Reenable debugging options.

* Mon Feb 10 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc2.git0.1
- Linux v3.14-rc2
- Disable debugging options.

* Sun Feb  9 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable CMA on aarch64
- Disable KVM temporarily on aarch64
- Minor ARM config updates and cleanups

* Sun Feb 09 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc1.git5.1.1
- Linux v3.14-rc1-182-g4944790

* Sat Feb 08 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc1.git4.1
- Linux v3.14-rc1-150-g34a9bff

* Fri Feb 07 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc1.git3.1
- Linux v3.14-rc1-86-g9343224

* Thu Feb 06 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc1.git2.1
- Linux v3.14-rc1-54-gef42c58

* Wed Feb 05 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc1.git1.1
- Linux v3.14-rc1-13-g878a876

* Tue Feb 04 2014 Kyle McMartin <kyle@fedoraproject.org>
- Fix %all_arch_configs on aarch64.

* Tue Feb 04 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc1.git0.2
- Add NUMA oops patches
- Reenable debugging options.

* Mon Feb 03 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc1.git0.1
- Linux v3.14-rc1
- Disable debugging options.
- Disable Xen on ARM temporarily as it doesn't build

* Mon Feb  3 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Re-enable modular Tegra DRM driver
- Add SD driver for ZYNQ SoCs

* Fri Jan 31 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git19.1
- Linux v3.13-10637-ge7651b8
- Enable ZRAM/ZSMALLOC (rhbz 1058072)
- Turn EXYNOS_HDMI back on now that it should build

* Thu Jan 30 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git18.1
- Linux v3.13-10231-g53d8ab2

* Thu Jan 30 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git17.1
- Linux v3.13-10094-g9b0cd30
- Add patches to fix imx-hdmi build, and fix kernfs lockdep oops (rhbz 1055105)

* Thu Jan 30 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git16.1
- Linux v3.13-9240-g1329311

* Wed Jan 29 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git15.1
- Linux v3.13-9218-g0e47c96

* Tue Jan 28 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git14.1
- Linux v3.13-8905-g627f4b3

* Tue Jan 28 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git13.1
- Linux v3.13-8789-g54c0a4b
- Enable CONFIG_CC_STACKPROTECTOR_STRONG on x86

* Mon Jan 27 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Build AllWinner (sunxi) on LPAE too (Cortex-A7 supports LPAE/KVM)

* Mon Jan 27 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git12.1
- Linux v3.13-8631-gba635f8

* Mon Jan 27 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git11.1
- Linux v3.13-8598-g77d143d

* Sat Jan 25 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git10.1
- Linux v3.13-8330-g4ba9920

* Sat Jan 25 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git9.1
- Linux v3.13-6058-g2d08cd0
- Quiet incorrect usb phy error (rhbz 1057529)

* Sat Jan 25 2014 Ville Skyttä <ville.skytta@iki.fi>
- Own the /lib/modules dir.

* Sat Jan 25 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Initial ARM config updates for 3.14
- Disable highbank cpuidle driver
- Enable mtd-nand drivers on ARM
- Update CPU thermal scaling options for ARM

* Fri Jan 24 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git8.1
- Linux v3.13-5617-g3aacd62

* Thu Jan 23 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git7.1
- Linux v3.13-4156-g90804ed

* Thu Jan 23 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git6.1.1
- Revert fsnotify changes as they cause slab corruption for multiple people
- Linux v3.13-3995-g0dc3fd0

* Thu Jan 23 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git5.1
- Linux v3.13-3667-ge1ba845

* Wed Jan 22 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git4.1
- Linux v3.13-3477-gdf32e43

* Wed Jan 22 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git3.1
- Linux v3.13-3260-g03d11a0

* Wed Jan 22 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git2.1
- Linux v3.13-2502-gec513b1

* Tue Jan 21 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git1.1
- Linux v3.13-737-g7fe67a1
- Reenable debugging options.  Enable SLUB_DEBUG

* Mon Jan 20 2014 Kyle McMartin <kyle@fedoraproject.org>
- Enable CONFIG_KVM on AArch64.

* Mon Jan 20 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-1
- Linux v3.13
- Disable debugging options.
- Use versioned perf man pages tarball
###
# The following Emacs magic makes C-c C-e use UTC dates.
# Local Variables:
# rpm-change-log-uses-utc: t
# End:
###
