# rpi_security_cam

Scripts to add email notification to the motion service.

- Sends an email when motion is detected
- Sends an with recorded video attached
- Also runs an hourly cron job to cleanup videos that could not be enailed due to any errors

Setup
- git clone https://github.com/jludwig75/rpi_security_cam.git
- cd rpi_security_cam
- git submodule update --init --recursive
- ./run_tests - Make sure all tests pass
- sudo ./install
- edit settings.json and mail_settings.json in /etc/rpi-cam/ with correct settings
If you are using gmail, setup the sending gmail account to "Allow less secure apps" I used a separate gmail account just for sending so I didn't have to set this on my general use account.

