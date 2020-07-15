# modify the kernel.spec file for lustre per
# https://wiki.whamcloud.com/pages/viewpage.action?pageId=54428329

import re
import sys

pat_build_root = re.compile(r'(^\s*)(find \$RPM_BUILD_ROOT/lib/modules/\$KernelVer)')
pat_empty_final = re.compile(r'# empty final patch to facilitate testing of kernel patches')
pat_apply_optional = re.compile(r'ApplyOptionalPatch linux-kernel-test\.patch')
pat_listnewconfig = re.compile(r'\%define listnewconfig_fail 1')

for line in sys.stdin:
    if pat_build_root.search(line):
        # grab the leading whitespace if any
        lw = re.match(r'\s*', line).group()
        print('pat_build_root', file=sys.stderr)
        print(line, end='')
        print(lw + 'cp -a fs/ext3/* $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/fs/ext3')
        print(lw + 'cp -a fs/ext4/* $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/fs/ext4')

    elif pat_empty_final.search(line):
        print('pat_empty_final', file=sys.stderr)
        print(line, end='')
        print('# adds Lustre patches')
        print('Patch99995: patch-%{version}-lustre.patch')

    elif pat_apply_optional.match(line):
        print('pat_apply_optional', file=sys.stderr)
        print(line, end='')
        print('# lustre patch')
        print('ApplyOptionalPatch patch-%{version}-lustre.patch')

    elif pat_listnewconfig.match(line):
        print('pat_listnewconfig', file=sys.stderr)
        print('%define listnewconfig_fail 0')

    else:
        print(line, end='')