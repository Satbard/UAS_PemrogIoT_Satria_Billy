from machine import Pin, ADC
from time import sleep
import dht
from umqtt.simple import MQTTClient

WIFI_SSID = 'PCU_Sistem_Kontrol'
WIFI_PASSWORD = 'lasikonn'

MQTT_SERVER = '192.168.41.54'
MQTT_PORT = 1883
DHT_TOPIC = b'dht'
POT_TOPIC = b'potensio'

def connect_to_wifi():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Menghubungkan ke Wi-Fi...')
        sta_if.active(True)
        sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
        while not sta_if.isconnected():
            pass
    print('Terhubung ke Wi-Fi:', sta_if.ifconfig()[0])

def publish_data(topic, data):
    client = MQTTClient('esp8266', MQTT_SERVER, port=MQTT_PORT)
    client.connect()
    client.publish(topic, data)
    client.disconnect()

connect_to_wifi()

sensor = dht.DHT11(Pin(14))
pot = ADC(0)

while True:
  pot_value = pot.read()
  print('RPM:', pot_value)
  sleep(0.1)
  
  try:
    sleep(2)
    sensor.measure()
    temp = sensor.temperature()
    print('Temperature: %3.1f C' % temp)
    
    dht_data = 'Temperature: %3.1f C' % temp
    publish_data(DHT_TOPIC, dht_data)

    pot_data = 'RPM: ' + str(pot_value)
    publish_data(POT_TOPIC, pot_data)

  except OSError as e:
    print('Failed to read sensor.')


