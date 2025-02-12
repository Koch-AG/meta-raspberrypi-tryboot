import logging
import os

from wic.pluginbase import SourcePlugin
from wic.misc import exec_cmd

logger = logging.getLogger('wic')

class TrybootPartitionPlugin(SourcePlugin):

    name = 'tryboot-partition'

    @classmethod
    def do_configure_partition(cls, part, source_params, cr, cr_workdir,
                             oe_builddir, bootimg_dir, kernel_dir,
                             native_sysroot):
        hdddir = f"{cr_workdir}/boot.{part.lineno}"
        install_cmd = f"install -d {hdddir}"
        exec_cmd(install_cmd)

        autoboot = ""
        autoboot += "[all]\n"
        autoboot += "tryboot_a_b=1\n"
        autoboot += "boot_partition=2\n"

        cfg = open(f"{hdddir}/autoboot.txt", "w")
        cfg.write(autoboot)
        cfg.close()


    @classmethod
    def do_prepare_partition(cls, part, source_params, cr, cr_workdir,
                             oe_builddir, bootimg_dir, kernel_dir,
                             rootfs_dir, native_sysroot):
        hdddir = f"{cr_workdir}/boot.{part.lineno}"

        logger.debug(f"Prepare boot partition using rootfs in {hdddir}")
        part.prepare_rootfs(cr_workdir, oe_builddir, hdddir,
                            native_sysroot, False)
