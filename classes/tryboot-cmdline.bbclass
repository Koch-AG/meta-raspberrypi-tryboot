
def get_wic_image(d):
    import os

    work_dir = d.getVar("WORKDIR")
    image_link_name = d.getVar("IMAGE_NAME")
    wic_image = os.path.join(work_dir, "deploy-" + d.getVar("PN") + "-image-complete", f"{image_link_name}.wic")

    if not os.path.exists(wic_image):
        bb.fatal(f"No WIC image found! {wic_image}")

    return wic_image


def get_partitions(wic_image):
    import subprocess

    fdisk_output = subprocess.check_output(["fdisk", "-l", "-o", "Start,Type", wic_image], text=True)
    vfat_partitions = []

    for line in fdisk_output.splitlines():
        if "FAT" in line:
            offset_blocks = int(line.split()[0])
            offset_bytes = offset_blocks * 512
            partition = f"{wic_image}@@{offset_bytes}"
            vfat_partitions.append(partition)

    return vfat_partitions


def update_cmdline(partition, root):
    import subprocess

    cmdline_data = subprocess.check_output([
        "mtype", "-i", partition, "::cmdline.txt"
    ], text=True)

    new_cmdline = cmdline_data.replace("root=XXX", f"root={root}")

    subprocess.run([
        "mcopy", "-Do", "-i", partition, "-", "::cmdline.txt"
    ], input=new_cmdline, text=True, check=True)


python do_update_tryboot_cmdline() {
    wic_image = get_wic_image(d)
    vfat_partitions = get_partitions(wic_image)

    update_cmdline(vfat_partitions[1], "/dev/mmcblk0p5")
    update_cmdline(vfat_partitions[2], "/dev/mmcblk0p6")
}

addtask do_update_tryboot_cmdline after do_image_wic before do_image_complete

