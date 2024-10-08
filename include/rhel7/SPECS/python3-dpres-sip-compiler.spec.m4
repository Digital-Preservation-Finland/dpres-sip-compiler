# vim:ft=spec

%define file_prefix M4_FILE_PREFIX
%define file_ext M4_FILE_EXT
%define file_version M4_FILE_VERSION
%define file_release_tag %{nil}M4_FILE_RELEASE_TAG
%define file_release_number M4_FILE_RELEASE_NUMBER
%define file_build_number M4_FILE_BUILD_NUMBER
%define file_commit_ref M4_FILE_COMMIT_REF

Name:           python3-dpres-sip-compiler
Version:        %{file_version}
Release:        %{file_release_number}%{file_release_tag}.%{file_build_number}.git%{file_commit_ref}%{?dist}
Summary:        Submission Information Package (SIP) Compiler for Tailored Usage.
Group:          Applications/Archiving
License:        LGPLv3+
URL:            https://www.digitalpreservation.fi
Source0:        %{file_prefix}-v%{file_version}%{?file_release_tag}-%{file_build_number}-g%{file_commit_ref}.%{file_ext}
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
Requires:       python3 python36-click python3-dpres-siptools
Requires:       python3-dpres-mets-builder python3-dpres-siptools-ng
BuildRequires:  python3-setuptools python3-file-scraper-full openssl-devel

%description
Submission Information Package (SIP) Compiler for Tailored Usage.

%prep
%setup -n %{file_prefix}-v%{file_version}%{?file_release_tag}-%{file_build_number}-g%{file_commit_ref}

%build

%install
rm -rf $RPM_BUILD_ROOT
make install3 PREFIX="%{_prefix}" ROOT="%{buildroot}"

# Rename executables to prevent naming collision with Python 2 RPM
mv %{buildroot}%{_bindir}/sip-compiler %{buildroot}%{_bindir}/sip-compiler-3
sed -ie '/^\/usr\/bin/ s/$/-3/g' INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root,-)
/usr/bin/*-3

# TODO: For now changelog must be last, because it is generated automatically
# from git log command. Appending should be fixed to happen only after %changelog macro
%changelog
