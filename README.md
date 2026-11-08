# WeCreat Laser Monitor for Home Assistant

An unofficial local integration that reads a Wi-Fi-connected laser's process status every five seconds. Keep using MakeIt to run jobs. Home Assistant talks to the laser directly.

## Compatibility

One Vision Pro 45W owner observed the following sequence during a normal job. Other models, firmware versions, paused jobs and canceled jobs still need testing.

| Raw status | Home Assistant state | Observation |
| --- | --- | --- |
| 2 | running | Job running |
| 3 | cooldown | Motion stopped and the fan continued running |
| 4 | ready | Fan stopped and the machine was ready |
| Other integer | unrecognized | See the raw_status attribute |

The integration uses an empty HTTP POST to /process/status on port 8080. Connection or response errors make the entity unavailable. Polling resumes automatically. A job or transition shorter than the polling interval can be missed.

## Install

Use Home Assistant Core 2025.6 or newer. Your Home Assistant host must be able to reach the laser over the LAN.

* Manual install: Copy the entire custom_components/wecreat folder into your Home Assistant configuration directory under custom_components/. The resulting path should be custom_components/wecreat/manifest.json. Restart Home Assistant.
* HACS custom repository: Open HACS, choose Custom repositories in the menu, enter `https://github.com/thomaskblr/HA-WeCreat`, and choose Integration. Download WeCreat Laser Monitor and restart Home Assistant.

Go to Settings → Devices & services → Add integration → WeCreat Laser Monitor. Enter the laser's hostname or IP address and port. To change the address later, use Reconfigure on the integration entry.

## Bed camera and iPhone photo alert

A Vision Pro 45W owner verified that a local GET to `/camera/take_photo` returns a bed photo. The **Bed camera** entity requests a still when viewed or captured. Background status polling does not fetch photos.

To receive a picture after cooldown, paste [the photo automation](examples/ready_photo_notification.yaml) into a new automation using **Edit in YAML**. Select your actual process status entity, bed camera entity and Companion App notification action. Enable it and check it on the next cooldown → ready transition. If replacing the plain alert, disable the old automation to avoid duplicate messages.

The example assumes a writable Home Assistant `/media` directory configured as local media and accessible to the Companion App. It stores one uniquely named JPEG per transition. Remove older photos periodically. If capture fails, the automation still sends the ready message. Test the camera separately from Developer Tools → Actions using `camera.snapshot` and a filename such as `/media/wecreat-test.jpg`.

## Phone alert

Open the added device to find its process status entity ID. Create an empty automation, select Edit in YAML, and paste examples/ready_notification.yaml. Replace the entity ID and phone notification action with yours. Save and run the actions once to test delivery. The automation fires on cooldown → ready. To alert when cutting stops, use running → cooldown and update the message.

These labels describe the machine's observed state. A ready alert alone cannot establish whether a job completed successfully. The integration sends status requests only.

## Testing and contributing

Install aiohttp and PyYAML in a Python environment. Run `python -m unittest discover -s tests -v`. Tests exercise the HTTP reader with a simulated laser and compare its status sequence with the example trigger. For a live check, confirm the sensor follows a full job, turn off the laser once idle, and verify availability recovers after power-up without a duplicate ready alert.

Compatibility reports are welcome. Include model, firmware, observed operation and sanitized status payloads. Exclude network addresses, serial numbers and account details.

## License

Apache License 2.0. An independent community project, unaffiliated with WeCreat or Home Assistant.
