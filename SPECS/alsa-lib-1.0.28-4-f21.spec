#define  prever     rc3
#define  prever_dot .rc3
#define  postver    a
#define  jkver	jk1

Summary:  The Advanced Linux Sound Architecture (ALSA) library
Name:     alsa-lib
Version:  1.0.28
Release:  4%{?prever_dot}%{?dist}
#Release:  2%{?jkver}
License:  LGPLv2+
Group:    System Environment/Libraries
URL:      http://www.alsa-project.org/

Source:   ftp://ftp.alsa-project.org/pub/lib/%{name}-%{version}%{?prever}%{?postver}.tar.bz2
Source10: asound.conf
Source11: modprobe-dist-alsa.conf
Source12: modprobe-dist-oss.conf
Patch0:   alsa-lib-1.0.24-config.patch
Patch2:   alsa-lib-1.0.14-glibc-open.patch
Patch4:   alsa-lib-1.0.16-no-dox-date.patch
Patch5:   0001-pcm-Fix-DSD-formats-userland-usability.patch
Patch6:   0001-pcm-Add-missing-signed-and-endianess-definitions-for.patch
Patch7:   0001-pcm-2nd-round-of-pcm_misc-DSD-fixes.patch
Patch8:   alsa-lib-add-dsd-u32-le-v3.patch
Patch9:   alsa-lib-add-dsd-be-formats.patch

BuildRequires:  doxygen
Requires(post): /sbin/ldconfig, coreutils

%description
The Advanced Linux Sound Architecture (ALSA) provides audio and MIDI
functionality to the Linux operating system.

This package includes the ALSA runtime libraries to simplify application
programming and provide higher level functionality as well as support for
the older OSS API, providing binary compatibility for most OSS programs.

%package  devel
Summary:  Development files from the ALSA library
Group:    Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: pkgconfig

%description devel
The Advanced Linux Sound Architecture (ALSA) provides audio and MIDI
functionality to the Linux operating system.

This package includes the ALSA development libraries for developing
against the ALSA libraries and interfaces.

%prep
%setup -q -n %{name}-%{version}%{?prever}%{?postver}
%patch0 -p1 -b .config
%patch2 -p1 -b .glibc-open
%patch4 -p1 -b .no-dox-date
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1

%build
%configure --disable-aload --with-plugindir=%{_libdir}/alsa-lib --disable-alisp

# Remove useless /usr/lib64 rpath on 64bit archs
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make %{?_smp_mflags} V=1
make doc

%install
make DESTDIR=%{buildroot} install

# We need the library to be available even before /usr might be mounted
mkdir -p %{buildroot}/%{_lib}
mv %{buildroot}%{_libdir}/libasound.so.* %{buildroot}/%{_lib}
ln -snf ../../%{_lib}/libasound.so.2 %{buildroot}%{_libdir}/libasound.so

# Install global configuration files
mkdir -p -m 755 %{buildroot}/etc
install -p -m 644 %{SOURCE10} %{buildroot}/etc

# Install the modprobe files for ALSA
mkdir -p -m 755 %{buildroot}/lib/modprobe.d/
install -p -m 644 %{SOURCE11} %{buildroot}/lib/modprobe.d/dist-alsa.conf
# bug#926973, place this file to the doc directory
install -p -m 644 %{SOURCE12} .

# Create UCM directory
mkdir -p %{buildroot}/%{_datadir}/alsa/ucm
# Remove all UCM files (should be selected by architecture)
rm -rf %{buildroot}/%{_datadir}/alsa/ucm/*

#Remove libtool archives.
find %{buildroot} -name '*.la' -delete

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%doc COPYING TODO doc/asoundrc.txt modprobe-dist-oss.conf
# file is as old as 0.2.0 / Red Hat bugzilla #510212
#doc Changelog
%config %{_sysconfdir}/asound.conf
/%{_lib}/libasound.so.*
%{_bindir}/aserver
%{_libdir}/alsa-lib/
%{_datadir}/alsa/
/lib/modprobe.d/dist-*

%files devel
%doc doc/doxygen/
%{_includedir}/alsa/
%{_includedir}/sys/asoundlib.h
%{_libdir}/libasound.so
%{_libdir}/pkgconfig/alsa.pc
%{_datadir}/aclocal/alsa.m4

%changelog
* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.28-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jul 24 2014 Peter Robinson <pbrobinson@fedoraproject.org> 1.0.28-1
- Update to 1.0.28

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.27.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Aug  1 2013 Ville Skyttä <ville.skytta@iki.fi> - 1.0.27.2-2
- Fix build with unversioned %%{_docdir_fmt}.

* Mon Jul 08 2013 Jaroslav Kysela <perex@perex.cz> - 1.0.27.2-1
- Updated to 1.0.27.2

* Thu May 30 2013 Jaroslav Kysela <perex@perex.cz> - 1.0.27.1-2
- Fixed bug#953352

* Tue May 21 2013 Jaroslav Kysela <perex@perex.cz> - 1.0.27.1-1
- Updated to 1.0.27.1

* Tue May 07 2013 Rex Dieter <rdieter@fedoraproject.org> 1.0.27-3
- pull in upstream fix for building in C90 mode

* Thu Apr 11 2013 Jaroslav Kysela <perex@perex.cz> - 1.0.27-2
- move dist-oss.conf to doc as modprobe-dist-oss.conf

* Thu Apr 11 2013 Jaroslav Kysela <perex@perex.cz> - 1.0.27-1
- Updated to 1.0.27

* Wed Apr 03 2013 Stephen Gallagher <sgallagh@redhat.com> - 1.0.26-4
- Add upstream patch to explicitly include sys/types.h

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.26-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Dec  3 2012 Peter Robinson <pbrobinson@fedoraproject.org> 1.0.26-2
- Create and own ucm directory so alsaucm doesn't crash.
- Cleanup and modernise spec

* Thu Sep  6 2012 Jaroslav Kysela <jkysela@redhat.com> - 1.0.26-1
- Updated to 1.0.26

* Thu Jul 26 2012 Michael Schwendt <mschwendt@fedoraproject.org> - 1.0.25-6
- Don't package ancient ChangeLog that ends at alsa-lib 0.2.0 (#510212).

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.25-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed May  2 2012 Josh Boyer <jwboyer@redhat.com> - 1.0.25-4
- Install ALSA related module conf files

* Wed Feb  1 2012 Jaroslav Kysela <jkysela@redhat.com> - 1.0.25-3
- Remove the pulse audio configuration from /etc/asound.conf

* Sat Jan 28 2012 Jaroslav Kysela <jkysela@redhat.com> - 1.0.25-1
- Updated to 1.0.25 final

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.24-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.24-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Jan 28 2011 Jaroslav Kysela <jkysela@redhat.com> - 1.0.24-1
- Updated to 1.0.24 final

* Tue Nov  9 2010 Jochen Schmitt <Jochen herr-schmitt de> 1.0.23-2
- Set plugindir to %%{_libdir}/alsa-lib (bz#651507)

* Fri Apr 16 2010 Jaroslav Kysela <jkysela@redhat.com> - 1.0.23-1
- Updated to 1.0.23 final

* Mon Dec 28 2009 Jaroslav Kysela <jkysela@redhat.com> - 1.0.22-1
- Updated to 1.0.22 final
- Fix file descriptor leak in pcm_hw plugin
- Fix sound distortions for S24_LE - softvol plugin

* Wed Sep  9 2009 Jaroslav Kysela <jkysela@redhat.com> - 1.0.21-3
- Add Speaker and Beep control names to mixer weight list
- Fix redhat bug #521988

* Wed Sep  2 2009 Jaroslav Kysela <jkysela@redhat.com> - 1.0.21-1
- Updated to 1.0.21 final

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.20-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed May  6 2009 Jaroslav Kysela <jkysela@redhat.com> - 1.0.20-1
- Updated to 1.0.20 final

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.19-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb  4 2009 Jaroslav Kysela <jkysela@redhat.com> - 1.0.19-2
- Make doxygen documentation same for all architectures (bz#465205)

* Tue Jan 20 2009 Jaroslav Kysela <jkysela@redhat.com> - 1.0.19-1
- Updated to 1.0.19 final
