%global  _hardened_build     1

%global  mpd_user            mpd
%global  mpd_group           %{mpd_user}

%global  mpd_homedir         %{_localstatedir}/lib/mpd
%global  mpd_logdir          %{_localstatedir}/log/mpd
%global  mpd_musicdir        %{mpd_homedir}/music
%global  mpd_playlistsdir    %{mpd_homedir}/playlists
%global  mpd_rundir          /run/mpd

%global  mpd_configfile      %{_sysconfdir}/mpd.conf
%global  mpd_dbfile          %{mpd_homedir}/mpd.db
%global  mpd_logfile         %{mpd_logdir}/mpd.log
%global  mpd_statefile       %{mpd_homedir}/mpdstate

Name:           mpd
Epoch:          1
Version:        0.18.16
Release:        2%{?dist}
Summary:        The Music Player Daemon
License:        GPLv2+
Group:          Applications/Multimedia
URL:            http://www.musicpd.org/

#Source0:        http://www.musicpd.org/download/mpd/0.18/mpd-%{version}.tar.xz
Source1:        http://www.musicpd.org/download/mpd/0.18/mpd-%{version}.tar.xz.sig
Source0:	mpd-0.18.16-dsd.tar.bz2
# Note that the 0.18.x branch doesn't yet work with Fedora's version of
# libmpcdec which needs updating.
# https://bugzilla.redhat.com/show_bug.cgi?id=1014468
# http://bugs.musicpd.org/view.php?id=3814#bugnotes
Source2:        mpd.logrotate
Source3:        mpd.tmpfiles.d
Patch0:         mpd-0.18-mpdconf.patch

BuildRequires:     alsa-lib-devel
BuildRequires:     audiofile-devel
BuildRequires:     autoconf
BuildRequires:     avahi-glib-devel
BuildRequires:     bzip2-devel
BuildRequires:     faad2-devel
BuildRequires:     ffmpeg-devel
BuildRequires:     flac-devel
BuildRequires:     jack-audio-connection-kit-devel
BuildRequires:     lame-devel
BuildRequires:     libao-devel
BuildRequires:     libcdio-paranoia-devel
BuildRequires:     libcurl-devel
BuildRequires:     libid3tag-devel
BuildRequires:     libmad-devel
BuildRequires:     libmms-devel
BuildRequires:     libmodplug-devel

# Need new version with SV8
# BuildRequires:     libmpcdec-devel

BuildRequires:     libogg-devel
BuildRequires:     libsamplerate-devel
BuildRequires:     libshout-devel
BuildRequires:     libvorbis-devel
BuildRequires:     mikmod-devel
BuildRequires:     opus-devel
BuildRequires:     pkgconfig(libpulse)
BuildRequires:     sqlite-devel
BuildRequires:     systemd-devel
BuildRequires:     wavpack-devel
BuildRequires:     yajl-devel
BuildRequires:     zlib-devel
BuildRequires:     zziplib-devel

Requires(pre):     shadow-utils
Requires(post):    systemd
Requires(preun):   systemd
Requires(postun):  systemd
Conflicts:         mpich2

%description
Music Player Daemon (MPD) is a flexible, powerful, server-side application for
playing music. Through plugins and libraries it can play a variety of sound
files (e.g., OGG, MP3, FLAC, AAC, WAV) and can be controlled remotely via its
network protocol. It can be used as a desktop music player, but is also great
for streaming music to a stereo system over a local network. There are many
GUI and command-line applications to choose from that act as a front-end for
browsing and playing your MPD music collection.


%prep
%setup -q -n %{name}-%{version}-dsd
%patch0 -p0

%build
./autogen.sh
%{configure} \
    --with-systemdsystemunitdir=%{_unitdir} \
    --enable-bzip2 \
    --enable-soundcloud \
    --enable-mikmod \
    --enable-pipe-output \
    --disable-mpc \
    --enable-zzip
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT

install -p -D -m 0644 %{SOURCE2} \
    $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/mpd

install -p -D -m 0644 %{SOURCE3} \
    $RPM_BUILD_ROOT%{_prefix}/lib/tmpfiles.d/mpd.conf
mkdir -p %{buildroot}/run
install -d -m 0755 %{buildroot}/%{mpd_rundir}

mkdir -p $RPM_BUILD_ROOT%{mpd_homedir}
mkdir -p $RPM_BUILD_ROOT%{mpd_logdir}
mkdir -p $RPM_BUILD_ROOT%{mpd_musicdir}
mkdir -p $RPM_BUILD_ROOT%{mpd_playlistsdir}
touch $RPM_BUILD_ROOT%{mpd_dbfile}
touch $RPM_BUILD_ROOT%{mpd_logfile}
touch $RPM_BUILD_ROOT%{mpd_statefile}

install -D -p -m644 doc/mpdconf.example $RPM_BUILD_ROOT%{mpd_configfile}
sed -i -e "s|#music_directory.*$|music_directory \"%{mpd_musicdir}\"|g" \
       -e "s|#playlist_directory.*$|playlist_directory \"%{mpd_playlistsdir}\"|g" \
       -e "s|#db_file.*$|db_file \"%{mpd_dbfile}\"|g" \
       -e "s|#log_file.*$|log_file \"%{mpd_logfile}\"|g" \
       -e "s|#state_file.*$|state_file \"%{mpd_statefile}\"|g" \
       -e 's|#user.*$|user "mpd"|g' \
       $RPM_BUILD_ROOT%{mpd_configfile}

rm -rf $RPM_BUILD_ROOT%{_docdir}/%{name}/


%pre
if [ $1 -eq 1 ]; then
    getent group %{mpd_group} >/dev/null || groupadd -r %{mpd_group}
    getent passwd %{mpd_user} >/dev/null || \
        useradd -r -g %{mpd_group} -d %{mpd_homedir} \
            -s /sbin/nologin -c "Music Player Daemon" %{mpd_user}
    gpasswd -a %{mpd_group} audio || :
    exit 0
fi

%post
%systemd_post mpd.service

%preun
%systemd_preun mpd.service

%postun
%systemd_postun_with_restart mpd.service


%files
%doc AUTHORS COPYING README UPGRADING README-native-DSD
%{_bindir}/%{name}
%{_mandir}/man1/mpd.1*
%{_mandir}/man5/mpd.conf.5*
%{_unitdir}/mpd.service
%config(noreplace) %{mpd_configfile}
%config(noreplace) %{_sysconfdir}/logrotate.d/mpd
%{_prefix}/lib/tmpfiles.d/%{name}.conf

%defattr(-,%{mpd_user},%{mpd_group})
%dir %{mpd_homedir}
%dir %{mpd_logdir}
%dir %{mpd_musicdir}
%dir %{mpd_playlistsdir}
%dir %{mpd_rundir}
%ghost %{mpd_dbfile}
%ghost %{mpd_logfile}
%ghost %{mpd_statefile}


%changelog
* Sun Nov 23 2014 Jurgen Kramer (gtmkramer@xs4all.nl) - 1:0.18.16-2
- Native DSD 32-bit sample format switched to DSD_U32_BE

* Fri Oct 24 2014 Jurgen Kramer (gtmkramer@xs4all.nl) - 1:0.18.16-1
- MPD 0.18.16-dsd release for native DSD playback support testing

* Mon Oct 20 2014 Sérgio Basto <sergio@serjux.com> - 1:0.18.16-2
- Rebuilt for FFmpeg 2.4.3

* Sun Oct 05 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:0.18.16-1
- update to upstream release 0.18.16

* Fri Sep 26 2014 Nicolas Chauvet <kwizart@gmail.com> - 1:0.18.11-3
- Rebuilt for FFmpeg 2.4.x

* Thu Aug 07 2014 Sérgio Basto <sergio@serjux.com> - 1:0.18.11-2
- Rebuilt for ffmpeg-2.3

* Thu Jul 17 2014 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 1:0.18.11-1
- Update to latest upstream release

* Mon May 05 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:0.18.10-1
- update to upstream release 0.18.10

* Sat Mar 29 2014 Sérgio Basto <sergio@serjux.com> - 1:0.18.9-2
- Rebuilt for ffmpeg-2.2

* Sun Mar 23 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:0.18.9-1
- update to upstream release 0.18.9
- update URL
- add detached signature as Source1
- add --enable-soundcloud and BR: yajl-devel
- add --enable-pipe-output
- add BR: systemd-devel

* Wed Oct 02 2013 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 1:0.18-0.1.git0e0be02
- Update mpdconf.example patch
- Update to git checkout from master since 0.17 doesn't use new ffmpeg at all
- disable mpcdec support until Fedora package is updated

* Thu Aug 15 2013 Nicolas Chauvet <kwizart@gmail.com> - 1:0.17.3-4
- Rebuilt for FFmpeg 2.0.x

* Sun May 26 2013 Nicolas Chauvet <kwizart@gmail.com> - 1:0.17.3-3
- Rebuilt for x264/FFmpeg

* Sun Feb 24 2013 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:0.17.3-2
- add tmpfiles.d/mpd.conf in case user wishes to use socket file
- change default socket location in mpd.conf, but leave commented

* Sat Feb 23 2013 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:0.17.3-1
- update to upstream release 0.17.3
- new CUE parser so remove libcue from BuildRequires
- update systemd scriptlets and remove chkconfig from the Requires
- add a logrotate file

* Sat Nov 24 2012 Nicolas Chauvet <kwizart@gmail.com> - 1:0.16.8-6
- Rebuilt for FFmpeg 1.0

* Fri Aug 17 2012 Adrian Reber <adrian@lisas.de> - 1:0.16.8-5
- fix "mpd fails to bind an addres: started too early" (#2447)

* Tue Jun 26 2012 Nicolas Chauvet <kwizart@gmail.com> - 1:0.16.8-4
- Rebuilt for FFmpeg
- Switch BR to pkgconfig(libpulse)

* Fri May 11 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 0.16.8-3
- enable lastfm support
- enable hardened build
- remove redundant libsidplay-devel BR, as mpd requires libsidplay2

* Mon Apr 09 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 0.16.8-2
- add missing chowns to %%post scriptlet
- add missing %%{mpd_logdir} to %%files

* Mon Apr 09 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:0.16.8-1
- update to 0.16.8

* Sat Feb 25 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:0.16.7-2
- remove obsolete BuildRoot tag, %%clean section and unnecessary macros
- do not add mpd to pulse-rt group as system mode is not recommended by
  pulseaudio upstream, and the group no longer exists
- add triggerun and systemd scriptlets
- add Epoch (for triggerun scriptlet) to allow updates to F16
- change default audio output to pulseaudio

* Sun Feb 05 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 0.16.7-1
- update to 0.16.7

* Sun Jan 08 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 0.16.6-1
- update to 0.16.6
- add convenient global variables
- add systemd unit file instead of initscript
- change incorrect --enable-zip to --enable-zzip
- change default log file location to /var/log/mpd/mpd.log
- remove obsolete mpd error-log
- remove obsolete hal fdi file

* Wed Oct 12 2011 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 0.16.5-1
- Update to latest upstream release (#1954)

* Mon Sep 26 2011 Nicolas Chauvet <kwizart@gmail.com> - 0.15.13-2
- Rebuilt for FFmpeg-0.8

* Thu Oct 28 2010 Adrian Reber <adrian@lisas.de> - 0.15.13-1
- updated to 0.15.13
- added mpd user to audio group (#1461)

* Wed Sep 29 2010 Adrian Reber <adrian@lisas.de> - 0.15.12-1
- updated to 0.15.12

* Tue Jul 20 2010 Adrian Reber <adrian@lisas.de> - 0.15.11-1
- updated to 0.15.11 (#1301)

* Fri Jan 22 2010 Adrian Reber <adrian@lisas.de> - 0.15.8-1
- updated to 0.15.8 (#1042)

* Wed Dec 02 2009 Adrian Reber <adrian@lisas.de> - 0.15.6-1
- updated to 0.15.6 (#989)
- added BR libcue-devel (#930)

* Mon Nov 09 2009 Adrian Reber <adrian@lisas.de> - 0.15.5-1
- updated to 0.15.5 (#929)

* Wed Oct 21 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 0.15.2-2
- rebuild for new ffmpeg

* Tue Aug 25 2009 Adrian Reber <adrian@lisas.de> - 0.15.2-1
- updated to 0.15.2
- applied patches from David Woodhouse to fix
  "mpd fails to play to usb audio device" (#731)
- fix description (#765)

* Mon Jun 29 2009 Adrian Reber <adrian@lisas.de> - 0.15-1
- updated to 0.15
- added "Conflicts: mpich2" (#593)
- added BR libmms-devel, libmodplug-devel, libsidplay-devel, bzip2-devel
           zziplib-devel, sqlite-devel
- changed BR avahi-devel to avahi-glib-devel
- adapted config file fixups to newest config file layout

* Sun Mar 29 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 0.14.2-2
- rebuild for new F11 features

* Fri Feb 20 2009 Adrian Reber <adrian@lisas.de> - 0.14.2-1
- updated to 0.14.2

* Sat Jan 31 2009 Adrian Reber <adrian@lisas.de> - 0.14-4
- added BR libcurl-devel (#326)

* Sat Dec 27 2008 Adrian Reber <adrian@lisas.de> - 0.14-3
- updated to 0.14 (#229, #280)
- add mpd user to group pulse-rt (#230)
- added BR lame-devel, wavpack-devel, ffmpeg-devel

* Sun Sep 28 2008 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info - 0.13.2-2
- rebuild

* Fri Jul 25 2008 Adrian Reber <adrian@lisas.de> - 0.13.2-1
- updated to 0.13.2
- added _default_patch_fuzz define

* Thu May 29 2008 Hans de Goede <j.w.r.degoede@hhs.nl> - 0.13.1-3
- Fix mpd crashing when reading in modtracker files (rh bug 448964)

* Thu Mar 06 2008 Adrian Reber <adrian@lisas.de> - 0.13.1-2
- added patches from Thomas Jansen to run mpd by default
  not as root.root but as mpd.mpd

* Mon Feb 11 2008 Adrian Reber <adrian@lisas.de> - 0.13.1-1
- updated to 0.13.1

* Thu Nov 15 2007 Adrian Reber <adrian@lisas.de> - 0.13.0-4
- another rebuilt for faad2

* Fri Nov 09 2007 Thorsten Leemhuis <fedora[AT]leemhuis.info> - 0.13.0-3
- rebuild after faad2 downgrade to fix undefined symbols

* Sat Oct 13 2007 Adrian Reber <adrian@lisas.de> - 0.13.0-2
- rebuilt for rpmfusion
- updated License

* Sun Jul 29 2007 Adrian Reber <adrian@lisas.de> - 0.13.0-1
- update to 0.13.0
- added dwmw2's patches (#1569)
- fixed rpmlint errors and warnings
- added libsamplerate-devel, avahi-devel and
  jack-audio-connection-kit-devel as BR

* Tue Mar 06 2007 Adrian Reber <adrian@lisas.de> - 0.12.1-3
- added flac-1.1.4 patch

* Sat Mar 03 2007 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 0.12.1-2
- Rebuild

* Mon Nov 27 2006 Adrian Reber <adrian@lisas.de> - 0.12.1-1
- updated to 0.12.1
- added missing Requires
- removed deletion of user mpd during %%preun
- removed -m (create home) from useradd

* Wed Oct 11 2006 Adrian Reber <adrian@lisas.de> - 0.11.6-6
- rebuilt

* Tue Mar 21 2006 Andreas Bierfert <andreas.bierfert[AT]lowlatency.de>
- Add missing BR zlib-devel

* Thu Mar 09 2006 Andreas Bierfert <andreas.bierfert[AT]lowlatency.de>
- switch to new release field

* Mon Mar 06 2006 Thorsten Leemhuis <fedora[AT]livna.org>
- no build time defines anymore so adapt spec completely to livna

* Tue Feb 28 2006 Andreas Bierfert <andreas.bierfert[AT]lowlatency.de>
- add dist

* Sun Nov 28 2004 Aurelien Bompard <gauret[AT]free.fr> 0:0.11.5-0.3
- Apply Adrian Reber's patch to use a system-wide daemon, see bug 2234

* Tue Nov 09 2004 Aurelien Bompard <gauret[AT]free.fr> 0:0.11.5-0.2
- Prepare for FC3 (different BuildRequires)

* Fri Nov 05 2004 Aurelien Bompard <gauret[AT]free.fr> 0:0.11.5-0.fdr.1
- Initial Fedora package (from Mandrake)
