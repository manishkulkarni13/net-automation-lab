#!/bin/bash
echo "Deploying lab..."
sudo containerlab deploy -t topology.yaml --reconfigure

echo "Starting FRR..."
docker exec clab-automation-lab-frr sed -i 's/bgpd=no/bgpd=yes/' /etc/frr/daemons
docker exec -d clab-automation-lab-frr /usr/lib/frr/frr start
sleep 20

echo "Loading FRR config..."
docker exec clab-automation-lab-frr vtysh -c "copy /etc/frr/frr.conf running-config"

echo "Pushing Day 0 config..."
source netauto/bin/activate
python3 scripts/07_day0_config.py

echo "Health check..."
python3 scripts/12_day2_bgp_health.py