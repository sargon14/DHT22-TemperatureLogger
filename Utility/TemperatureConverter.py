import logging


class TemperatureConverter():
    '''Used to do temperature conversions between celsius and fahrenheit'''

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("TemperatureConverter instantiated")

    def celsiusToFahrenheits(self, temperatureInCelsius):
        '''Function for converting celsius degrees to fahrenheits'''
        self.logger.info("Converting temperature to fahrenheits")
        return float(temperatureInCelsius) * (9.0 / 5.0) + 32

    def FahrenheitToCelsius(self, temperatureInFahrenheits):
        '''Function for converting fahrenheits to celsius degrees'''
        self.logger.info("Converting temperature to celsius")
        return (float(temperatureInFahrenheits) - 32) / (9.0 / 5.0)
