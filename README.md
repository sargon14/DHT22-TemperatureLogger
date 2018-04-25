# DS18B20-TemperatureLogger
Code for temperature logger project. Project uses Raspberry pi and Adafruit DS18B20 temperature sensors.

This is a conversion of tsamu's DHT22-TemperatureLogger project, which itself is an extension of jjpFin's DHT22-TemperatureLogger project, which is associated with jjpFin's [great Instructable tutorial](http://www.instructables.com/id/Raspberry-PI-and-DHT22-temperature-and-humidity-lo/?ALLSTEPS). tsamu extended the code to work with an arbitrary number of DHT22 temperature/humidity sensors. For my version of this project, I'm trying to convert this code to be compatible with a completely different sensor, the DS18B20. So far I have gotten this to work with a single sensor (in fact I've made it all the way through jjpFin's tutorial).

The DS18B20 is part of a family of temperature sensors that use the OneWire communications protocol. Raspbian has OneWire support built in, which simplifies the code for reading temperatures from one sensor. I don't have to refer to the Adafruit DHT library to get the basic data, I just have to read a text file. However, the way to deal with multiple sensors is completely different ([Adafruit](https://www.adafruit.com/products/374) has more details: see links and tutorials on the product page). Motivated by this and by wanting to use nice things, I've switched the sensor handling over to [timofurrer's excellent w1thermsensor package](https://github.com/timofurrer/w1thermsensor). To use multiple sensors, you need to add entries in the "sensors" list of config.json. Make "id" and "tag" match the actual ID number of the sensor you have at location "tag".

The logger also now creates a graph of the last 12 hours of temperature data, so that it can be displayed on the website (see example below).

## Current Branch Project

Currently, in branch day-night-graph, I'm trying to make the graph prettier by having it show when sunrise and sunset happen. What I want is basically for it to have a shaded background during the nighttime portion of the graph. The simplest way I can think of to do this involves asking for sunrise/sunset times from https://sunrise-sunset.org/. But that means I'll have to convert to my time zone, and that means I need to know if it's daylight savings time or not, which means I need the time zone database from https://timezonedb.com, which means...

...that the graph code is going to be too involved for it to stay just tacked on to the end of main(). So, I'm going to break it out into its own function, that pulls temperature data from the database and makes a graph for an arbitrary datetime interval. It should also probably be able to save the graph .svg to different locations besides /var/www/html.

## Next steps

This project will be maximally useful once I have more sensors. Specifically, a sensor near the thermostat will be crucial, so that I can compare what the heat thinks it's doing to what it feels like in the rest of the room. But the two locations are too far away to wire up to the same Raspberry Pi, so I may need to set up some sort of satellite microcontroller...

## Examples

Check the temperature of my apartment at http://rlbtemplogger.ddns.net/ !
