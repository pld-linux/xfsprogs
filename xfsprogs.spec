Summary:	Tools for the XFS filesystem
Summary(pl):	Narzêdzia do systemu plikowego XFS
Name:		xfsprogs
Version:	1.2.0
Release:	1
License:	GPL
Group:		Applications/System
Group(de):	Applikationen/System
Group(pl):	Aplikacje/System
Source0:	ftp://linux-xfs.sgi.com/projects/xfs/download/cmd_tars/%{name}-%{version}.src.tar.gz
Patch0:		%{name}-miscfix.patch
BuildRequires:	e2fsprogs-devel
BuildRequires:	lvm-devel
BuildRequires:	autoconf
URL:		http://oss.sgi.com/projects/xfs/
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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
by³ u¿ywany na platformie SGI IRIX. Jest to w pe³ni wielo-w±tkowy,
obs³uguj±cy wielkie pliki oraz wielkie systemy, o rozsze¿onych
atrybutach, zmiennych wielko¶ciach bloków, mocno wykorzystuj±cy
B-drzewa by uzyskaæ wysok± wydajno¶æ oraz skalowalno¶æ.

%package devel
Summary:	Header files and libraries to develop XFS software
Summary(pl):	Pliki nag³ówkowe i biblioteki
Group:		Development/Libraries
Group(de):	Entwicklung/Libraries
Group(fr):	Development/Librairies
Group(pl):	Programowanie/Biblioteki
Requires:	%{name} = %{version}

%description devel
Header files and libraries to develop software which operates on XFS
filesystems.

%description -l pl devel
Pliki nag³ówkowe i biblioteki potrzebne do rozwoju oprogramowania
operuj±cego na systemie plików XFS.

%prep
%setup  -q
%patch0 -p1

%build
DEBUG="%{?debug:-DDEBUG}%{!?debug:-DNDEBUG}"; export DEBUG
autoconf
%configure 

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

DIST_ROOT="$RPM_BUILD_ROOT"
DIST_INSTALL=`pwd`/install.manifest
DIST_INSTALL_DEV=`pwd`/install-dev.manifest
export DIST_ROOT DIST_INSTALL DIST_INSTALL_DEV 
%{__make} install DIST_MANIFEST="$DIST_INSTALL"
%{__make} install-dev DIST_MANIFEST="$DIST_INSTALL_DEV"

for man in attr_list_by_handle.3 attr_multi_by_handle.3 \
           fd_to_handle.3 free_handle.3 fssetdm_by_handle.3 \
	   handle_to_fshandle.3 open_by_handle.3 path_to_fshandle.3 \
	   readlink_by_handle.3; do
	   	rm -f $RPM_BUILD_ROOT%{_mandir}/man3/$man
		echo ".so man3/path_to_handle.3" \
			> $RPM_BUILD_ROOT%{_mandir}/man3/$man
done

rm -f $RPM_BUILD_ROOT%{_mandir}/man8/xfs_info.8
echo ".so man8/xfs_growfs.8" > $RPM_BUILD_ROOT%{_mandir}/man8/xfs_info.8

gzip -9nf doc/{CHANGES,CREDITS,README.*}
%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc doc/*.gz
%attr(755,root,root) /sbin/*
%attr(755,root,root) %{_sbindir}/*
%{_mandir}/man[18]/*

%files devel
%defattr(644,root,root,755)
%{_mandir}/man3/*
%{_includedir}/xfs
%{_libdir}/*.a
