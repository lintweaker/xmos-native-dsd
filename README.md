Linux native DSD playback support
=================================
[23-Jan-17]<br>
<br>
Fix Singxer F-1 converter board patch<br>
<br>
[02-Dec-16]<br>
<br>
Add support for Audiolab M-DAC+<br>
<br>
[30-Nov-16]<br>
<br>
Add seperate patch for Amanero Combo384 BE sample format support
Rename original Amanero patch<br>
<br>
[22-Oct-16]<br>
<br>
Add support for the CH Precision C1 DAC<br>
Add support for the Singxer F-1 converter board<br>
<br>
[30-Aug-16]<br>
<br>
Add support for Bryston BDA3<br>
<br>
[28-Aug-16]<br>
<br>
Add support for the Engineered Electronics Stereo Playback Interface<br>
<br>
[21-Aug-16]<br>
<br>
Add support for Holo Springs Level 3 R2R DAC<br>
<br>
[30-Jul-16]<br>
<br>
Add support for MSB Technology<br>
Add support for LH Labs VI DAC Inifinity<br>
<br>
[12-Jun-16]

Support for WaveIO USB Audio 2.0 cards.


[05-Jun-16]

Experimental support for Soekris 'dac1101'.


[27-May-16]

Update/extend native DSD support for Playback Design


[16-May-16]

Add experimental support for:
- LH Labs Geek Pulse X Inifinity 2V0
- LH Labs Geek Out 1V5
- NuPrime IDA-8
- Eastern Electric MiniMax Tube DAC Supreme

Moved TEAC-501 patch to archive. Patch was close but not sufficient.<br>
Investigation not complete due to lack of (access to) a TEAC-501.


[29-apr-16]

Add experimental support for TEAC UD-501 and support for the NuPrime Audio
HD-AVP/AVA.


[11-apr-16]

Add support for Matrix Audio Quattro II<br>
Experimental support for NuPrime Audio DAC-9


[30-mar-16]

Updated patch for Amanero Combo384. Requires at least firmware 1099rc2

[12-mar-16]

Add experimental suppor for the Unison Research Unico CD Due.


[04-mar-16]

Added experimental support for the Amanero Combo384.
Firmware 1099rc1 is needed (see Amanero site). [Update: waiting for firmware
update, rc1 does not work correctly]

[13-feb-16]

Added experimental support for:

Mytek Brooklyn DAC and NuPrime DAC-10H


[29-jan-16]

Support for PS Audio NuWave DAC confirmed to work.
New patch for Oppo HA-2.


[19-jan-16]

Experimental support for Auralice Vega. This patch also fixes a type in the code
for the W4S DAC-2.

New patch for the W4S DAC-2.


[17-jan-16]

Experimental support for the PS Audio NuWave DAC.

[16-jan-16]

Experimental support for Wyred 4 Sound DAC-2 DSD. Needs firmware update.
Oppo HA-1 support will land in kernel 4.5.

[25-nov-15]

Experimental support for Oppo HA-1

[23-nov-15]

Hegel patch moved to archive. DSD support does not work.

[09-nov-15]

Add support for Aune X1S and experimental support for Hegel HD12 DSD

[21-aug-15]

Add support for Gustard DAC-X20U

[29-may-15]

Added support for JLsounds I2SoverUSB

[28-mar-15]

With kernel 3.19.1 and up all needed DSD support and native DSD device patches
are included in the mainline kernel.

[21-feb-15]

Update to kernel 3.18.7 for Fedora 21.
Support added for Denon DA300-USB (per kernel bugzilla #93261)

[31-jan-15]

SRPMs and patches for Fedora 21.

[28-nov-14]

Support for Denon/Marantz HiFi devices with USB DACs added.<br>
Kernel updated and added kernel patches.

[24-nov-14]

DSD sampleformat for 32-bit samples changed to DSD_U32_BE.<br>
ALSA, MPD and kernel packages and patches updated.<br>
New kernel 3.17.4<br>

[19-nov-14]

news: native DSD support now working for Marantz/Denon DACs.

Although not XMOS based, recent Denon en Marantz CD/SACD players and DACs also
support native DSD playback using a 32-bit sample format.
The following device will be supported shortly:
- Marantz SA-14S1
- Marantz HD-DAC1

Stay tuned.

## Native DSD support for XMOS based devices
XMOS based USB DACs and converters can support native DSD playback using a
32-bit sample format. DACs that support this feature expose it using a *Alternate Setting* on the USB interface.

On Windows systems this feature can be used with a ASIO 2.1/2.2 driver from the DAC manufacturer.

I have added a new DSD sample format to ALSA and the Linux kernel (DSD_U32_LE) to support it on Linux and added the needed *quirks* to support it for a few XMOS based USB DACs/boards.

Currently native DSD playback on Linux is supported for the following XMOS based DACs/USB converters:

- iFi Audio micro iDSD [max DSD512]
- iFi Audio nano iDSD [max DSD256, with latest 4.04 firmware]
- DIYINHK USB to I2S/DSD converter [max DSD128]
- ..more to follow

#### ALSA support status:
- New DSD sample format accepted, code resides in ALSA development git
- Will be generally available with the next ALSA release (1.0.29)

#### Kernel support status:
- Kernel 3.18rc1 contains the needed new sample format support
- Kernel 3.18rc1 supports the iFi Audio and DIYINKHK devices

#### Linux Playback support:
- python scripts [python-dsd-tools] (https://github.com/lintweaker/python-dsd-tools)
- MPD support (0.18-dsd). See [mpd-dsd-018] (https://github.com/lintweaker/mpd-dsd-018)


## Check if you have a supported device
Currently devices with USB ID `20b1:3008` and USB ID `20b1:2009` are supported. This are devices from iFi Audio/AMR and DIYINHK. If you think you have a (XMOS based) DAC device or converter that should support native DSD playback please contact me.

To check if your device is supported, or at least XMOS based(1), use the following command:

`lsusb -d 20b1:`

For the iFi Audio nano and micro iDSD it reports:
`Bus 003 Device 004: ID 20b1:3008 XMOS Ltd` (please note: Bus and Device numbers may vary).

*(1) Some manufacturers may use the XMOS chip with their own vendor id instead of XMOS.*

## HOWTO
There are three ways to get enable native DSD playback on your Linux system:

1. Use pre-compiled binaries
2. Build the RPMs yourself
3. Patch and build from source

### 1. Use pre-compiled binaries
Pre-compiled binaries are provided for Fedora 20 x86_64. Before installing them,
make sure your Fedora installation is fully up-to-date.

Prerequisites:
- rpmfusion repo added and enabled (rpmfusion-free should be sufficient)

Steps:
- clone this repo
- Install the RPMS from the RPMS directory

Start with the kernel:

`sudo yum localinstall kernel-3.17.4-200.jk6.fc20.x86_64.rpm`

If needed, also install the *kernel-headers* and *kernel-devel* packages.

Replace ALSA lib, the current ALSA lib needs to be overwritten due to the many
dependencies.

`sudo rpm -ivh alsa-lib-1.0.27.2-2.fc20.x86_64.rpm --force`

If needed, install the *alsa-devel* package as well.

Install/update MPD:

`sudo yum localinstall mpd-0.18.16-2.fc20.x86_64.rpm`

With the rpmfusion repo enabled any missing library will be installed as dependency.

As a final installation step, reboot the machine.
After the reboot make sure you are running the new kernel:
`uname -r` should report `3.17.4-200.jk1.fc20.x86_64`.

Now configure mpd (*/etc/mpd.conf*) to your liking and add the statements with "dsd_native" to the audio section, e.g.:

*audio_output {<br>
&nbsp;&nbsp;type&nbsp;"alsa"<br>
&nbsp;&nbsp;name&nbsp;"iFi Audio micro iDSD"<br>
&nbsp;&nbsp;device&nbsp;"hw:1,0"<br>
&nbsp;&nbsp;# Enable native DSD playback<br>
&nbsp;&nbsp;dsd_native&nbsp;"yes"<br>
&nbsp;&nbsp;# Select 32-bit DSD_U32_BE output format<br>
&nbsp;&nbsp;dsd_native_type&nbsp;"2"<br>
}*<br>

Nb if you have DSD over PCM (DoP) enabled with "dsd_usb" "yes", disable it with "dsd_usb" "no".

#### Verifify that is works

To verify that native DSD playback actually works, play back a DSD file using either *MPD* or the *playdsd.py* script and check the 'hw_params' file of your ALSA audio device.

Example for a DSD64 file:

cat /proc/asound/Audio/pcm0p/sub0/hw_params<br>
access: MMAP_INTERLEAVED<br>
format: DSD_U32_BE<br>
subformat: STD<br>
channels: 2<br>
rate: 88200 (88200/1)<br>
period_size: 11025<br>
buffer_size: 44100<br>

Notice the DSD_U32_BE sample format and rate of 88200.

### 2. Build the RPMs yourself

These instructions are tested on Fedora 20 x86_64.

General prerequisites:
- System prepared for rpm building, see [Fedora build a custom kernel] (https://fedoraproject.org/wiki/Building_a_custom_kernel)

Prerequisites for building MPD:
- rpmfusion repo added and enabled (rpmfusion-free should be sufficient)

Prepare:
- clone this repo

Build the kernel:
- Download the required kernel source RPM from [koji] (http://koji.fedoraproject.org/koji/packageinfo?packageID=8)
- Make sure the needed dependencies are installed:

   `sudo yum-builddep kernel-<version>.src.rpm`<br>
   `yum install pesign`<br>

- Install it (as normal user).

  `rpm -ivh <kernel-source-rpm>`

- Copy the needed patches from this repo to the SOURCES directory

  `cp SRPMS/patches/* ~/rpmbuild/SOURCES`

- Replace the SPEC file (2):

  `cp SPECS/kernel.spec ~/rpmbuild/SPECS`

(2) If you use another kernel then 3.17.4-200, its SPEC file needs to be adjusted to include the needed patches

- Build the kernel, e.g.:

  `cd ~/rpmbuild/SPECS`<br>
  ``rpmbuild -bb --without debug --without perf --without debuginfo --target=`uname -m`  kernel.spec``<br>

Build ALSA lib:

- Make sure the needed dependencies are installed:

  `sudo yum-builddep alsa-lib-1.0.27.2-2.fc20.src.rpm`

- Install it (as normal user):

  `sudo rpm -ivh alsa-lib-1.0.27.2-2.fc20.src.rpm`

- Build it (as normal user):

  `cd ~/rpmbuild/SPECS`<br>
  ``rpmbuild -bb --target=`uname -m`  alsa-lib.spec``<br>

Build MPD:
- Make sure the needed dependencies are installed:

  `sudo yum-builddep mpd-0.18.16-2.fc20.src.rpm`

- Install it (as normal user):

  `sudo rpm -ivh mpd-0.18.16-2.fc20.src.rpm`

- Build it:

  `cd ~/rpmbuild/SPECS`<br>
  ``rpmbuild -bb --target=`uname -m` mpd.spec``<br>

Install the created RPMs using HOWTO step 1 above.

### 3. Patch and build from source

General instructions for compiling everything yourself. The needed patches are in SRPMS/patches.

#### kernel
Download and prepare the kernel source for your distribution. Enter the kernel source directory.
Check if the patches apply cleanly:<br>
`patch -p1 < /path/to/SRPM/patches/kernel/alsa-add-dsd-u32-le-v5.patch --dry-run`<br>
`patch -p1 < /path/to/SRPM/patches/kernel/0001-add-native-DSD-support-for-XMOS-based-DACs.patch --dry-run`<br>
`patch -p1 < /path/to/SRPM/patches/kernel/alsa-usb-marantz-ctl-msg-quirk-v2.patch --dry-run`<br>
`patch -p1 < /path/to/SRPM/patches/kernel/alsa-add-dsd-be-formats.patch --dry-run`<br>
`patch -p1 < /path/to/SRPM/patches/kernel/alsa-usb-switch-xmos-dsd-quirk-to-be.patch --dry-run`<br>
`patch -p1 < /path/to/SRPM/patches/kernel/alsa-usb-add-marantz-dsd-quirk.patch --dry-run`<br>
`patch -p1 < /path/to/SRPM/patches/kernel/alsa-usb-marantz-select-mode-quirk-v5.patch --dry-run`<br>

If the patches apply cleanly, apply them.<br>
`patch -p1 < /path/to/SRPM/patches/kernel/alsa-add-dsd-u32-le-v5.patch`<br>
`patch -p1 < /path/to/SRPM/patches/kernel0001-add-native-DSD-support-for-XMOS-based-DACs.patch`<br>
`patch -p1 < /path/to/SRPM/patches/kernel/alsa-usb-marantz-ctl-msg-quirk-v2.patch`<br>
`patch -p1 < /path/to/SRPM/patches/kernel/alsa-add-dsd-be-formats.patch`<br>
`patch -p1 < /path/to/SRPM/patches/kernel/alsa-usb-switch-xmos-dsd-quirk-to-be.patch`<br>
`patch -p1 < /path/to/SRPM/patches/kernel/alsa-usb-add-marantz-dsd-quirk.patch`<br>
`patch -p1 < /path/to/SRPM/patches/kernel/alsa-usb-marantz-select-mode-quirk-v5.patch`<br>

Compile and install the kernel as per instructions for your Linux distribution.

#### ALSA lib
The provided ALSA patches are for ALSA lib version 1.0.27.2.<br>

Download the ALSA lib 1.0.27.2 sources from ftp://ftp.alsa-project.org/pub/lib/alsa-lib-1.0.27.2.tar.bz2

Unpack and enter the alsa-lib-1.0.27.2 directory. Apply the patches:

`patch -p1 < ~/path/to/SRPMS/patches/alsa-lib/0001-pcm-Fix-DSD-formats-userland-usability.patch --dry-run`<br>
`patch -p1 < ~/path/to/SRPMS/patches/alsa-lib/0001-pcm-Add-missing-signed-and-endianess-definitions-for.patch --dry-run`<br>
`patch -p1 < ~/path/to/SRPMS/patches/alsa-lib/0001-pcm-2nd-round-of-pcm_misc-DSD-fixes.patch --dry-run`<br>
`patch -p1 < ~/path/to/SRPMS/patches/alsa-lib/alsa-lib-add-dsd-u32-le-v3.patch`<br>
`patch -p1 < ~/path/to/SRPMS/patches/alsa-lib/alsa-lib-add-dsd-be-formats.patch`<br>

Compile and install alsa-lib.

#### MPD

Use [mpd-dsd-018] (https://github.com/lintweaker/mpd-dsd-018). Configure mpd to use dsd_native as mentioned above.

