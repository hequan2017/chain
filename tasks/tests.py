
a ={'SDF': {'task0': {'cmd': 'pwd', 'stdout': '/home/hequan', 'stderr': '', 'rc': 0, 'start': '2018-04-12 15:32:41.836286', 'end': '2018-04-12 15:32:41.841759', 'delta': '0:00:00.005473', 'changed': True, 'invocation': {'module_args': {'_raw_params': 'pwd', '_uses_shell': True, 'warn': True, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, '_ansible_parsed': True, 'stdout_lines': ['/home/hequan'], 'stderr_lines': [], '_ansible_no_log': False}, 'task1': {'cmd': 'hostname', 'stdout': 'k8s_master', 'stderr': '', 'rc': 0, 'start': '2018-04-12 15:32:42.679044', 'end': '2018-04-12 15:32:42.684143', 'delta': '0:00:00.005099', 'changed': True, 'invocation': {'module_args': {'_raw_params': 'hostname', '_uses_shell': True, 'warn': True, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, '_ansible_parsed': True, 'stdout_lines': ['k8s_master'], 'stderr_lines': [], '_ansible_no_log': False}}, 'devops': {'task0': {'changed': True, 'end': '2018-04-12 15:32:41.905235', 'stdout': '/home/hequan', 'cmd': 'pwd', 'rc': 0, 'start': '2018-04-12 15:32:41.894985', 'stderr': '', 'delta': '0:00:00.010250', 'invocation': {'module_args': {'creates': None, 'executable': None, '_uses_shell': True, '_raw_params': 'pwd', 'removes': None, 'warn': True, 'chdir': None, 'stdin': None}}, '_ansible_parsed': True, 'stdout_lines': ['/home/hequan'], 'stderr_lines': [], '_ansible_no_log': False}, 'task1': {'changed': True, 'end': '2018-04-12 15:32:42.775568', 'stdout': 'devops', 'cmd': 'hostname', 'rc': 0, 'start': '2018-04-12 15:32:42.765349', 'stderr': '', 'delta': '0:00:00.010219', 'invocation': {'module_args': {'creates': None, 'executable': None, '_uses_shell': True, '_raw_params': 'hostname', 'removes': None, 'warn': True, 'chdir': None, 'stdin': None}}, '_ansible_parsed': True, 'stdout_lines': ['devops'], 'stderr_lines': [], '_ansible_no_log': False}}}

import pprint
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(a)
hostname = ['SDF','devops']


ret1 = {}
c = []

for i in range(len(hostname)):
    b= []
    ret1 = {}
    n = hostname[i]
    for t in range(2):
        print(n,a[n]['task{}'.format(t)]['stdout'])
        b.append(a[n]['task{}'.format(t)]['stdout'])
    ret1['hostname']=n
    ret1['data']='\n'.join(b)
        # print(ret1)
    c.append(ret1)


print(c)
