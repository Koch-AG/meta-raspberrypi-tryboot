#
# Copyright OpenEmbedded Contributors
#
# SPDX-License-Identifier: GPL-2.0-only
#
# DESCRIPTION
# This implements the 'bootimg-partition' source plugin class for
# 'wic'. The plugin creates an image of boot partition, copying over
# files listed in IMAGE_BOOT_FILES bitbake variable.
#
# AUTHORS
# Maciej Borzecki <maciej.borzecki (at] open-rnd.pl>
#

import logging
import os
import re

from glob import glob

from wic import WicError
from wic.engine import get_custom_config
from wic.pluginbase import SourcePlugin
from wic.misc import exec_cmd, get_bitbake_var

logger = logging.getLogger('wic')

class BootimgModify(SourcePlugin):
    """
    Create an image of boot partition, copying over files
    listed in IMAGE_BOOT_FILES bitbake variable.
    """

    name = 'bootimg-modify'
    image_boot_files_var_name = 'IMAGE_BOOT_FILES'

    @classmethod
    def do_configure_partition(cls, part, source_params, cr, cr_workdir,
                             oe_builddir, bootimg_dir, kernel_dir,
                             native_sysroot):
        """
        Called before do_prepare_partition(), create u-boot specific boot config
        """
        hdddir = "%s/boot.%d" % (cr_workdir, part.lineno)
        install_cmd = "install -d %s" % hdddir
        exec_cmd(install_cmd)

        boot_files = get_bitbake_var(cls.image_boot_files_var_name)
        if boot_files is None:
            raise WicError('No boot files defined, %s unset for entry #%d' % (cls.image_boot_files_var_name, part.lineno))

        logger.debug('Boot files: %s', boot_files)

        # list of tuples (src_name, dst_name)
        deploy_files = []
        for src_entry in re.findall(r'[\w;\-\./\*]+', boot_files):
            if ';' in src_entry:
                dst_entry = tuple(src_entry.split(';'))
                if not dst_entry[0] or not dst_entry[1]:
                    raise WicError('Malformed boot file entry: %s' % src_entry)
            else:
                dst_entry = (src_entry, src_entry)

            logger.debug('Destination entry: %r', dst_entry)
            deploy_files.append(dst_entry)

        cls.install_task = [];
        for deploy_entry in deploy_files:
            src, dst = deploy_entry
            if '*' in src:
                # by default install files under their basename
                entry_name_fn = os.path.basename
                if dst != src:
                    # unless a target name was given, then treat name
                    # as a directory and append a basename
                    entry_name_fn = lambda name: \
                                    os.path.join(dst,
                                                 os.path.basename(name))

                srcs = glob(os.path.join(kernel_dir, src))

                logger.debug('Globbed sources: %s', ', '.join(srcs))
                for entry in srcs:
                    src = os.path.relpath(entry, kernel_dir)
                    entry_dst_name = entry_name_fn(entry)
                    cls.install_task.append((src, entry_dst_name))
            else:
                cls.install_task.append((src, dst))


    @classmethod
    def do_prepare_partition(cls, part, source_params, cr, cr_workdir,
                             oe_builddir, bootimg_dir, kernel_dir,
                             rootfs_dir, native_sysroot):
        """
        Called to do the actual content population for a partition i.e. it
        'prepares' the partition to be incorporated into the image.
        In this case, does the following:
        - sets up a vfat partition
        - copies all files listed in IMAGE_BOOT_FILES variable
        """
        hdddir = "%s/boot.%d" % (cr_workdir, part.lineno)

        if not kernel_dir:
            kernel_dir = get_bitbake_var("DEPLOY_DIR_IMAGE")
            if not kernel_dir:
                raise WicError("Couldn't find DEPLOY_DIR_IMAGE, exiting")

        logger.debug('Kernel dir: %s', bootimg_dir)


        for task in cls.install_task:
            src_path, dst_path = task
            logger.debug('Install %s as %s', src_path, dst_path)
            install_cmd = "install -m 0644 -D %s %s" \
                          % (os.path.join(kernel_dir, src_path),
                             os.path.join(hdddir, dst_path))
            exec_cmd(install_cmd)



        cmdline_path = os.path.join(hdddir, "cmdline.txt")

        if not os.path.exists(cmdline_path):
            raise FileNotFoundError(f"cmdline.txt not found in {hdddir}")

        # Read new_root argument from WKS file
        new_root = source_params.get("root")
        if not new_root:
            raise ValueError(f"Missing 'root' argument in partition {part.mountpoint}")

        # Modify cmdline.txt
        with open(cmdline_path, "r") as f:
            cmdline = f.read()

        new_cmdline = cmdline.replace("root=/dev/mmcblk0p2", f"root={new_root}")

        with open(cmdline_path, "w") as f:
            f.write(new_cmdline)

        print(f"Updated {cmdline_path} to root={new_root}")



        logger.debug('Prepare boot partition using rootfs in %s', hdddir)
        part.prepare_rootfs(cr_workdir, oe_builddir, hdddir,
                            native_sysroot, False)
