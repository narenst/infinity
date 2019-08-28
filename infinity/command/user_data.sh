#!/bin/bash

cat > /etc/load_volume.sh << 'ENDOFFILE'
#!/bin/bash

device=$(lsblk -s -d -o NAME,MOUNTPOINT | awk '$2 == "" { print $1}')

# Wait until device is available
i=0
until [ ! -z $device ]
do
  echo "Waiting for device"
  sleep 10

  i=$(($i+1))
  if [ "$i" -eq 6 ]
  then
    echo "Device is not available, exiting without mouting volume"
    exit 0
  fi

  device=$(lsblk -s -d -o NAME,MOUNTPOINT | awk '$2 == "" { print $1}')
done

echo "Device is available"

device_name=/dev/$device

# Format /dev/xvdh if it does not contain a partition yet
if [ "$(file -b -s $device_name)" == "data" ]; then
  echo "New volume, formatting the disk"
  mkfs -t xfs $device_name
fi

# Create mount point
mkdir -p /data

# Check if disk is already mounted
if ! mountpoint -q /data
then
  mount $device_name /data
  echo "Mounting the disk"
fi

# Set permissions
chmod a+rwx /data/
echo "Permission set"

echo "Done"
ENDOFFILE

chmod +x /etc/load_volume.sh

# Update rc.local file
sed -i -e '$i /etc/load_volume.sh\n' /etc/rc.local