import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import threading
import time

# MQTT Broker settings
MQTT_SERVER = '192.168.41.54'
MQTT_PORT = 1883
DHT_TOPIC = 'dht'
POT_TOPIC = 'potensio'

# Data storage
temperature_data = []
rpm_data = []
items_inside_fridge = []  # Dummy data for the number of items inside the fridge
light_status = []  # Dummy data for the light status inside the fridge

# MQTT client callback functions
def generate_dummy_data():
    while True:
        # Generate random number of items inside the fridge (between 0 and 10)
        items = random.randint(0, 10)
        items_inside_fridge.append(items)
        print('Items inside the fridge:', items)

        # Generate random light status (0 for off, 1 for on)
        light = 0
        
        # Randomly turn on the light multiple times within a cycle of 10 seconds
        for _ in range(random.randint(1, 5)):
            light_status.append(light)
            print('Fridge light status:', light)
            time.sleep(random.uniform(0.1, 1))
            light = 1 - light
            light_status.append(light)
            print('Fridge light status:', light)
            time.sleep(random.uniform(0.1, 1))

# Generate random dummy data at regular intervals
def generate_data(interval):
    while True:
        generate_dummy_data()
        plt.pause(interval)

def on_connect(client, userdata, flags, rc):
    print('Connected to MQTT broker')
    client.subscribe(DHT_TOPIC)
    client.subscribe(POT_TOPIC)

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode('utf-8')

    if topic == DHT_TOPIC:
        # Parse and store temperature data
        temperature = float(payload.split(':')[1].strip().split(' ')[0])
        temperature_data.append(temperature)
        print('Received temperature:', temperature)

    elif topic == POT_TOPIC:
        # Parse and store RPM data
        rpm = int(payload.split(':')[1].strip())
        rpm_data.append(rpm)
        print('Received RPM:', rpm)

    elif topic == 'fridge':
        # Parse and store number of items inside the fridge
        items = int(payload.split(':')[1].strip())
        items_inside_fridge.append(items)
        print('Items inside the fridge:', items)
    elif topic == 'fridge/light':
        # Parse and store light status (1 for on, 0 for off)
        light = int(payload.split(':')[1].strip())
        light_status.append(light)
        print('Fridge light status:', light)

def on_disconnect(client, userdata, rc):
    print('Disconnected from MQTT broker')

# Create MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Connect to MQTT broker
client.connect(MQTT_SERVER, MQTT_PORT, 60)

# Start the MQTT network loop
client.loop_start()

# Start generating dummy data
data_generation_interval = 1  # In seconds
data_generator = threading.Thread(target=generate_data, args=(data_generation_interval,))
data_generator.start()

# Plot and update the graph
fig, (ax1, ax2, ax3,ax4) = plt.subplots(4, 1, figsize=(15, 8))
line1, = ax1.plot([], [], 'r', label='Temperature')
line2, = ax2.plot([], [], 'b', label='RPM')
line3, = ax3.plot([], [], 'g', label='Fridge Light')
bar = ax4.bar([], [])
ax1.set_ylabel('Temperature (Celsius)')
ax2.set_ylabel('RPM')
ax3.set_ylabel('Light Status')
ax3.set_xlabel('Time')
ax1.legend()
ax2.legend()
ax3.legend()

def update_graph(frame):
    line1.set_data(range(len(temperature_data)), temperature_data)
    line2.set_data(range(len(rpm_data)), rpm_data)
    line3.set_data(range(len(light_status)), light_status)
    ax1.relim()
    ax1.autoscale_view(True, True, True)
    ax2.relim()
    ax2.autoscale_view(True, True, True)
    ax3.relim()
    ax3.autoscale_view(True, True, True)
    ax4.clear()
    ax4.bar(range(len(items_inside_fridge)), items_inside_fridge)
    ax4.set_xlabel('Time')
    ax4.set_ylabel('Number of Items')
    ax4.set_xticks(range(len(items_inside_fridge)))
    ax4.set_xticklabels([str(i) for i in range(len(items_inside_fridge))])
    return line1, line2, line3, bar

ani = animation.FuncAnimation(fig, update_graph, interval=1000)
plt.show()