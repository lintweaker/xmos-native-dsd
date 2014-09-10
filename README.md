xmos-native-dsd
==============

Placeholder for Linux support for native DSD playback on XMOS based DSD DACs and converters with native DSD support.

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
- Modified aplay to test with DSDIFF files
- Python test scripts
- MPD support (0.18-dsd)


