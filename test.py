import requests
# my coords are actually more like 41.317188, -72.908981
# r = requests.get('https://api.sunrise-sunset.org/json?date=2018-11-01&lat=36.7201600&lng=-4.4203400')
r = requests.get('https://api.sunrise-sunset.org/json?lat=41.317188&lng=-72.908981')

print(r.text)
