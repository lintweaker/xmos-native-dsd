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

Planned support:
- Python test scripts
- MPD support (0.18-dsd). Done, see [mpd-dsd-018] (https://github.com/lintweaker/mpd-dsd-018)

# Native DSD support for XMOS based devices
XMOS based USB DACs and converters can support native DSD playback using a
32-bit sample format. DACs that supporting this feature expose it using a USB interface Alternate Setting.

On Windows systems this feature can be used with a ASIO 2.1/2.2 driver from the DAC manufacturer.

I have added a new DSD sample format to ALSA and the Linux kernel (DSD_U32_LE) to support it on Linux.


# HOWTO
1. Use pre-compiled binaries
2. Build the RPMs yourself
3. Patch and build from source


