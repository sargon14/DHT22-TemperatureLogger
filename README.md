# DS18B20-TemperatureLogger
Code for temperature logger project. Project uses Rasbperry pi and Adafruit DS18B20 temperature sensors.

This is a conversion of tsamu's DHT22-TemperatureLogger project, which itself is an extension of jjpFin's DHT22-TemperatureLogger project, which is associated with jjpFin's [great Instructable tutorial](http://www.instructables.com/id/Raspberry-PI-and-DHT22-temperature-and-humidity-lo/?ALLSTEPS). tsamu extended the code to work with an arbitrary number of DHT22 temperature/humidity sensors. For my version of this project, I'm trying to convert this code to be compatible with a completely different sensor, the DS18B20. So far I have gotten this to work with a single sensor (in fact I've made it all the way through jjpFin's tutorial).

The DS18B20 is part of a family of temperature sensors that use the OneWire communications protocol. Raspbian has OneWire support built in, which simplifies the code for reading temperatures from one sensor. I don't have to refer to the Adafruit DHT library to get the basic data, I just have to read a text file. However, the way to deal with multiple sensors is completely different ([Adafruit](https://www.adafruit.com/products/374) has more details: see links and tutorials on the product page), and actually almost certainly __will not__ work in its current form (as of 2017-03-08). I believe it will just arbitrarily pick the sensor with the lowest ID number to read from.

## Next steps:

To fix the multiple-sensor-handling features, I'm going to switch my sensor handling to [timofurrer's excellent w1thermsensor package](https://github.com/timofurrer/w1thermsensor). This will make DS18B20read.py unnecessary. The configuration file will also need refactoring. Most likely, the sensor ID numbers will have to be manually entered into config.json in order for the datalogging to make sense...

## Examples

Check the temperature of my apartment at http://rlbtemplogger.ddns.net/!
