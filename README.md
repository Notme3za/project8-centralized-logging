# Project 8: Centralized Logging and SSH Failure Detection

A beginner-friendly Linux lab that forwards SSH authentication events to an rsyslog receiver and alerts when one source address produces five failed SSH password attempts within five minutes.

## Lab architecture

The verified lab uses one Linux Mint 22.3 VirtualBox machine as both the SSH log source and collector. The source forwards `auth` and `authpriv` syslog facilities to an rsyslog TCP receiver on the same machine. The collector stores received events in a host-specific file:

```text
/var/log/remote/<hostname>/auth.log
```

The collector also listens on its lab interface for a future second host. In this single-host setup, the demonstration uses loopback (`127.0.0.1`), so it proves the forwarding and detection flow but does not demonstrate traffic from a separate machine.

## Detection rule

`detect_ssh_failures.py` scans collected `auth.log` files for OpenSSH `Failed password` events. It groups them by source IP and reports an alert when at least five events occur within a rolling five-minute window. The script reads the latest five minutes each time it runs; it is not scheduled automatically and may report the same recent alert again if run repeatedly during that window.

## Requirements

- Linux Mint or another system with rsyslog and OpenSSH server
- Python 3
- A trusted lab network for any remote syslog traffic

## Configure the collector

Copy `rsyslog/10-central-auth.conf` to `/etc/rsyslog.d/10-central-auth.conf`. Replace `192.168.100.55` with the collector's lab IPv4 address. The loopback input is used by this single-host demonstration.

Allow TCP 514 only from the lab subnet. For the verified lab subnet:

```bash
sudo ufw allow from 192.168.100.0/24 to 192.168.100.55 port 514 proto tcp
```

Adjust both addresses to match the lab. Validate and restart rsyslog:

```bash
sudo rsyslogd -N1
sudo systemctl restart rsyslog
sudo ss -lntp | grep ':514'
```

## Configure forwarding

Copy `rsyslog/90-forward-auth.conf` to `/etc/rsyslog.d/90-forward-auth.conf` on the source. The supplied file forwards to loopback for the single-host lab. For a separate source host, replace `127.0.0.1` with the collector's lab address, then validate and restart rsyslog on the source.

The collector must be reachable on TCP port 514 from that source. Keep this traffic inside a trusted lab network; this project does not configure encrypted syslog transport.

## Run the detector

Place `detect_ssh_failures.py` on the collector, then run:

```bash
sudo python3 detect_ssh_failures.py
```

Root privileges are used here so the script can read rsyslog's protected log files. Defaults are five failures within five minutes. Both values can be changed:

```bash
sudo python3 detect_ssh_failures.py --threshold 3 --window-minutes 2
```

Exit status is `0` when there is no alert, `1` when a threshold is met, and `2` when no collected logs are found.

## Validation performed

- Confirmed rsyslog was active and listening on TCP 514 at the lab address and on loopback.
- Confirmed that SSH uses the `AUTH` facility on the lab machine. Forwarding both `auth` and `authpriv` captured the failed-password event.
- One failed SSH password event produced a no-alert result.
- Five failed password attempts from `127.0.0.1` within five minutes produced an alert.

## Scope and limitations

- The verified source and collector are the same VM. A second Linux host can be added later by pointing its forwarding config at the collector's lab IP.
- Detection covers failed SSH password attempts. It does not detect failed public-key attempts, successful logins from unexpected locations, or other suspicious activity.
- The script runs on demand and scans recent log entries; it does not run as a service or send notifications.
- TCP syslog is not encrypted in this setup. Keep it on a trusted lab network.
