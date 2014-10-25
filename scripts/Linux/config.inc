# ReactOS BuildBot Build Scripts for Linux
# config.inc - Shared settings for all builders
# Each setting can be overriden in a builder_config.inc

# Constants
TIME="../../time"
export LANG="C"

# Build Settings
WORKDIR="/mnt/ramdisk/buildbot"
export ROS_ARCH="i386"
export ROS_OUTPUT="$WORKDIR/output-MinGW-$ROS_ARCH"
export PATH="/usr/local/RosBE/$ROS_ARCH/bin:/usr/local/RosBE/bin:$PATH"
export _ROSBE_VERSION=`cat "/usr/local/RosBE/RosBE-Version"`

# ccache
CCACHE_MEMORY="4G"
export CCACHE_HARDLINK=1
export CCACHE_DIR="/mnt/ramdisk/ccache"
export CCACHE_SLOPPINESS=time_macros

# Regression Testing Settings
REGTESTCD_DIR="to be overriden in builder_config.inc"
TESTMAN_BUILDER="to be overriden in builder_config.inc"
TESTMAN_ID="to be overriden in builder_config.inc"
TESTMAN_PASS="to be overriden in builder_config.inc"

# Upload Settings
UPLOAD_SUFFIX="to be overriden in builder_config.inc"

# Allow additional configuration and overrides in a local per-builder config
source ../builder_config.inc