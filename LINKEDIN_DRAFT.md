# LinkedIn post draft

I completed Project 8 in my cybersecurity portfolio: a Linux centralized logging and SSH failure detection lab.

I configured rsyslog to receive Linux authentication events over TCP and store them in host-specific log files. I then wrote a Python script that scans the collected logs and alerts when it finds five failed SSH password attempts from the same source IP within five minutes.

During validation, I found that this Linux Mint SSH server logged authentication events using the `AUTH` facility. Forwarding only `authpriv` missed the failed-password events, so I updated the setup to collect both facilities. One failed attempt stayed below the alert threshold; five attempts from the same address triggered the alert.

This version uses one Linux Mint VM as both source and collector, with forwarding over loopback. A separate Linux host and scheduled detection are possible next extensions.

#Cybersecurity #Linux #Python #BlueTeam #LearningByDoing
