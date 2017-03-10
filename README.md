# DS18B20-TemperatureLogger
Code for temperature logger project. Project uses Raspberry pi and Adafruit DS18B20 temperature sensors.

This is a conversion of tsamu's DHT22-TemperatureLogger project, which itself is an extension of jjpFin's DHT22-TemperatureLogger project, which is associated with jjpFin's [great Instructable tutorial](http://www.instructables.com/id/Raspberry-PI-and-DHT22-temperature-and-humidity-lo/?ALLSTEPS). tsamu extended the code to work with an arbitrary number of DHT22 temperature/humidity sensors. For my version of this project, I'm trying to convert this code to be compatible with a completely different sensor, the DS18B20. So far I have gotten this to work with a single sensor (in fact I've made it all the way through jjpFin's tutorial).

The DS18B20 is part of a family of temperature sensors that use the OneWire communications protocol. Raspbian has OneWire support built in, which simplifies the code for reading temperatures from one sensor. I don't have to refer to the Adafruit DHT library to get the basic data, I just have to read a text file. However, the way to deal with multiple sensors is completely different ([Adafruit](https://www.adafruit.com/products/374) has more details: see links and tutorials on the product page). Motivated by this and by wanting to use nice things, I've switched the sensor handling over to [timofurrer's excellent w1thermsensor package](https://github.com/timofurrer/w1thermsensor). To use multiple sensors, you need to add entries in the "sensors" list of config.json. Make "id" and "tag" match the actual ID number of the sensor you have at location "tag".

## Next steps

I want the temperature-monitoring website that the raspi serves (see below) to be fancier. Specifically, I want it to include a temperature graph. So I'll need to add some code to plot the data with matplotlib and save an image of the plot...

## Examples

Check the temperature of my apartment at http://rlbtemplogger.ddns.net/!
