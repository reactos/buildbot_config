# ReactOS BuildBot Build Scripts
# config.inc - Shared settings for all builders
# Each setting can be overriden in a builder_config.inc

# Constants
if [ "$OS" = "Windows_NT" ]; then
	SOURCEDIR=`cygpath -am $PWD`
else
	SOURCEDIR="$PWD"
fi

TIME="../../time"
export LANG="C" LC_ALL=C

# Build Settings
ROSBE_DIR="/usr/local/RosBE"
WORKDIR="/mnt/ramdisk/buildbot"
export ROS_ARCH="i386"
export ROS_OUTPUT="$WORKDIR/output-MinGW-$ROS_ARCH"
export PATH="$ROSBE_DIR/$ROS_ARCH/bin:$ROSBE_DIR/bin:$PATH"
export _ROSBE_VERSION=`cat "/usr/local/RosBE/RosBE-Version"`

# CCache Settings
CCACHE_MEMORY="4G"
export CCACHE_HARDLINK=1
export CCACHE_DIR="/mnt/ramdisk/ccache"
export CCACHE_SLOPPINESS=time_macros

# Regression Testing Settings
TESTMAN_BUILDER="to be overriden in builder_config.inc"
TESTMAN_ID="to be overriden in builder_config.inc"
TESTMAN_PASS="to be overriden in builder_config.inc"

# Upload Settings
UPLOAD_HOST="10.94.0.12"
UPLOAD_ISODIR="/srv/iso/isostorage"
UPLOAD_KEY="$PWD/../../ssh_upload.key"
UPLOAD_REGTESTCD=1
UPLOAD_SUFFIX="to be overriden in builder_config.inc"
UPLOAD_USER="rosbuild"

# VBox Settings
VBOX_VM_NAME="to be overriden in builder_config.inc"

# VMware Settings
VMWARE_SERIAL_FILE="to be overriden in builder_config.inc"
VMWARE_VMDK_FILE="to be overriden in builder_config.inc"
VMWARE_VMX_FILE="to be overriden in builder_config.inc"

# Allow additional configuration and overrides in a local per-builder config
source ../builder_config.inc
