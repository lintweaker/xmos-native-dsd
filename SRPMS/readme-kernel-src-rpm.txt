[24-Oct-14] Jurgen Kramer

There is no kernel source RPM here, it is too big.

-Instructions for creating a proper kernel SRPM yourself

Prerequisites:
Fedora 20, fully updated. Prepared for kernel building (see: https://fedoraproject.org/wiki/Building_a_custom_kernel)

Example for kernel 3.16.6:

Download kernel 3.16.6 SRPM from koji:
wget https://kojipkgs.fedoraproject.org//packages/kernel/3.16.6/202.fc20/src/kernel-3.16.6-202.fc20.src.rpm

Install it (as non-root user):
rpm -ivh kernel-3.16.6-202.fc20.src.rpm

Copy the needed patches from this repo to the rpmbuild/SOURCES directory:

cp SRPMS/patches/* ~/rpmbuild/SOURCES

Replace the SPEC file:

cp SPECS/kernel.spec ~/rpmbuild/SPECS

Build new SRPM:

cd ~/rpmbuild/SPECS
rpmbuild -bs kernel.spec







