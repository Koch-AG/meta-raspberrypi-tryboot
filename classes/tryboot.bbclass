
python do_tryboot_preprocess() {
    import os
    import shutil
    import subprocess

    # Create a temporary directory
    tmpdir = d.getVar('WORKDIR', True) + "/tryboot-tmp"
    bb.utils.remove(tmpdir, True)
    os.makedirs(tmpdir)

    # Create the autoboot.txt file
    autoboot_path = tmpdir + "/autoboot.txt"
    with open(autoboot_path, 'w') as f:
        f.write("[all]\n")
        f.write("tryboot_a_b=1\n")
        f.write("boot_partition=2\n")

    # Create the tryboot.img file
    tryboot_img_path = tmpdir + "/tryboot.img"
    subprocess.run(["dd", "if=/dev/zero", f"of={tryboot_img_path}", "bs=1M", "count=10"], check=True)
    subprocess.run(["mkfs.vfat", tryboot_img_path], check=True)
    subprocess.run(["mcopy", "-i", tryboot_img_path, autoboot_path, "::"], check=True)

    # Copy the tryboot.img to the deployment directory
    deploy_dir = d.getVar('DEPLOY_DIR_IMAGE', True)
    shutil.copy(tryboot_img_path, deploy_dir)

    # Clean up
    bb.utils.remove(tmpdir, True)
}

do_tryboot_preprocess[depends] += "dosfstools-native:do_populate_sysroot"
do_tryboot_preprocess[depends] += "mtools-native:do_populate_sysroot"
addtask do_tryboot_preprocess after do_rootfs before do_image_wic

