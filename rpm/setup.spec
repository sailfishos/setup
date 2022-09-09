Summary: A set of system configuration and setup files
Name: setup
Version: 0
Release: 1
License: Public Domain
URL: https://github.com/sailfishos/setup
Source0: %{name}-%{version}.tar.bz2
Patch0: 0001-setup-2.13.6-tcsh.patch
Patch1: 0002-dont-use-here-string.patch
BuildArch: noarch
#systemd: required to use _tmpfilesdir macro
BuildRequires: bash
BuildRequires: pkgconfig(systemd)

%description
The setup package contains a set of important system configuration and
setup files, such as passwd, group, and profile.

%package doc
Summary:   Documentation for %{name}
Requires:  %{name} = %{version}-%{release}

%description doc
%{summary}.

%prep
%autosetup -n %{name}-%{version}/setup

./shadowconvert.sh

%build

%check
# Run any sanity checks.
make check

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc/profile.d
mkdir -p %{buildroot}/etc/motd.d
cp -ar * %{buildroot}/etc
mv %{buildroot}/etc/lang* %{buildroot}/etc/profile.d/
rm -f %{buildroot}/etc/uidgid
rm -f %{buildroot}/etc/COPYING
mkdir -p %{buildroot}/var/log
touch %{buildroot}/var/log/lastlog
touch %{buildroot}/etc/environment
chmod 0644 %{buildroot}/etc/environment
chmod 0400 %{buildroot}/etc/{shadow,gshadow}
chmod 0644 %{buildroot}/var/log/lastlog
touch %{buildroot}/etc/fstab
mkdir -p %{buildroot}/etc/profile.d
echo "#Add any required envvar overrides to this file, it is sourced from /etc/profile" >%{buildroot}/etc/profile.d/sh.local
echo "#Add any required envvar overrides to this file, is sourced from /etc/csh.login" >%{buildroot}/etc/profile.d/csh.local
mkdir -p %{buildroot}/run/motd.d
touch %{buildroot}/run/motd
mkdir -p %{buildroot}/usr/lib/motd.d
touch %{buildroot}/usr/lib/motd
#tmpfiles needed for files in /run
mkdir -p %{buildroot}%{_tmpfilesdir}
echo "f /run/motd 0644 root root -" >%{buildroot}%{_tmpfilesdir}/%{name}.conf
echo "d /run/motd.d 0755 root root -" >>%{buildroot}%{_tmpfilesdir}/%{name}.conf
chmod 0644 %{buildroot}%{_tmpfilesdir}/%{name}.conf

# remove unpackaged files from the buildroot
rm -f %{buildroot}/etc/Makefile
rm -f %{buildroot}/etc/serviceslint
rm -f %{buildroot}/etc/uidgidlint
rm -f %{buildroot}/etc/shadowconvert.sh
rm -f %{buildroot}/etc/setup.spec
rm -rf %{buildroot}/etc/contrib

mkdir -p %{buildroot}%{_docdir}/%{name}-%{version}
install -m0644 uidgid %{buildroot}%{_docdir}/%{name}-%{version}

# At top: throw away useless and dangerous update stuff until rpm will be able
# to handle it ( http://rpm.org/ticket/6 )
# At bottom: Ensure that at least sh and bash are properly in place. See JB#53402
# That part is taken from Fedora's bash packaging and modified slightly
%post -p <lua>
for i, name in ipairs({"passwd", "shadow", "group", "gshadow"}) do
     os.remove("/etc/"..name..".rpmnew")
end
if posix.access("/usr/bin/newaliases", "x") then
  os.execute("/usr/bin/newaliases >/dev/null")
end

nl        = '\n'
sh        = '/bin/sh'..nl
usr_sh    = '%{_bindir}/sh'..nl
bash      = '/bin/bash'..nl
usr_bash  = '%{_bindir}/bash'..nl
f = io.open('/etc/shells', 'a+')
if f then
  local shells = nl..f:read('*all')..nl
  if not shells:find(nl..sh) then f:write(sh) end
  if not shells:find(nl..usr_sh) then f:write(usr_sh) end
  if not shells:find(nl..bash) then f:write(bash) end
  if not shells:find(nl..usr_bash) then f:write(usr_bash) end
  f:close()
end

%files
%defattr(-,root,root,-)
%license COPYING
%verify(not md5 size mtime) %config(noreplace) /etc/passwd
%verify(not md5 size mtime) %config(noreplace) /etc/group
%verify(not md5 size mtime) %attr(0000,root,root) %config(noreplace,missingok) /etc/shadow
%verify(not md5 size mtime) %attr(0000,root,root) %config(noreplace,missingok) /etc/gshadow
%verify(not md5 size mtime) %config(noreplace) /etc/subuid
%verify(not md5 size mtime) %config(noreplace) /etc/subgid
%config(noreplace) /etc/services
%verify(not md5 size mtime) %config(noreplace) /etc/exports
%config(noreplace) /etc/aliases
%config(noreplace) /etc/environment
%config(noreplace) /etc/filesystems
%config(noreplace) /etc/host.conf
%verify(not md5 size mtime) %config(noreplace) /etc/hosts
%verify(not md5 size mtime) %config(noreplace) /etc/motd
%dir /etc/motd.d
%verify(not md5 size mtime) %config(noreplace) /run/motd
%dir /run/motd.d
%verify(not md5 size mtime) %config(noreplace) /usr/lib/motd
%dir /usr/lib/motd.d
%config(noreplace) /etc/printcap
%verify(not md5 size mtime) %config(noreplace) /etc/inputrc
%config(noreplace) /etc/bashrc
%config(noreplace) /etc/profile
%config(noreplace) /etc/protocols
%config(noreplace) /etc/ethertypes
%config(noreplace) /etc/csh.login
%config(noreplace) /etc/csh.cshrc
%config(noreplace) /etc/networks
%dir /etc/profile.d
%config(noreplace) /etc/profile.d/sh.local
%config(noreplace) /etc/profile.d/csh.local
/etc/profile.d/lang.{sh,csh}
%config(noreplace) %verify(not md5 size mtime) /etc/shells
%ghost %attr(0644,root,root) %verify(not md5 size mtime) /var/log/lastlog
%ghost %verify(not md5 size mtime) %config(noreplace,missingok) /etc/fstab
%{_tmpfilesdir}/%{name}.conf

%files doc
%defattr(-,root,root,-)
%doc uidgid
%{_docdir}/%{name}-%{version}
