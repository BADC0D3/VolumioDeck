sudo bash -c "/bin/cat <<EOF >/etc/systemd/system/volumioDeck.service
[Unit]
 Description=Volumio Stream Deck
[Service]
 User=$USER
 WorkingDirectory=$PWD
 ExecStart=/bin/bash -c 'cd $PWD && . venv/bin/activate && python main.py'
 Restart=always
[Install]
 WantedBy=multi-user.target
EOF"

# cat /etc/systemd/system/volumioDeck.service

sudo chmod 644 /etc/systemd/system/volumioDeck.service
sudo systemctl daemon-reload
sudo systemctl start volumioDeck.service
sudo systemctl enable volumioDeck.service
sudo systemctl status volumioDeck.service
