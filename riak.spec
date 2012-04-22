# TODO:
# - package dependencies separately
Name:		riak
Version:	1.1.2
Release:	0
License:	Apache
Group:		Development/Libraries
Source0:	http://downloads.basho.com/riak/CURRENT/%{name}-%{version}.tar.gz
# Source0-md5:	2820cc52942c778656d9dc839247dbb4
Source1:	%{name}.init
Source2:	%{name}.tmpfiles.conf
Summary:	Riak Distributed Data Store
URL:		http://basho.com
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Riak is a distrubuted data store.

%prep
%setup -q
cat > rel/vars.config <<EOF
% app.config
{web_ip,       "127.0.0.1"}.
{web_port,     8098}.
{handoff_port, 8099}.
{pb_ip,        "127.0.0.1"}.
{pb_port,      8087}.
{ring_state_dir,        "%{_sharedstatedir}/%{name}/ring"}.
{bitcask_data_root,     "%{_sharedstatedir}/%{name}/bitcask"}.
{leveldb_data_root,     "%{_sharedstatedir}/%{name}/leveldb"}.
{merge_index_data_root,    "%{_sharedstatedir}/%{name}/merge_index"}.
{merge_index_data_root_2i, "%{_sharedstatedir}/%{name}/merge_index_2i"}.
{sasl_error_log,        "/var/log/%{name}/sasl-error.log"}.
{sasl_log_dir,          "/var/log/%{name}/sasl"}.
{mapred_queue_dir,      "%{_sharedstatedir}/%{name}/mr_queue"}.
{map_js_vms,   8}.
{reduce_js_vms, 6}.
{hook_js_vms, 2}.
% Platform-specific installation paths
{platform_bin_dir,  "%{_bindir}"}.
{platform_data_dir, "%{_sharedstatedir}/%{name}"}.
{platform_etc_dir, "%{_sysconfdir}/%{name}"}.
{platform_lib_dir,  "%{_libdir}/%{name}"}.
{platform_log_dir,  "/var/log/%{name}"}.
% vm.args
{node,              "riak@127.0.0.1"}.
{crash_dump,        "/var/log/%{name}/erl_crash.dump"}.
% bin/riak*
{runner_script_dir,  "%{_bindir}"}.
{runner_base_dir,    "%{_libdir}/%{name}"}.
{runner_etc_dir, "%{_sysconfdir}/%{name}"}.
{runner_log_dir,     "/var/log/%{name}"}.
{pipe_dir,           "%{_varrun}/%{name}/"}.
{runner_user,        "%{name}"}.
EOF
cp rel/files/riak rel/files/riak.tmp
sed -e "s/^RIAK_VERSION.*$/RIAK_VERSION=\"%{_versionstring}\"/" < rel/files/riak.tmp > rel/files/riak

%build
mkdir %{name}
%{__make} rel

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/riak
install -d $RPM_BUILD_ROOT%{_libdir}/%{name}
install -d $RPM_BUILD_ROOT%{_mandir}/man1
install -d $RPM_BUILD_ROOT%{_sharedstatedir}/%{name}/dets
install -d $RPM_BUILD_ROOT%{_sharedstatedir}/%{name}/bitcask
install -d $RPM_BUILD_ROOT%{_sharedstatedir}/%{name}/leveldb
install -d $RPM_BUILD_ROOT%{_sharedstatedir}/%{name}/ring
install -d $RPM_BUILD_ROOT%{_sharedstatedir}/%{name}/merge_index
install -d $RPM_BUILD_ROOT/var/log/%{name}
install -d $RPM_BUILD_ROOT/var/log/%{name}/sasl
install -d $RPM_BUILD_ROOT%{_varrun}/%{name}
install -d $RPM_BUILD_ROOT%{_sharedstatedir}/%{name}/mr_queue

#Copy all necessary lib files etc.
cp -r rel/%{name}/lib $RPM_BUILD_ROOT%{_libdir}/%{name}/
cp -r rel/%{name}/erts-* \
		$RPM_BUILD_ROOT%{_libdir}/%{name}
cp -r rel/%{name}/releases \
		$RPM_BUILD_ROOT%{_libdir}/%{name}
cp -r doc/man/man1/*.gz \
		$RPM_BUILD_ROOT%{_mandir}/man1
install -p -D \
rel/%{name}%{_sysconfdir}/app.config \
$RPM_BUILD_ROOT%{_sysconfdir}/riak/
install -p -D \
rel/%{name}%{_sysconfdir}/vm.args \
$RPM_BUILD_ROOT%{_sysconfdir}/riak/
install -p -D \
	rel/%{name}/bin/%{name} \
	$RPM_BUILD_ROOT/%{_bindir}/%{name}
install -p -D \
	rel/%{name}/bin/%{name}-admin \
	$RPM_BUILD_ROOT/%{_bindir}/%{name}-admin
install -p -D \
	rel/%{name}/bin/search-cmd \
	$RPM_BUILD_ROOT/%{_bindir}/search-cmd

install -d $RPM_BUILD_ROOT/etc/rc.d/init.d/
install -p -D %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

install -d $RPM_BUILD_ROOT/%{_sysconfdir}/tmpfiles.d/
install %{SOURCE2} $RPM_BUILD_ROOT/%{_sysconfdir}/tmpfiles.d/%{name}.conf

%pre
%groupadd -g 281 riak
%useradd -u 281 -d %{_sharedstatedir}/%{name} -s /bin/sh -g riak -c "Riak Server" riak

%post
[ ! -x /usr/sbin/fix-info-dir ] || /usr/sbin/fix-info-dir -c %{_infodir} >/dev/null 2>&1
/sbin/ldconfig
/sbin/chkconfig --add riak
%service riak restart

%files
%defattr(644,root,root,755)
%attr(-,root,root) %{_libdir}/*
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/*
%config(noreplace) %{_sysconfdir}/tmpfiles.d/%{name}.conf
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(755,root,root) %{_bindir}/%{name}
%attr(755,root,root) %{_bindir}/%{name}-admin
%attr(755,root,root) %{_bindir}/search-cmd
%{_mandir}/man1/*
%attr(770,riak,riak) %{_sharedstatedir}/%{name}
%attr(751,riak,root) %dir /var/log/%{name}
%attr(751,riak,root) %dir /var/log/%{name}/sasl
%{_varrun}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT
