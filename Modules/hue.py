# Philips Hue module
from phue import Bridge

hub = Bridge("192.168.1.193")

hub.connect()

lights = hub.lights

print("Lights:")

# Print light names
for l in lights:
    print(l.name)

print(hub.get_light(lights[0].name))
print(lights[0])
