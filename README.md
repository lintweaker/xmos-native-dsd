Linux native DSD playback support
=================================

## Native DSD support for XMOS based devices
XMOS based USB DACs and converters can support native DSD playback using a
32-bit sample format. DACs that supporting this feature expose it using a USB interface Alternate Setting.

On Windows systems this feature can be used with a ASIO 2.1/2.2 driver from the DAC manufacturer.

I have added a new DSD sample format to ALSA and the Linux kernel (DSD_U32_LE) to support it on Linux and added the needed quirks to support it for a few XMOS based USB DACs/boards.

Currently supports native DSD playback on the following XMOS based DACs/USB converters:

- iFi Audio micro iDSD [max DSD512]
- iFi Audio nano iDSD [max DSD256, with latest 4.04 firmware]
- DIYINHK USB to I2S/DSD converter [max DSD128]
- ..more to follow

#### ALSA support status:
- New DSD sample format accepted, code resides in ALSA development git
- Will be generally available with the next ALSA lib update

#### Kernel support status:
- Kernel 3.18rc1 contains the needed new sample format support
- Kernel 3.18rc1 supports the iFi Audio and DIYINKHK devices

#### Linux Playback support:
- My python scripts [python-dsd-tools] (https://github.com/lintweaker/python-dsd-tools)
- MPD support (0.18-dsd). See [mpd-dsd-018] (https://github.com/lintweaker/mpd-dsd-018)


## Test if you have a supported device
Currently only devices with USB ID `20b1:3008` and USB ID `20b1:2009` are supported. This are devices from iFi Audio/AMR and DIYINHK. If you think you have a (XMOS based) DAC device or converter that should support native DSD playback please contact me.

To check if your device is supported, or at least XMOS based(1), use the following command:

`lsusb -d 20b1:`

For the iFi Audio nano and micro iDSD it reports:
`Bus 003 Device 004: ID 20b1:3008 XMOS Ltd` (please note: Bus and Device number may vary).

*(1) Some manufacturers using the XMOS chip use their own vendor id instead of XMOS.*

## HOWTO
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

`sudo yum localinstall kernel-3.16.6-202.jk17.fc20.x86_64.rpm`

If needed, also install the *kernel-headers* and *kernel-devel* packages.

Replace ALSA, the current ALSA needs to be replaced due to the many
dependencies.

`sudo rpm -ivh alsa-lib-1.0.27.2-2.fc20.x86_64.rpm --force`

If needed, install the *alsa-devel* package as well.

Install/update MPD:

`sudo yum localinstall mpd-0.18.16-1.fc20.x86_64.rpm`

With the rpmfusion repo enabled any missing library will be installed as dependency.

As a final installation step, reboot.the machine.
After the reboot make sure you are running the new kernel:
`uname -r` should report `3.16.6-202.jk17.fc20.x86_64`.

Now configure mpd (*/etc/mpd.conf*) to your liking and add the statements with "dsd_native" to the audio section, e.g.:

*audio_output {<br>
&nbsp;&nbsp;type&nbsp;"alsa"<br>
&nbsp;&nbsp;name&nbsp;"iFi Audio micro iDSD"<br>
&nbsp;&nbsp;device&nbsp;"hw:1,0"<br>
&nbsp;&nbsp;# Enable native DSD playback<br>
&nbsp;&nbsp;dsd_native&nbsp;"yes"<br>
&nbsp;&nbsp;# Select 32-bit DSD_U32_LE output format<br>
&nbsp;&nbsp;dsd_native_type&nbsp;"2"<br>
}*<br>

Nb if you have DSD over PCM (DoP) enabled with "dsd_usb" "yes", disable it with "dsd_usb" "no".

#### Verifify that is works

To verify that native DSD playback actually works, play back a DSD file using either MPD or the playdsd.py python script and check the 'hw_params' file for your ALSA audio device.

Example for a DSD64 file:

cat /proc/asound/Audio/pcm0p/sub0/hw_params<br>
access: MMAP_INTERLEAVED<br>
format: DSD_U32_LE<br>
subformat: STD<br>
channels: 2<br>
rate: 88200 (88200/1)<br>
period_size: 11025<br>
buffer_size: 44100<br>

Notice the DSD_U32_LE sample format and rate of 88200.

### 2. Build the RPMs yourself

These instructions are tested on Fedora 20 x86_64.

General prerequisites:
- System prepared for rpm building, [Fedora build a custom kernel] (https://fedoraproject.org/wiki/Building_a_custom_kernel)

Prerequisites for building MPD:
- rpmfusion repo added and enabled (rpmfusion-free should be sufficient)

Prepare:
- clone this repo

Build the kernel:
- Download the required kernel source RPM from [koji] (http://koji.fedoraproject.org/koji/)
- Install it (as normal user).
  `rpm -ivh <kernel-source-rpm>`
- Copy the needed patches from this repo to the SOURCES directory

  `cp SRPMS/patches/* ~/rpmbuild/SOURCES`
- Replace the SPEC file:

  `cp SPECS/kernel.spec ~/rpmbuild/SPECS`
- Build the kernel, e.g.:

  ``rpmbuild -bb --without debug --without perf --without debuginfo --target=`uname -m`  kernel.spec``



### 3. Patch and build from source

