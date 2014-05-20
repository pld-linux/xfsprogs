#
# Conditional build:
%bcond_without	tcmalloc	# don't use tcmalloc
#
Summary:	Tools for the XFS filesystem
Summary(pl.UTF-8):	Narzędzia do systemu plików XFS
Name:		xfsprogs
Version:	3.2.0
Release:	1
License:	LGPL v2.1 (libhandle), GPL v2 (the rest)
Group:		Applications/System
Source0:	ftp://linux-xfs.sgi.com/projects/xfs/cmd_tars/%{name}-%{version}.tar.gz
# Source0-md5:	400047b2f6af87c0345b8f0cc00c13db
Source1:	xfs_lsprojid
Patch0:		%{name}-miscfix-v2.patch
Patch1:		%{name}-pl.po-update.patch
Patch2:		%{name}-repair-tcmalloc.patch
Patch3:		%{name}-noquotasync.patch
URL:		http://www.xfs.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bash
BuildRequires:	gettext-devel
BuildRequires:	libblkid-devel
%{?with_tcmalloc:BuildRequires:	libtcmalloc-devel}
BuildRequires:	libtool
BuildRequires:	libuuid-devel
BuildRequires:	readline-devel
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	rpmbuild(macros) >= 1.402
%{?with_tcmalloc:Requires:	libtcmalloc >= 1.8.3-3}
Obsoletes:	xfsprogs-initrd
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%if "%{pld_release}" == "ac"
# libtool in ac doesn't do the reordering of args properly
%define		filterout_ld -Wl,--as-needed
%endif

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

%{?with_tcmalloc:%patch2 -p1}
%patch3 -p1

%build
%{__aclocal} -I m4
%{__autoconf}
%configure \
	--sbindir=%{_bindir}\
	--enable-gettext \
	--enable-readline \
	--enable-blkid \
	DEBUG="%{?debug:-DDEBUG}%{!?debug:-DNDEBUG}" \
	OPTIMIZER="%{rpmcflags}"

%{__make} -j1 \
	V=1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libexecdir},/etc}

DIST_ROOT=$RPM_BUILD_ROOT
DIST_INSTALL=$(pwd)/install.manifest
DIST_INSTALL_DEV=$(pwd)/install-dev.manifest
export DIST_ROOT DIST_INSTALL DIST_INSTALL_DEV

%{__make} install \
	DIST_MANIFEST="$DIST_INSTALL"
%{__make} install-dev \
	DIST_MANIFEST="$DIST_INSTALL_DEV"

install %{SOURCE1} $RPM_BUILD_ROOT%{_bindir}/xfs_lsprojid

ln -sf %{_libdir}/$(basename $RPM_BUILD_ROOT%{_libdir}/libhandle.so.*.*.*) \
	 $RPM_BUILD_ROOT%{_libexecdir}/libhandle.so

mv $RPM_BUILD_ROOT%{_libdir}/lib*.la $RPM_BUILD_ROOT%{_libexecdir}
mv $RPM_BUILD_ROOT%{_libdir}/lib*.a $RPM_BUILD_ROOT%{_libexecdir}

%{__sed} -i -e "s|libdir='%{_libdir}'|libdir='%{_libexecdir}'|" \
	$RPM_BUILD_ROOT%{_libexecdir}/libhandle.la

echo "#10:/mnt/ftp/roman"  >> $RPM_BUILD_ROOT/etc/projects
echo "#ftproman:10" >> $RPM_BUILD_ROOT/etc/projid

%find_lang %{name}

%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/%{name}

# already in /usr
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libhandle.so

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc README doc/{CHANGES,CREDITS}
%config(noreplace) %verify(not md5 mtime size) /etc/projects
%config(noreplace) %verify(not md5 mtime size) /etc/projid
%attr(755,root,root) %{_sbindir}/fsck.xfs
%attr(755,root,root) %{_sbindir}/mkfs.xfs
%attr(755,root,root) %{_sbindir}/xfs_repair
%attr(755,root,root) %{_bindir}/xfs_*
%attr(755,root,root) %{_libdir}/libhandle.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libhandle.so.1
%{_mandir}/man5/projects.5*
%{_mandir}/man5/projid.5*
%{_mandir}/man5/xfs.5*
%{_mandir}/man8/fsck.xfs.8*
%{_mandir}/man8/mkfs.xfs.8*
%{_mandir}/man8/xfs_*.8*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libexecdir}/libhandle.so
%{_libexecdir}/libhandle.la
%{_includedir}/xfs
%{_mandir}/man3/*handle.3*
%{_mandir}/man3/xfsctl.3*

%files static
%defattr(644,root,root,755)
%{_libexecdir}/libhandle.a
