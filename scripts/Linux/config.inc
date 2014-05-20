SOURCEDIR="$PWD"
TIME="../../time"
WORKDIR="/mnt/ramdisk/buildbot"

export J="-j9"
export LANG="C"
export ROS_ARCH=i386
export ROS_OUTPUT="$WORKDIR/output-MinGW-$ROS_ARCH"
export PATH="/usr/local/RosBE/$ROS_ARCH/bin:/usr/local/RosBE/bin:$PATH"

# ccache
export CCACHE_HARDLINK=1
export CCACHE_DIR="/mnt/ramdisk/ccache"
export CCACHE_SLOPPINESS=time_macros

# Dummy var
export _ROSBE_VERSION=`cat "/usr/local/RosBE/RosBE-Version"`
