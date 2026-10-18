# GitHub setup

Suggested repository name: `project8-centralized-logging`.

Before publishing, place these project files together in `~/project8-centralized-logging` on the Mint VM:

```text
README.md
GIT_SETUP.md
LINKEDIN_DRAFT.md
.gitignore
detect_ssh_failures.py
rsyslog/10-central-auth.conf
rsyslog/90-forward-auth.conf
```

The detector already exists in that directory. Save the README and other project files there, then copy the active rsyslog configuration examples into the repository folder:

```bash
mkdir -p ~/project8-centralized-logging/rsyslog
sudo cp /etc/rsyslog.d/10-central-auth.conf ~/project8-centralized-logging/rsyslog/
sudo cp /etc/rsyslog.d/90-forward-auth.conf ~/project8-centralized-logging/rsyslog/
sudo chown "$USER":"$USER" ~/project8-centralized-logging/rsyslog/*.conf
```

Create an empty public GitHub repository named `project8-centralized-logging` in your account. Do not initialize it with a README or license, since those files are already in the project folder. Then, from the project directory:

```bash
cd ~/project8-centralized-logging
git init -b main
git add README.md GIT_SETUP.md LINKEDIN_DRAFT.md .gitignore detect_ssh_failures.py rsyslog/
git commit -m "Add centralized SSH logging and detection lab"
git remote add origin https://github.com/Notme3za/project8-centralized-logging.git
git push -u origin main
```

GitHub may ask you to authenticate through its browser flow or a configured credential manager. Never put a password or access token in the remote URL or commit it to the repository.
