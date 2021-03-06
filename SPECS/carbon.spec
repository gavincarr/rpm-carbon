%if %rhel < 6
%define python_sitelib  %(%{__python} -c "from distutils.sysconfig import get_python_lib; import sys; sys.stdout.write(get_python_lib())")
%define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; import sys; sys.stdout.write(get_python_lib(1))")
%define python_version  %(%{__python} -c "import sys; sys.stdout.write(sys.version[:3])")
%endif

Summary:    Backend data caching and persistence daemon for Graphite
Name:       carbon
Version:    0.9.9
Release:    3%{?dist}
Source0:    %{name}-%{version}.tar.gz
Source1:    carbon-cache.init
Source2:    carbon-relay.init
Source3:    carbon-aggregator.init
Source4:    carbon.conf
Source5:    carbon-storage-schemas.conf
Patch0:     %{name}-0.9.9-fhs-compliance.patch
License:    Apache Software License 2.0
Group:      System Environment/Daemons
BuildArch:  noarch
URL:        https://launchpad.net/graphite
Requires:   whisper >= %{version}
Requires:   python-twisted
Requires:   python-txamqp
Requires:   python-zope-interface
Obsoletes:  python-carbon

%description
Carbon is the backend storage application of the graphite framework,
providing data collection, caching and persistence services.

%prep
%setup
%patch0 -p1

%build
%{__python} setup.py build

%install
%{__python} setup.py install --root=%{buildroot}

install -d -m 0755 %{buildroot}%{_sysconfdir}
install -d -m 0755 %{buildroot}%{_initrddir}
install -d -m 0755 %{buildroot}%{_localstatedir}/lib/carbon
install -d -m 0755 %{buildroot}%{_localstatedir}/log/graphite/carbon-cache
install -d -m 0755 %{buildroot}%{_localstatedir}/run/graphite

mv %{buildroot}/usr/conf %{buildroot}%{_sysconfdir}/graphite
install -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/graphite/carbon.conf
install -m 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/graphite/storage-schemas.conf

install -m 0755 %{SOURCE1} %{buildroot}%{_initrddir}/carbon-cache
install -m 0755 %{SOURCE2} %{buildroot}%{_initrddir}/carbon-relay
install -m 0755 %{SOURCE3} %{buildroot}%{_initrddir}/carbon-aggregator

find %{buildroot} -type f -name \*~\* -exec rm {} +

%clean
rm -rf %{buildroot}

%pre
getent group graphite >/dev/null || groupadd -r graphite
getent passwd graphite >/dev/null || \
    useradd -r -g graphite -d '/etc/graphite' -s /sbin/nologin \
    -c "Graphite Service User" graphite

%post
for svc in carbon-{aggregator,cache,relay}; do
    /sbin/chkconfig --add "$svc"
done

%preun
if [ $1 -eq 0 ]; then
    for svc in carbon-{aggregator,cache,relay}; do
        /sbin/service "$svc" stop >/dev/null 2>&1
        /sbin/chkconfig --del "$svc"
    done
fi

%postun
if [ $1 -ge 1 ]; then
    for svc in carbon-{aggregator,cache,relay}; do
        /sbin/service "$svc" condrestart >/dev/null 2>&1 || :
    done
fi

%files
%defattr(-,root,root)
%dir %{_sysconfdir}/graphite
%{_initrddir}/carbon-aggregator
%{_initrddir}/carbon-cache
%{_initrddir}/carbon-relay
%config(noreplace) %{_sysconfdir}/graphite/*.conf
%{_sysconfdir}/graphite/*.example
%{_bindir}/carbon-aggregator.py
%{_bindir}/carbon-cache.py
%{_bindir}/carbon-client.py
%{_bindir}/carbon-relay.py
%{_bindir}/validate-storage-schemas.py
%if %rhel >= 6
%{python_sitelib}/%{name}-%{version}-py%{python_version}.egg-info
%endif
%{python_sitelib}/%{name}/*.py
%{python_sitelib}/%{name}/*.pyc
%{python_sitelib}/%{name}/*.pyo
%{python_sitelib}/%{name}/amqp0-8.xml
%{python_sitelib}/%{name}/aggregator/*.py
%{python_sitelib}/%{name}/aggregator/*.pyc
%{python_sitelib}/%{name}/aggregator/*.pyo
%attr(0755,graphite,graphite) %{_localstatedir}/lib/carbon
%attr(0755,graphite,graphite) %{_localstatedir}/log/graphite
%attr(0755,graphite,graphite) %{_localstatedir}/log/graphite/carbon-cache
%attr(0755,graphite,graphite) %{_localstatedir}/run/graphite

# This is questionable and should probably be split into another package
%{python_sitelib}/twisted/plugins/carbon_aggregator_plugin.py
%{python_sitelib}/twisted/plugins/carbon_aggregator_plugin.pyc
%{python_sitelib}/twisted/plugins/carbon_aggregator_plugin.pyo
%{python_sitelib}/twisted/plugins/carbon_cache_plugin.py
%{python_sitelib}/twisted/plugins/carbon_cache_plugin.pyc
%{python_sitelib}/twisted/plugins/carbon_cache_plugin.pyo
%{python_sitelib}/twisted/plugins/carbon_relay_plugin.py
%{python_sitelib}/twisted/plugins/carbon_relay_plugin.pyc
%{python_sitelib}/twisted/plugins/carbon_relay_plugin.pyo

%changelog
* Sun Nov  6 2011 Jeff Goldschrafe <jeff@holyhandgrenade.org> - 0.9.9-3
- Rename python-carbon to carbon

* Fri Nov  4 2011 Jeff Goldschrafe <jeff@holyhandgrenade.org> - 0.9.9-2
- Add graphite user/group
- Add init scripts
- Add /var/run/graphite to store PIDs

* Wed Oct 26 2011 Jeff Goldschrafe <jeff@holyhandgrenade.org> - 0.9.9-1
- Bump to version 0.9.9

* Wed Oct 26 2011 Jeffrey Goldschrafe <jeff@holyhandgrenade.org> - 0.9.7-1
- Initial package for Fedora
