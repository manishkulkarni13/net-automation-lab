# Network Automation Lab

Hands-on network automation lab built on Containerlab with Arista cEOS.

## Topology
- 2 spine switches (AS65001, AS65002)
- 2 leaf switches (AS65101, AS65102)
- FRRouting container (AS65000, simulated WAN/ISP)
- OSPF Area 0 underlay + eBGP full mesh

## What's Automated
- Day 0 full provisioning via Nornir + Jinja2
- Config backup with automated Git commit
- BGP health check across all devices
- NAPALM config diff and rollback
- NETCONF get-config with structured parsing
- Arista eAPI queries
- Ansible playbooks with roles

## Tools
Netmiko · Nornir · NAPALM · Jinja2 · Ansible · NETCONF · eAPI

## Lab Setup
```bash
sudo containerlab deploy -t topology.yaml
docker exec -d clab-automation-lab-frr /usr/lib/frr/frr start
python3 scripts/07_day0_config.py
```

## Scripts
| Script | Purpose |
|---|---|
| 01_netmiko_single.py | Single device SSH connect + config push |
| 02_netmiko_bulk.py | Bulk loop with failure handling |
| 03_nornir_parallel.py | Parallel execution + group filtering |
| 04_jinja2_push.py | Per-device config from Jinja2 templates |
| 05_backup_and_git.py | Config backup + auto git commit |
| 06_error_handling.py | Snapshot → push → validate → rollback |
| 07_day0_config.py | Full Day 0 provisioning |
| 08_napalm_getters.py | NAPALM facts, interfaces, BGP |
| 09_napalm_diff.py | Config diff + commit + rollback |
| 10_netconf_get.py | NETCONF get-config + xmltodict parsing |
| 11_eapi.py | Arista eAPI BGP state query |
| 12_day2_bgp_health.py | Day 2 BGP health check report |