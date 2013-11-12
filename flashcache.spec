%{?!kernel:%define kernel %(rpm -q kernel-devel | tail -1 | sed -e 's|kernel-devel-||')}
%define kversion %(echo "%{kernel}" | sed -e 's|-.*||')
%define krelease %(echo "%{kernel}" | sed -e 's|.*-||')
%define kernel_moduledir /lib/modules/%{kernel}
%define kernel_src_path %{kernel_moduledir}/source

Summary: A write-back block cache for Linux
Name: flashcache
Vendor: flashcache development, https://github.com/facebook/flashcache
Version: 3.1.1
Release: 3%{?dist}
License: GPL
Group: System Environment/Base
URL: https://github.com/facebook/flashcache/
Packager: Daniel Carneiro <daniel@bluesoft.com.br>
#Source0: %{name}-%{version}.tar.gz
#Patch0: flashcache-sysvinit.patch
Requires(post): /sbin/chkconfig dkms gcc make kernel-devel
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: x86_64
BuildRequires: tar gcc make kernel-devel rpm-build git
ExclusiveArch: x86_64

%description
Flashcache : A write-back block cache for Linux

%package -n kmod-%{name}
Summary: kernel modules for flashcache
Vendor: flashcache development, https://github.com/facebook/flashcache
Version: 3.1.1
#Release: 3%{?dist}
Group: System Environment/Kernel
Requires: dkms >= 1.00
Requires: bash
Requires(post): /sbin/depmod
Requires(postun): /sbin/depmod

%description -n kmod-%{name}
kernel modules for flashcache

%prep
rm -rf %{name}-%{version}
git clone https://github.com/facebook/flashcache.git %{name}-%{version}
cd %{name}-%{version}
git checkout %{version}

%install
if [ "$RPM_BUILD_ROOT" != "/" ]; then
	rm -rf $RPM_BUILD_ROOT
fi
mkdir -p $RPM_BUILD_ROOT/usr/src/%{name}-%{version}/
rsync -r %{name}-%{version}/src/ $RPM_BUILD_ROOT/usr/src/%{name}-%{version}/
make DESTDIR=$RPM_BUILD_ROOT -C %{name}-%{version}/src/utils install
sed "s/PACKAGE_VERSION=/PACKAGE_VERSION=%{version}/" %{name}-%{version}/src/dkms.conf > "$RPM_BUILD_ROOT/usr/src/%{name}-%{version}/dkms.conf"

%files
/usr/src/%{name}-%{version}/
/sbin/*

%post
dkms add -m %{name} -v %{version} --rpm_safe_upgrade
dkms build -m %{name} -v %{version} --rpm_safe_upgrade
dkms install -m %{name} -v %{version} --rpm_safe_upgrade

%preun
dkms remove -m %{name} -v %{version} --all --rpm_safe_upgrade
