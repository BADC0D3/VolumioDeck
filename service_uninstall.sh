sudo systemctl stop volumioDeck.service
sudo systemctl disable volumioDeck.service
sudo rm /etc/systemd/system/volumioDeck.service
sudo systemctl daemon-reload
sudo systemctl reset-failed