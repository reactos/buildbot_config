SOURCEDIR="$PWD"
TIME="../../time"
WORKDIR="/mnt/ramdisk/buildbot"

export J="-j9"
export LANG="C"
export ROS_ARCH=i386
export ROS_OUTPUT="$WORKDIR/output-MinGW-$ROS_ARCH"
export PATH="/usr/local/RosBE-2.1.1/$ROS_ARCH/bin:/usr/local/RosBE-2.1.1/bin:$PATH"

# ccache
#export CCACHE_DIR="/srv/buildbot_cmake/ccache"
#export CCACHE_COMPRESS

export CCACHE_HARDLINK=1
export CCACHE_DIR="/mnt/ramdisk/ccache"
export CCACHE_SLOPPINESS=time_macros

# Dummy var
export _ROSBE_VERSION=2.1.1
