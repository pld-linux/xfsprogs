# conditional build
#  --with static
Summary:	Tools for the XFS filesystem
Summary(pl):	Narzêdzia do systemu plików XFS
Name:		xfsprogs
Version:	2.3.6
Release:	1
License:	GPL
Group:		Applications/System
Source0:	ftp://linux-xfs.sgi.com/projects/xfs/download/cmd_tars/%{name}-%{version}.src.tar.gz
Patch0:		%{name}-miscfix-v2.patch
Patch1:		%{name}-install-sh.patch
Patch2:		%{name}-sharedlibs.patch
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bash
BuildRequires:	e2fsprogs-devel
URL:		http://oss.sgi.com/projects/xfs/
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Obsoletes:	libxfs1

%define		_sbindir	/sbin
%define		_bindir		/usr/sbin
%define		_libdir		/lib
%define		_libexecdir	/usr/lib

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

%description -l pl
Zbiór komend do u¿ytku z systemem plików XFS, w³±czaj±c w to mkfs.xfs.

XFS jest wysoko wydajnym systemem plików z kronik±, który oryginalnie
by³ u¿ywany na platformie SGI IRIX. Jest to w pe³ni wielow±tkowy,
obs³uguj±cy wielkie pliki oraz wielkie systemy, o rozszerzonych
atrybutach, zmiennych wielko¶ciach bloków, mocno wykorzystuj±cy
B-drzewa by uzyskaæ wysok± wydajno¶æ oraz skalowalno¶æ.

%package devel
Summary:	Header files and libraries to develop XFS software
Summary(pl):	Pliki nag³ówkowe i biblioteki
Group:		Development/Libraries
Requires:       %{name} = %{version}
Obsoletes:	libxfs1-devel

%description devel
Header files and libraries to develop software which operates on XFS
filesystems.

%description devel -l pl
Pliki nag³ówkowe i biblioteki potrzebne do rozwoju oprogramowania
operuj±cego na systemie plików XFS.

%package static
Summary:	Static XFS software libraries
Summary(pl):	Biblioteki statyczne do XFS
Group:		Development/Libraries

%description static
Static XFS software libraries.

%description static -l pl
Biblioteki statyczne do XFS.

%prep
%setup  -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
DEBUG="%{?debug:-DDEBUG}%{!?debug:-DNDEBUG}"
OPTIMIZER="%{rpmcflags}"
export DEBUG OPTIMIZER
%{__aclocal}
%{__autoconf}
%configure \
	%{!?_with_static:--enable-shared-uuid=yes} \
	%{?_with_static:--disable-shared --disable-shared-uuid}

%{__make} \
	%{?_with_static:LTLINK='$(LIBTOOL) --mode=link %{__cc} -all-static' LDFLAGS=-static}

%install
rm -rf $RPM_BUILD_ROOT

DIST_ROOT="$RPM_BUILD_ROOT"
DIST_INSTALL=`pwd`/install.manifest
DIST_INSTALL_DEV=`pwd`/install-dev.manifest
export DIST_ROOT DIST_INSTALL DIST_INSTALL_DEV
%{?_with_static:cp include/builddefs include/builddefs.tmp}
%{?_with_static:sed -e 's/\.lai/.la/' include/builddefs.tmp > include/builddefs}
%{__make} install DIST_MANIFEST="$DIST_INSTALL"
%{__make} install-dev DIST_MANIFEST="$DIST_INSTALL_DEV"

for man in attr_list_by_handle.3 attr_multi_by_handle.3 \
           fd_to_handle.3 free_handle.3 fssetdm_by_handle.3 \
	   handle_to_fshandle.3 open_by_handle.3 path_to_fshandle.3 \
	   readlink_by_handle.3; do
	   	rm -f $RPM_BUILD_ROOT%{_mandir}/man3/$man
		echo ".so path_to_handle.3" \
			> $RPM_BUILD_ROOT%{_mandir}/man3/$man
done

rm -f $RPM_BUILD_ROOT%{_mandir}/man8/xfs_info.8
echo ".so xfs_growfs.8" > $RPM_BUILD_ROOT%{_mandir}/man8/xfs_info.8

ln -sf %{_libdir}/libhandle.so.1.0.1 $RPM_BUILD_ROOT%{_libexecdir}/libhandle.so
ln -sf %{_libdir}/libdisk.so.0.0.0 $RPM_BUILD_ROOT%{_libexecdir}/libdisk.so
ln -sf %{_libdir}/libxfs.so.0.0.0 $RPM_BUILD_ROOT%{_libexecdir}/libxfs.so
ln -sf %{_libdir}/libxlog.so.0.0.0 $RPM_BUILD_ROOT%{_libexecdir}/libxlog.so

%clean
rm -rf $RPM_BUILD_ROOT

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc doc/{CHANGES,CREDITS,README.*}
%attr(755,root,root) %{_sbindir}*
%attr(755,root,root) %{_bindir}/*
%{!?_with_static:%attr(755,root,root) /lib/lib*.so.*.*}
%{_mandir}/man[185]/*

%files devel
%defattr(644,root,root,755)
%{_mandir}/man3/*
%{_includedir}/disk
%{_includedir}/xfs
%{_libexecdir}/*.la
%attr(755,root,root) %{_libexecdir}/*.so

%files static
%defattr(644,root,root,755)
%{_libexecdir}/*.a
