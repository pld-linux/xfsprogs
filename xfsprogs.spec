#
# Conditional build:
%bcond_without	debug_asserts
%bcond_without	libicu		# libicu (unicode scanning in xfs_scrub)
%bcond_without	scrub		# xfs_scrub utility
%bcond_without	static_libs	# static library
#
Summary:	Tools for the XFS filesystem
Summary(pl.UTF-8):	Narzędzia do systemu plików XFS
Name:		xfsprogs
Version:	6.11.0
Release:	1
License:	LGPL v2.1 (libhandle), GPL v2 (the rest)
Group:		Applications/System
Source0:	https://www.kernel.org/pub/linux/utils/fs/xfs/xfsprogs/%{name}-%{version}.tar.xz
# Source0-md5:	01ac717e8ecffbbb313a20242da9c98d
Source1:	xfs_lsprojid
Patch0:		%{name}-miscfix-v2.patch
Patch1:		%{name}-pl.po-update.patch
Patch2:		build-deps.patch
URL:		https://xfs.wiki.kernel.org/
# for <attr/attributes.h>
BuildRequires:	attr-devel
BuildRequires:	autoconf >= 2.69
BuildRequires:	automake
BuildRequires:	bash
BuildRequires:	device-mapper-devel
BuildRequires:	gettext-tools
BuildRequires:	glibc-static
BuildRequires:	inih-devel
BuildRequires:	libblkid-devel
# without .la file so that -static-libtool-libs won't take libedit.a
BuildRequires:	libedit-devel >= 3.1-1.20191231.1
%{?with_libicu:BuildRequires:	libicu-devel}
BuildRequires:	libtool
BuildRequires:	libuuid-devel
BuildRequires:	libuuid-static
BuildRequires:	pkgconfig
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	rpmbuild(macros) >= 1.527
%{?with_scrub:BuildRequires:	systemd-devel}
BuildRequires:	userspace-rcu-devel
BuildRequires:	userspace-rcu-static
BuildRequires:	sed >= 4.0
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
Obsoletes:	xfsprogs-initrd < 3.1.11-2
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%if "%{pld_release}" == "ac"
# libtool in ac doesn't do the reordering of args properly
%define		filterout_ld -Wl,--as-needed
%endif

%description
A set of commands to use the XFS filesystem, including mkfs.xfs.

XFS is a high performance journaling filesystem which originated on
the SGI IRIX platform. It is completely multi-threaded, can support
large files and large filesystems, extended attributes, variable block
sizes, is extent based, and makes extensive use of Btrees
(directories, extents, free space) to aid both performance and
scalability.

This implementation is on-disk compatible with the IRIX version of
XFS.

%description -l pl.UTF-8
Zbiór komend do użytku z systemem plików XFS, włączając w to mkfs.xfs.

XFS jest wysoko wydajnym systemem plików z kroniką, który oryginalnie
był używany na platformie SGI IRIX. Jest to w pełni wielowątkowy,
obsługujący wielkie pliki oraz wielkie systemy, o rozszerzonych
atrybutach, zmiennych wielkościach bloków, mocno wykorzystujący
B-drzewa by uzyskać wysoką wydajność oraz skalowalność.

%package scrub
Summary:	xfs_scrub - XFS online check and repair feature (EXPERIMENTAL!)
Summary(pl.UTF-8):	xfs_scrub - sprawdzanie i naprawianie zamontowanego systemu plików XFS (EKSPERYMENTALNE!)
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}
Requires:	systemd-units >= 38

%description scrub
xfs_scrub is an XFS online check and repair feature.

WARNING: EXPERIMENTAL, use at your own risk!

%description scrub -l pl.UTF-8
xfs_scrub służy do sprawdzania i naprawiania zamontowanego systmeu
plików XFS w locie.

UWAGA: EXPERIMENTALNE, użycie na własne ryzyko!

%package devel
Summary:	Header files and libraries to develop XFS software
Summary(pl.UTF-8):	Pliki nagłówkowe i biblioteki
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	libuuid-devel
Requires:	linux-libc-headers

%description devel
Header files and libraries to develop software which operates on XFS
filesystems.

%description devel -l pl.UTF-8
Pliki nagłówkowe i biblioteki potrzebne do rozwoju oprogramowania
operującego na systemie plików XFS.

%package static
Summary:	Static XFS software libraries
Summary(pl.UTF-8):	Biblioteki statyczne do XFS
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static XFS software libraries.

%description static -l pl.UTF-8
Biblioteki statyczne do XFS.

%prep
%setup -q
%patch0 -p1
%patch2 -p1

# files order in pot changes in every version, making diff huge - sort entries first
%{__mv} po/xfsprogs.pot po/xfsprogs.pot.upstream
msgcat -F po/xfsprogs.pot.upstream -o po/xfsprogs.pot
# update line numbers etc.
%{__mv} po/pl.po po/pl.po.upstream
msgmerge po/pl.po.upstream po/xfsprogs.pot -o po/pl.po
%patch1 -p1 -b .orig

%{__sed} -i -e '1s,/usr/bin/env python3,%{__python3},' scrub/xfs_scrub_all.in tools/xfsbuflock.py

%build
%{__aclocal} -I m4
%{__autoconf}
%configure \
	DEBUG="%{?with_debug_asserts:-DDEBUG}%{!?with_debug_asserts:-DNDEBUG}" \
	OPTIMIZER="%{rpmcflags}" \
	--enable-editline \
	--enable-gettext \
	%{__enable_disable libicu libicu} \
	--disable-lto \
	%{?with_scrub:--enable-scrub=yes} \
	%{__enable_disable static_libs static} \
	--with-udev-rule-dir=/lib/udev/rules.d

%{__make} \
	V=1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/cron.d,/sbin,/%{_lib}}

DIST_ROOT=$RPM_BUILD_ROOT
DIST_INSTALL=$(pwd)/install.manifest
DIST_INSTALL_DEV=$(pwd)/install-dev.manifest
export DIST_ROOT DIST_INSTALL DIST_INSTALL_DEV

%{__make} install \
	DIST_MANIFEST="$DIST_INSTALL"
%{__make} install-dev \
	DIST_MANIFEST="$DIST_INSTALL_DEV"

%{__mv} $RPM_BUILD_ROOT%{_sbindir}/{fsck.xfs,mkfs.xfs,xfs_repair} $RPM_BUILD_ROOT/sbin
%{__mv} $RPM_BUILD_ROOT%{_libdir}/libhandle.so.* $RPM_BUILD_ROOT/%{_lib}

install -p %{SOURCE1} $RPM_BUILD_ROOT%{_sbindir}/xfs_lsprojid

# adjust symlink to point to actual library, not libhandle.so symlink, which we remove afterwards
ln -sf /%{_lib}/$(basename $RPM_BUILD_ROOT/%{_lib}/libhandle.so.*.*.*) \
	 $RPM_BUILD_ROOT%{_libdir}/libhandle.so
# adjust library path used at link time
%{__sed} -i -e "s|libdir='/%{_lib}'|libdir='%{_libdir}'|" \
	$RPM_BUILD_ROOT%{_libdir}/libhandle.la

# install cron file
%if %{with scrub}
%{__mv} $RPM_BUILD_ROOT{%{_datadir}/%{name}/xfs_scrub_all.cron,/etc/cron.d/xfs_scrub_all}
%else
%{__rm} $RPM_BUILD_ROOT/%{_datadir}/%{name}/xfs_scrub_all.cron
%endif

# (config file paths are specified in libfrog/projects.c)
echo "#10:/mnt/ftp/roman"  >> $RPM_BUILD_ROOT/etc/projects
echo "#ftproman:10" >> $RPM_BUILD_ROOT/etc/projid

%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/%{name}

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun -p /sbin/ldconfig

%post scrub
%systemd_reload

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc README doc/{CHANGES,CREDITS}
%config(noreplace) %verify(not md5 mtime size) /etc/projects
%config(noreplace) %verify(not md5 mtime size) /etc/projid
%attr(755,root,root) /sbin/fsck.xfs
%attr(755,root,root) /sbin/mkfs.xfs
%attr(755,root,root) /sbin/xfs_repair
%attr(755,root,root) %{_sbindir}/xfs_*
%if %{with scrub}
%exclude %{_sbindir}/xfs_scrub*
%endif
%attr(755,root,root) /%{_lib}/libhandle.so.*.*
%attr(755,root,root) %ghost /%{_lib}/libhandle.so.1
%{_datadir}/%{name}
%if %{with scrub}
%dir %{_libexecdir}/%{name}
%attr(755,root,root) %{_libexecdir}/%{name}/xfs_scrub_fail
%endif
%{_mandir}/man5/projects.5*
%{_mandir}/man5/projid.5*
%{_mandir}/man5/xfs.5*
%{_mandir}/man8/fsck.xfs.8*
%{_mandir}/man8/mkfs.xfs.8*
%{_mandir}/man8/xfs_*.8*
%if %{with scrub}
%exclude %{_mandir}/man8/xfs_scrub*.8*
%endif

%if %{with scrub}
%files scrub
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/xfs_scrub
%attr(755,root,root) %{_sbindir}/xfs_scrub_all
/lib/udev/rules.d/64-xfs.rules
%{systemdunitdir}/system-xfs_scrub.slice
%{systemdunitdir}/xfs_scrub@.service
%{systemdunitdir}/xfs_scrub_all.service
%{systemdunitdir}/xfs_scrub_all.timer
%{systemdunitdir}/xfs_scrub_all_fail.service
%{systemdunitdir}/xfs_scrub_fail@.service
%{systemdunitdir}/xfs_scrub_media@.service
%{systemdunitdir}/xfs_scrub_media_fail@.service
%config(noreplace) %verify(not md5 mtime size) /etc/cron.d/xfs_scrub_all
%{_mandir}/man8/xfs_scrub.8*
%{_mandir}/man8/xfs_scrub_all.8*
%endif

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libhandle.so
%{_libdir}/libhandle.la
%{_includedir}/xfs
%{_mandir}/man2/ioctl_xfs_ag_geometry.2*
%{_mandir}/man2/ioctl_xfs_bulkstat.2*
%{_mandir}/man2/ioctl_xfs_exchange_range.2*
%{_mandir}/man2/ioctl_xfs_fsbulkstat.2*
%{_mandir}/man2/ioctl_xfs_fscounts.2*
%{_mandir}/man2/ioctl_xfs_fsgeometry.2*
%{_mandir}/man2/ioctl_xfs_fsgetxattr.2*
%{_mandir}/man2/ioctl_xfs_fsgetxattra.2*
%{_mandir}/man2/ioctl_xfs_fsinumbers.2*
%{_mandir}/man2/ioctl_xfs_fssetxattr.2*
%{_mandir}/man2/ioctl_xfs_getbmap.2*
%{_mandir}/man2/ioctl_xfs_getbmapa.2*
%{_mandir}/man2/ioctl_xfs_getbmapx.2*
%{_mandir}/man2/ioctl_xfs_getparents.2*
%{_mandir}/man2/ioctl_xfs_getresblks.2*
%{_mandir}/man2/ioctl_xfs_goingdown.2*
%{_mandir}/man2/ioctl_xfs_inumbers.2*
%{_mandir}/man2/ioctl_xfs_scrub_metadata.2*
%{_mandir}/man2/ioctl_xfs_scrubv_metadata.2*
%{_mandir}/man2/ioctl_xfs_setresblks.2*
%{_mandir}/man3/*handle.3*
%{_mandir}/man3/xfsctl.3*

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libhandle.a
%endif
