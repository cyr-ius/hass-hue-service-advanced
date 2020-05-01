[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# Hue-Service-Advanced

Place the custom_components folder in your configuration directory (or add its contents to an existing custom_components folder). You need to set up [Hue bridge](https://www.home-assistant.io/components/hue/) first.

Modify the hue integration behavior for sensors and remotes.
* Set Hue motion attributes
* Set a custom refresh rate and monitor the current polling rate for each Hue bridge.

Add service to set motions sensors
```
set_motion_sensor:
  description: Set config for binary sensor or sensor.
  fields:
    entity_id:
      description: Name(s) of the entities to set.
      example: "binary_sensor.hue_motion"
    sensitivity:
      description: Set sensitivity for binary sensor motion ( value between 0 and sensitivity max).
      example: 2
    tholdoffset:
      description: Set offset for dark mode into binary sensor motion ( value between 0 and 25000).
      example: 7000
    tholddark:
      description : Set offset to dertermine insufficient level.
      example: 16000
    sunriseoffset:
      description: Set sunrise offset.
      example: -30
    sunsetoffset:
      description: Set sunset offset.
      example: 30
    long:
      description: Longitude
      example: -115.81
    lat:
      description: Latitude
      example: 37.235
    "on":
      description: Enable/Disable sensor.
      example: true
```

As per [this issue](https://github.com/Cyr-ius/hass-hue-service-advanced/issues/48) it is recommended to use the default naming options in the Hue app in order to ensure sensible sensor names in HA.


## Track Updates
This custom component can be tracked with the help of [HACS](https://github.com/custom-components/hacs).

## Debugging

If you get an error when using this component, the procedure for debugging is as follows.

1. Open an issue here on Github. Include the error message, release number of the custom component.


There are a couple of examples of this process in the debugging_issues folder.
