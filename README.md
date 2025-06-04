Experimental, use at your own risk. Absolutely no warranty

Hopefully, this can save you the 30 mins. But there's been dumber stuff posted to github

1. Move into klipper/klippy/extras/
2. Add temp-power points:
```ini
# Linear heating for bed
[heater_adaptive_max_power heater_bed]
temp_points:
  0, 0.5
  36, 0.5
  66, 0.68
  81, 0.76
  96, 0.8
  145, 1.0

# Limit PTC heater's initial power
[heater_adaptive_max_power extruder]
temp_points:
  0, 0.73
  25, 0.73
  120, 1.0

# Limit chamber heater's air temperature
[heater_adaptive_max_power exhaust]
temp_sensor: chamber_heater_air
temp_points:
  0, 1.0
  90, 0.6
  105, 0.25
  110, 0.0
 ```
The max powers are absolute and will override the value set in the heater config. Klipper's PID control limits, not scales (that's good), the value to max_power, so it can be changed without affecting stability.
