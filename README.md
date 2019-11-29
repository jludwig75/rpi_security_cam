# rpi_security_cam

Scripts to add email notification for the motion service.

- Sends an email when motion is detected
- Sends an with recorded video attached
- Also runs an hourly cron job to cleanup videos that could not be enailed due to any errors

Setup
- clone repo
- cd <repo name>
- git submodule update --init --recursive
- sudo ./install
- edit settings.json and mail_settings.json in /etc/rpi-cam/ with correct settings
