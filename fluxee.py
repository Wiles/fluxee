import platform
from bottle import run, post, request
from yeelight import Bulb
import configparser

bulbs = []
maxtemps = []
mintemps = []
check_state = True


@post('/room_1')
def room_handler():
    post_dict = request.query.decode()
    if 'ct' in post_dict and 'bri' in post_dict:
        color_temp = int(post_dict['ct'])
        brightness = int(round(float(post_dict['bri']) * 100))
        for (currentbulb, maxtemp, mintemp) in zip(bulbs, maxtemps, mintemps):
            maxtemp = int(round(float(maxtemp)))
            mintemp = int(round(float(mintemp)))
            if currentbulb != '':
                print('Sending command to Yeelight at', currentbulb)
                bulb = Bulb(currentbulb)
                if static_brightness is False:
                    bulb.set_brightness(brightness)
                    print('Brightness set to', brightness, 'percent')
                if mintemp < color_temp < maxtemp:
                    bulb.set_color_temp(color_temp)
                    print('Color temperature set to', color_temp, 'Kelvin')
                else:
                    if color_temp >= maxtemp:
                        bulb.set_color_temp(maxtemp)
                        print('Reached highest color temperature of', maxtemp, 'Kelvin')
                    if color_temp <= mintemp:
                        bulb.set_color_temp(mintemp)
                        print('Reached lowest color temperature of', mintemp, 'Kelvin')


def main():
    print('Welcome to fluxee by davidramiro')
    print('Reading config...')
    config = configparser.ConfigParser()
    config.read('config.ini')
    global static_brightness
    bulb_count = int(config.get('general', 'LampCount'))
    check_state = config.getboolean('general', 'CheckLampState')
    static_brightness = config.getboolean('general', 'StaticBrightness')
    default_brightness = int(config.get('general', 'BrightnessValue'))
    for n in range(1, (bulb_count + 1)):
        bulbs.append(config.get(str(n), 'ip'))
        if config.get(str(n), 'MaxColorTemperature') == '':
            maxtemps.append(6500)
        else:
            maxtemps.append(config.get(str(n), 'MaxColorTemperature'))
        if config.get(str(n), 'MinColorTemperature') == '':
            mintemps.append(1700)
        else:
            mintemps.append(config.get(str(n), 'MinColorTemperature'))
    print('Initializing...')
    for init_bulb in bulbs:
        if init_bulb != '':
            print('Initializing Yeelight at %s' % init_bulb)
            bulb = Bulb(init_bulb)
            if check_state is True:
                state = bulb.get_properties(requested_properties=['power'])
                if 'off' in state['power']:
                    print('Powered off. Ignoring Yeelight at %s' % init_bulb)
                elif static_brightness is True:
                    print('Changing brightness of', init_bulb)
                    bulb.set_brightness(default_brightness)
            else:
                print('Turning on Yeelight at %s' % init_bulb)
                bulb.turn_on()
                if static_brightness is True:
                    bulb.set_brightness(default_brightness)
                else:
                    bulb.set_brightness(100)

    run(host=config.get('general', 'Host'), port=config.get('general', 'Port'))
    print('Thank you for using fluxee. Have a good one!')


main()
