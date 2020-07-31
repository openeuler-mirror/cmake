%bcond_with bootstrap
%bcond_without ncurses
%bcond_without sphinx
%bcond_without X11_test
%global rpm_macros_dir %(d=%{_rpmconfigdir}/macros.d; [ -d $d ] || d=%{_sysconfdir}/rpm; echo $d)

%{!?_pkgdocdir:%global _pkgdocdir %{_docdir}/cmake-%{version}}
%{?rcsuf:%global relsuf .%{rcsuf}}
%{?rcsuf:%global versuf -%{rcsuf}}

Name:           cmake
Version:        3.18.0
Release:        1
Summary:        Cross-platform make system
License:        BSD and MIT and zlib
URL:            http://www.cmake.org
Source0:        https://www.cmake.org/files/v3.18/cmake-%{version}.tar.gz
Source1:        cmake-init.el
Source2:        macros.cmake
Source3:        cmake.attr
Source4:        cmake.prov
Source5:        cmake.req
Patch0:         cmake-findruby.patch
Patch1:         cmake-fedora-flag_release.patch
Patch2:         cmake-mingw-dl.patch

BuildRequires:  coreutils findutils gcc-c++ gcc-gfortran sed gdb
BuildRequires:  emacs python3-devel pkgconfig(Qt5Widgets) desktop-file-utils
%if %{with X11_test}
BuildRequires:  libX11-devel
%endif
%if %{with ncurses}
BuildRequires:  ncurses-devel
%endif
%if %{with sphinx}
BuildRequires:  python3-sphinx
%endif
%if %{without bootstrap}
BuildRequires:  bzip2-devel curl-devel expat-devel jsoncpp-devel libarchive-devel
BuildRequires:  libuv-devel rhash-devel xz-devel zlib-devel cmake-rpm-macros
%endif

Requires:       cmake-data = %{version}-%{release} cmake-rpm-macros = %{version}-%{release}
Requires:       cmake-filesystem = %{version}-%{release}
Provides:       cmake3 = %{version}-%{release} bundled(md5-deutsch) bundled(kwsys)

%description
CMake is used to control the software compilation process using simple
platform and compiler independent configuration files. CMake generates
native makefiles and workspaces that can be used in the compiler
environment of your choice. CMake is quite sophisticated: it is possible
to support complex environments requiring system configuration, preprocessor
generation, code generation, and template instantiation.

%package        data
Summary:        Common data-files for cmake
Requires:       cmake = %{version}-%{release} cmake-filesystem = %{version}-%{release}
Requires:       cmake-rpm-macros = %{version}-%{release}
Requires:       emacs-filesystem%{?_emacs_version: >= %{_emacs_version}}

BuildArch:      noarch

%description    data
This package contains common data-files for cmake.

%package        filesystem
Summary:        Directories used by CMake modules

%description    filesystem
This package owns all directories used by CMake modules.

%package        gui
Summary:        Qt GUI for cmake

Requires:       cmake = %{version}-%{release}
Requires:       hicolor-icon-theme
Requires:       shared-mime-info

%description    gui
The cmake-gui package contains the Qt based GUI for cmake.

%package        rpm-macros
Summary:        Common RPM macros for cmake
Requires:       rpm
Conflicts:      cmake-data < 3.10.1-2
BuildArch:      noarch

%description    rpm-macros
This package contains common RPM macros for cmake.

%package        help
Summary:        Documentation for cmake
Provides:       %{name}-doc = %{version}-%{release}
Obsoletes:      %{name}-doc < %{version}-%{release}
BuildArch:      noarch

%description    help
Documentation for cmake.

%prep
%autosetup -n cmake-%{version}%{?versuf} -p 1
sed '1c #!%{__python3}' %{SOURCE4} > cmake.prov
sed '1c #!%{__python3}' %{SOURCE5} > cmake.req

%build
export CFLAGS="%{optflags}"
export CXXFLAGS="%{optflags}"
export LDFLAGS="%{?__global_ldflags}"
mkdir build
pushd build
../bootstrap --prefix=%{_prefix} --datadir=/share/cmake \
             --docdir=/share/doc/cmake --mandir=/share/man \
             --%{?with_bootstrap:no-}system-libs \
             --parallel=`/usr/bin/getconf _NPROCESSORS_ONLN` \
%if %{with sphinx}
             --sphinx-man --sphinx-html \
%else
             --sphinx-build=%{_bindir}/false \
%endif
             --qt-gui \
;
%make_build VERBOSE=1

%install
install -d %{buildroot}%{_pkgdocdir}
%make_install -C build CMAKE_DOC_DIR=%{buildroot}%{_pkgdocdir}
find %{buildroot}%{_datadir}/cmake/Modules -type f | xargs chmod -x
for f in ccmake cmake cpack ctest;
do
 ln -s $f %{buildroot}%{_bindir}/${f}3;
done
install -d %{buildroot}%{_datadir}/bash-completion/completions
for f in %{buildroot}%{_datadir}/cmake/completions/*
do
  ln -s ../../cmake/completions/$(basename $f) %{buildroot}%{_datadir}/bash-completion/completions
done
install -d %{buildroot}%{_emacs_sitelispdir}/cmake
install -p -m 0644 Auxiliary/cmake-mode.el %{buildroot}%{_emacs_sitelispdir}/cmake/cmake-mode.el
%{_emacs_bytecompile} %{buildroot}%{_emacs_sitelispdir}/cmake/cmake-mode.el
install -d %{buildroot}%{_emacs_sitestartdir}
install -p -m 0644 %SOURCE1 %{buildroot}%{_emacs_sitestartdir}
install -p -m0644 -D %{SOURCE2} %{buildroot}%{rpm_macros_dir}/macros.cmake
sed -i -e "s|@@CMAKE_VERSION@@|%{version}|" -e "s|@@CMAKE_MAJOR_VERSION@@|3|" %{buildroot}%{rpm_macros_dir}/macros.cmake
touch -r %{SOURCE2} %{buildroot}%{rpm_macros_dir}/macros.cmake
install -p -m0644 -D %{SOURCE3} %{buildroot}%{_prefix}/lib/rpm/fileattrs/cmake.attr
install -p -m0755 -D cmake.prov %{buildroot}%{_prefix}/lib/rpm/cmake.prov
install -p -m0755 -D cmake.req %{buildroot}%{_prefix}/lib/rpm/cmake.req
install -d %{buildroot}%{_libdir}/cmake
find Source Utilities -type f -iname copy\*
cp -p Source/kwsys/Copyright.txt ./Copyright_kwsys
cp -p Utilities/KWIML/Copyright.txt ./Copyright_KWIML
cp -p Utilities/cmlibarchive/COPYING ./COPYING_cmlibarchive
cp -p Utilities/cmliblzma/COPYING ./COPYING_cmliblzma
cp -p Utilities/cmcurl/COPYING ./COPYING_cmcurl
cp -p Utilities/cmlibrhash/COPYING ./COPYING_cmlibrhash
cp -p Utilities/cmzlib/Copyright.txt ./Copyright_cmzlib
cp -p Utilities/cmexpat/COPYING ./COPYING_cmexpat
install -d %{buildroot}%{_pkgdocdir}
cp -pr %{buildroot}%{_datadir}/cmake/Help %{buildroot}%{_pkgdocdir}

desktop-file-install --delete-original \
  --dir=%{buildroot}%{_datadir}/applications \
  %{buildroot}%{_datadir}/applications/cmake-gui.desktop
install -d %{buildroot}%{_metainfodir}

find %{buildroot}%{_datadir}/cmake -type d | sed -e 's!^%{buildroot}!%%dir "!g' -e 's!$!"!g' > data_dirs.mf
find %{buildroot}%{_datadir}/cmake -type f | sed -e 's!^%{buildroot}!"!g' -e 's!$!"!g' > data_files.mf
find %{buildroot}%{_libdir}/cmake -type d | sed -e 's!^%{buildroot}!%%dir "!g' -e 's!$!"!g' > lib_dirs.mf
find %{buildroot}%{_libdir}/cmake -type f | sed -e 's!^%{buildroot}!"!g' -e 's!$!"!g' > lib_files.mf
find %{buildroot}%{_bindir} -type f -or -type l -or -xtype l | \
  sed -e '/.*-gui$/d' -e '/^$/d' -e 's!^%{buildroot}!"!g' -e 's!$!"!g' >> lib_files.mf

%check
#cd build
#export NO_TEST="CMake.FileDownload|CTestTestUpload|curl|RunCMake.CPack_RPM"
#bin/ctest -V -E "$NO_TEST" %{?_smp_mflags}

%post gui
update-desktop-database &> /dev/null || :
touch --no-create %{_datadir}/mime || :
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun gui
update-desktop-database &> /dev/null || :
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/mime || :
    update-mime-database %{_datadir}/mime &> /dev/null || :
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans gui
update-mime-database %{_datadir}/mime &> /dev/null || :
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files -f lib_files.mf
%doc %dir %{_pkgdocdir}
%license Copyright_* COPYING* Copyright.txt

%files data -f data_files.mf
%{_datadir}/aclocal/cmake.m4
%{_datadir}/bash-completion
%{_emacs_sitelispdir}/cmake
%{_emacs_sitelispdir}/cmake-mode.el
%{_emacs_sitestartdir}/cmake-init.el
%{_datadir}/vim/vimfiles/indent/%{name}.vim
%{_datadir}/vim/vimfiles//syntax/%{name}.vim

%files filesystem -f data_dirs.mf -f lib_dirs.mf

%files gui
%{_bindir}/cmake-gui
%{_datadir}/applications/cmake-gui.desktop
%{_datadir}/mime/packages
%{_datadir}/icons/hicolor/*/apps/CMake%{?name_suffix}Setup.png

%files rpm-macros
%{rpm_macros_dir}/macros.cmake
%{_rpmconfigdir}/fileattrs/cmake.attr
%{_rpmconfigdir}/cmake.prov
%{_rpmconfigdir}/cmake.req

%files help
%if %{with sphinx}
%{_mandir}/man1/ccmake.1.*
%{_mandir}/man1/cmake.1.*
%{_mandir}/man1/cpack.1.*
%{_mandir}/man1/ctest.1.*
%{_mandir}/man7/*.7.*
%{_mandir}/man1/cmake-gui.1.*
%endif
%doc %{_pkgdocdir}
%exclude %{_pkgdocdir}/Copyright.txt

%changelog
* Thu Jul 30 2020 wangchen <wangchen137@huawei.com> - 3.18.0-1
- Update to cmake-3.18.0

* Mon May 25 2020 licihua <licihua@huawei.com> - 3.17.2-1
- Update to cmake-3.17.2

* Fri Apr 03 2020 zhouyihang <zhouyihang1@huawei.com> - 3.12.1-6
- Remove useless scriptlet

* Mon Mar 23 2020 Xiangyang Yu <yuxiangyang4@huawei.com> -3.12.1-5
- add BuildRequires:gdb to fix src.rpm build error

* Thu Feb 20 2020 lijin Yang <yanglijin@huawei.com> -3.12.1-4
- make sphinx-build enable

* Wed Jan 22 2020 Yiru Wang <wangyiru1@huawei.com> - 3.12.1-3
- Disable test

* Fri Nov 29 2019 lijin Yang <yanglijin@huawei.com> - 3.12.1-2
- init package

