This project allows users of various operating systems to interact with their Garmin Virb action camera's.

The library is split in three parts:
* One part to interact with the wifi supplied http/json api on the Virb devices
* One part to read / interact with the Mass Storage section of the device
* One part to interact with the Garmin website to fetch firmware packages

The API allows the user to read settings, features and update them
Fetching sensordata, taking picures, upgrading the firmware (without the windows/mac only software), start / stop video / set timelapse settings / change lense settings, eg what the official api will allow you to do, complemented with code to read and comprehend the GPX and fit files on the filesystem.


