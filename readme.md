sudo systemctl restart gunicorn
sudo systemctl reload nginx
sudo systemctl restart tcmt_service_bot
sudo systemctl restart daphne