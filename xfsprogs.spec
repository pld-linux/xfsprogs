#
# Conditional build:
%bcond_without	initrd		# don't build initrd version
%bcond_without	dietlibc	# link initrd version with static glibc instead of dietlibc
#
Summary:	Tools for the XFS filesystem
Summary(pl.UTF-8):	Narzędzia do systemu plików XFS
Name:		xfsprogs
Version:	3.0.0
Release:	3.1
License:	LGPL v2.1 (libhandle), GPL v2 (the rest)
Group:		Applications/System
Source0:	ftp://linux-xfs.sgi.com/projects/xfs/cmd_tars/%{name}-%{version}.tar.gz
# Source0-md5:	ec734f935ec87ebb8be890d29380a3e6
Patch0:		%{name}-miscfix-v2.patch
Patch1:		%{name}-install-sh.patch
Patch2:		%{name}-sharedlibs.patch
Patch3:		%{name}-pl.po-update.patch
Patch4:		%{name}-dynamic_exe.patch
Patch5:		%{name}-LDFLAGS.patch
Patch6:		%{name}-diet.patch
URL:		http://oss.sgi.com/projects/xfs/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bash
%{?with_dietlibc:BuildRequires:	dietlibc-static >= 2:0.31-6}
BuildRequires:	gettext-devel
BuildRequires:	libtool
BuildRequires:	libuuid-devel
BuildRequires:	rpmbuild(macros) >= 1.402
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sbindir	/sbin
%define		_bindir		/usr/sbin
%define		_libdir		/%{_lib}
%define		_libexecdir	/usr/%{_lib}

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

%package devel
Summary:	Header files and libraries to develop XFS software
Summary(pl.UTF-8):	Pliki nagłówkowe i biblioteki
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	libuuid-devel

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
%patch1 -p1
%patch2 -p1
# currently obsolete until needed again
# %patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1

rm -f include/{builddefs,platform_defs}.h

%build
%{__aclocal} -I m4

%if %{with initrd}
sed -i -e 's|^AC_PACKAGE_NEED_AIO_H|dnl AC_PACKAGE_NEED_AIO_H|' \
	-e 's|^AC_PACKAGE_NEED_LIO_LISTIO|dnl AC_PACKAGE_NEED_LIO_LISTIO|' \
	configure.in
sed -i -e 's|\(^LIBRT.*=.*\)|# \1|' include/builddefs.in
sed -i -e 's|\(^LLDLIBS.*=.*\)|\1 -lcompat|' db/Makefile mkfs/Makefile

%{__autoconf}
%configure \
	CC="diet %{__cc} -static" \
	--disable-gettext \
	--disable-readline \
	--disable-shared \
	--enable-static \
	DEBUG="%{?debug:-DDEBUG}%{!?debug:-DNDEBUG}" \
	OPTIMIZER="-Wno-deprecated-declarations -Os -D_BSD_SOURCE"

%{__make} -j1 include libxfs libxlog libxcmd libhandle libdisk
%{__make} -j1 db growfs logprint mkfs mdrestore repair

sed -i -e 's|^dnl AC_PACKAGE_NEED_AIO_H|AC_PACKAGE_NEED_AIO_H|' \
	-e 's|^dnl AC_PACKAGE_NEED_LIO_LISTIO|AC_PACKAGE_NEED_LIO_LISTIO|' \
	configure.in
sed -i -e 's|# \(^LIBRT.*=.*\)|\1|' include/builddefs.in
sed -i -e 's|\(^LLDLIBS.*=.*\) -lcompat|\1|' db/Makefile mkfs/Makefile

#{__make} clean
%endif

%{__autoconf}
%configure \
	--enable-gettext \
	--enable-readline \
	DEBUG="%{?debug:-DDEBUG}%{!?debug:-DNDEBUG}" \
	OPTIMIZER="%{rpmcflags}"

%{__make} -j1

%install
rm -rf $RPM_BUILD_ROOT

DIST_ROOT=$RPM_BUILD_ROOT
DIST_INSTALL=$(pwd)/install.manifest
DIST_INSTALL_DEV=$(pwd)/install-dev.manifest
export DIST_ROOT DIST_INSTALL DIST_INSTALL_DEV

%{__make} install \
	DIST_MANIFEST="$DIST_INSTALL"
%{__make} install-dev \
	DIST_MANIFEST="$DIST_INSTALL_DEV"

ln -sf %{_libdir}/$(basename $RPM_BUILD_ROOT%{_libdir}/libhandle.so.*.*.*) \
	 $RPM_BUILD_ROOT%{_libexecdir}/libhandle.so
ln -sf %{_libdir}/$(basename $RPM_BUILD_ROOT%{_libdir}/libdisk.so.*.*.*) \
	$RPM_BUILD_ROOT%{_libexecdir}/libdisk.so
ln -sf %{_libdir}/$(basename $RPM_BUILD_ROOT%{_libdir}/libxcmd.so.*.*.*) \
	$RPM_BUILD_ROOT%{_libexecdir}/libxcmd.so
ln -sf %{_libdir}/$(basename $RPM_BUILD_ROOT%{_libdir}/libxfs.so.*.*.*) \
	$RPM_BUILD_ROOT%{_libexecdir}/libxfs.so
ln -sf %{_libdir}/$(basename $RPM_BUILD_ROOT%{_libdir}/libxlog.so.*.*.*) \
	$RPM_BUILD_ROOT%{_libexecdir}/libxlog.so

%{__sed} -i -e "s|libdir='%{_libdir}'|libdir='%{_libexecdir}'|" \
	$RPM_BUILD_ROOT%{_libexecdir}/lib{disk,handle,xcmd,xfs,xlog}.la
%{__sed} -i -e "s| %{_libdir}/libxfs.la | %{_libexecdir}/libxfs.la |" \
	$RPM_BUILD_ROOT%{_libexecdir}/libxlog.la

%find_lang %{name}

rm -rf $RPM_BUILD_ROOT%{_docdir}/%{name}

# already in /usr
rm -f $RPM_BUILD_ROOT%{_libdir}/libdisk.{a,la,so}
rm -f $RPM_BUILD_ROOT%{_libdir}/libhandle.{a,la,so}
rm -f $RPM_BUILD_ROOT%{_libdir}/libxcmd.{a,la,so}
rm -f $RPM_BUILD_ROOT%{_libdir}/libxfs.{a,la,so}
rm -f $RPM_BUILD_ROOT%{_libdir}/libxlog.{a,la,so}

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc README doc/{CHANGES,CREDITS}
%attr(755,root,root) %{_sbindir}/fsck.xfs
%attr(755,root,root) %{_sbindir}/mkfs.xfs
%attr(755,root,root) %{_sbindir}/xfs_repair
%attr(755,root,root) %{_bindir}/xfs_*
%attr(755,root,root) %{_libdir}/libdisk.so.*.*
%attr(755,root,root) %{_libdir}/libhandle.so.*.*
%attr(755,root,root) %{_libdir}/libxcmd.so.*.*
%attr(755,root,root) %{_libdir}/libxfs.so.*.*
%attr(755,root,root) %{_libdir}/libxlog.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libdisk.so.0
%attr(755,root,root) %ghost %{_libdir}/libhandle.so.1
%attr(755,root,root) %ghost %{_libdir}/libxcmd.so.0
%attr(755,root,root) %ghost %{_libdir}/libxfs.so.0
%attr(755,root,root) %ghost %{_libdir}/libxlog.so.0
%{_mandir}/man5/xfs.5*
%{_mandir}/man8/fsck.xfs.8*
%{_mandir}/man8/mkfs.xfs.8*
%{_mandir}/man8/xfs_*.8*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libexecdir}/libdisk.so
%attr(755,root,root) %{_libexecdir}/libhandle.so
%attr(755,root,root) %{_libexecdir}/libxcmd.so
%attr(755,root,root) %{_libexecdir}/libxfs.so
%attr(755,root,root) %{_libexecdir}/libxlog.so
%{_libexecdir}/libdisk.la
%{_libexecdir}/libhandle.la
%{_libexecdir}/libxcmd.la
%{_libexecdir}/libxfs.la
%{_libexecdir}/libxlog.la
%{_includedir}/xfs
%{_mandir}/man3/*handle.3*
%{_mandir}/man3/xfsctl.3*

%files static
%defattr(644,root,root,755)
%{_libexecdir}/libdisk.a
%{_libexecdir}/libhandle.a
%{_libexecdir}/libxcmd.a
%{_libexecdir}/libxfs.a
%{_libexecdir}/libxlog.a
