xmos-native-dsd
==============

Linux support for native DSD playback on XMOS based DSD DACs and converters with native DSD support.

Currently supports native DSD playback on the following XMOS based DACs/USB converters:

- iFi Audio micro iDSD [max DSD512]
- iFi Audio nano iDSD [max DSD256, with latest 4.04 firmware]
- DIYINHK USB to I2S/DSD converter [max DSD128]
- ..more to follow

[05-sep-14]
- Patches have been sent to the ALSA development list for inclusion in the kernel
[08-sep-14]
- Kernel patches accepted and queued for upstream
[10-sep-14]
- Patch for ALSA lib for DSD_U32_LE support sent to ALSA development list

Support:
- Python scripts [python-dsd-tools] (https://github.com/lintweaker/python-dsd-tools)
- MPD support (0.18-dsd). See [mpd-dsd-018] (https://github.com/lintweaker/mpd-dsd-018)

## Native DSD support for XMOS based devices
XMOS based USB DACs and converters can support native DSD playback using a
32-bit sample format. DACs that supporting this feature expose it using a USB interface Alternate Setting.

On Windows systems this feature can be used with a ASIO 2.1/2.2 driver from the DAC manufacturer.

I have added a new DSD sample format to ALSA and the Linux kernel (DSD_U32_LE) to support it on Linux and added the needed quirks to support it for a few XMOS based USB DACs/boards.

## Test if you have a supported device
Currently only devices with USB ID `20b1:3008` and USB ID `20b1:2009` are supported. This are devices from iFi Audio/AMR and DIYINHK. If you think you have a (XMOS based) DAC device or converter that should support native DSD playback please contact me.

To check if your device is supported, or at least XMOS based(1), use the following command:

`lsusb -d 20b1:`

For the iFi Audio nano and micro iDSD it reports:
`Bus 003 Device 004: ID 20b1:3008 XMOS Ltd` (please note: Bus and Device number may vary).

*(1) Some manufacturers using the XMOS chip use their own vendor id instead of XMOS.*

If your device is supported, skip to the HOWTO section.

### Support for your XMOS based device?

If your device is XMOS based but not currently supported, the next step is to see if your devices has an *Alternate Setting*


## HOWTO
1. Use pre-compiled binaries
2. Build the RPMs yourself
3. Patch and build from source

### 1. Use pre-compiled binaries
Pre-compiled binaries are provided for Fedora 20 x86_64. Before installing them,
make sure your Fedora installation is fully up-to-date.

Prequisites:
- rpmfusion repo added and enabled (rpmfusion-free should be sufficient)

Steps:
- clone this repo
- Install the RPMS from the RPMS directory

Start with the kernel:
`sudo yum localinstall kernel-3.16.6-202.jk17.fc20.x86_64.rpm`

If needed, also install the kernel-headers and kernel-devel packages.

Replace ALSA, the current ALSA needs to be replaced due to the many
dependencies.

`sudo rpm -ivh alsa-lib-1.0.27.2-2.fc20.x86_64.rpm --force`

If needed, install the alsa-devel package as well.

Install/update MPD:

`sudo yum localinstall mpd-0.18.16-1.fc20.x86_64.rpm`

With the rpmfusion repo enabled any needed library will be installed.

As a final installation step, reboot.
After the reboot make sure you are running the new kernel:
`uname -r` should report `3.16.6-202.jk17.fc20.x86_64`.

Now configure mpd (/etc/mpd.conf) to your liking and add the statements with "dsd_native" to the audio section, e.g.:

*audio_output {<br>
&nbsp;&nbsp;type&nbsp;"alsa"<br>
&nbsp;&nbsp;name&nbsp;"iFi Audio micro iDSD"<br>
&nbsp;&nbsp;device&nbsp;"hw:1,0"<br>
&nbsp;&nbsp;# Enable native DSD playback<br>
&nbsp;&nbsp;dsd_native&nbsp;"yes"<br>
&nbsp;&nbsp;# Select 32-bit DSD_U32_LE output format<br>
&nbsp;&nbsp;dsd_native_type&nbsp;"2"<br>
}*<br>



### 2. Build the RPMs yourself

### 3. Patch and build from source

