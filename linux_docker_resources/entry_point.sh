#!/bin/sh

# This file fixes the permissions of the home directory so that it matches the host user's ID.
# It also enables multicast and changes directories before executing the input from docker run.

# Adapted from: http://chapeau.freevariable.com/2014/08/docker-uid.html

export ORIGPASSWD=$(cat /etc/passwd | grep rosbuild)
export ORIG_UID=$(echo $ORIGPASSWD | cut -f3 -d:)
export ORIG_GID=$(echo $ORIGPASSWD | cut -f4 -d:)

export UID=${UID:=$ORIG_UID}
export GID=${GID:=$ORIG_GID}

ARCH=`uname -i`

ORIG_HOME=$(echo $ORIGPASSWD | cut -f6 -d:)

echo "Enabling multicast..."
ifconfig eth0 multicast
echo "done."

case "${CI_ARGS}" in
  *--connext*)
    echo "Installing Connext..."
    case "${CI_ARGS}" in
      *--connext-debs*)
        echo "Using Debian package of Connext"
        ;;
      *)
        echo "Installing Connext binaries off RTI website..."
        python3 -u /tmp/rti_web_binaries_install_script.py /tmp/rti_connext_dds-5.3.1-eval-x64Linux3gcc5.4.0.run /home/rosbuild/rti_connext_dds-5.3.1 --rtipkg_paths /tmp/rti_security_plugins-5.3.1-eval-x64Linux3gcc5.4.0.rtipkg
        if [ $? -ne 0 ]
        then
          echo "Connext not installed correctly (maybe you're on an ARM machine?)." >&2
          exit 1
        fi
        mv /tmp/rti_license.dat /home/rosbuild/rti_license.dat
        export RTI_LICENSE_FILE=/home/rosbuild/rti_license.dat
        ;;
    esac
    echo "done."
    ;;
  *)
    echo "NOT installing Connext."
    ;;
esac

echo "Fixing permissions..."
sed -i -e "s/:$ORIG_UID:$ORIG_GID:/:$UID:$GID:/" /etc/passwd
sed -i -e "s/rosbuild:x:$ORIG_GID:/rosbuild:x:$GID:/" /etc/group

chown -R ${UID}:${GID} "${ORIG_HOME}"
echo "done."

cd /home/rosbuild/ci_scripts

exec sudo -H -u rosbuild -E -- /bin/sh -c "$*"
