inherit bundle

CURRENT_RECIPE_DIR := "${@os.path.dirname(d.getVar('FILE'))}"
META_LAYER_DIR := "${@os.path.dirname(os.path.dirname('${CURRENT_RECIPE_DIR}'))}"

RAUC_BUNDLE_FORMAT = "verity"
RAUC_KEY_FILE = "${META_LAYER_DIR}/files/development-1.key.pem"
RAUC_CERT_FILE = "${META_LAYER_DIR}/files/development-1.cert.pem"

RAUC_BUNDLE_COMPATIBLE = "${MACHINE}${TARGET_VENDOR}"

RAUC_BUNDLE_SLOTS = "rootfs"
RAUC_SLOT_rootfs = "core-image-minimal"

