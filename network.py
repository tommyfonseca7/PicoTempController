import socket
import gc
from machine import Pin
import network
from ctrl import PID, on_off
from time import sleep
import select

from actuator import Actuation
from sensor import Temperature
from cdr import WebServer

gc.collect()

ssid = 'ssid'
password = 'password'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
    pass

print('Connection successful')
print(station.ifconfig())

# Create sockets for each port
s_main = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_main.bind(('', 80))
s_main.listen(5)

s_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_data.bind(('', 4444))
s_data.listen(5)

s_control = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_control.bind(('', 5555))
s_control.listen(5)

led = Pin('LED', Pin.OUT)

temperature = Temperature()
actuation = Actuation()
webserver = WebServer()
PIDController = PID(0, 0, 0, 0, 0, actuation)
ONOFFController = on_off(0, 0, actuation)
T_in = 0
H_in = 0
T_out = 0
H_out = 0
timestamp = 0

def handle_request(conn, addr, port):
    global T_in, H_in, T_out, H_out, timestamp
    try:
        if gc.mem_free() < 102000:
            gc.collect()
        conn.settimeout(3.0)
        print('Got a connection from %s on port %d' % (str(addr), port))
        led.on()
        request = conn.recv(1024)
        conn.settimeout(None)

        request = webserver.parse_http_request(request)
        response = 'HTTP/1.1 404 Not Found\nContent-Type: text/html\nConnection: close\n\nPage not found'
        
        if port == 80:
            if request['method'] == 'GET' and request['path'] == '/':
                T_in, H_in, T_out, H_out, timestamp = temperature.read_all_sensors()
                response = webserver.web_page(T_in, H_in, T_out, H_out, timestamp)
                conn.send('HTTP/1.1 200 OK\r\n')
                conn.send('Content-Type: text/html\r\n')
                conn.send('Connection: close\r\n')
                conn.send('Access-Control-Allow-Origin: *\r\n\r\n')
                conn.sendall(response)
                conn.close()
                gc.collect()
                led.off()
        elif port == 4444:
            if request['method'] == 'GET' and request['path'] == '/data':
                fan_percentage = actuation.fan_percentage()
                heater_percentage = actuation.heater_percentage()
                T_in, H_in, T_out, H_out, timestamp = temperature.read_all_sensors()
                response = str(T_in) + "&" + str(H_in) + "&" + str(T_out) + "&" + str(H_out) + "&" + str(timestamp) + "&" + str(fan_percentage) + "&" + str(heater_percentage)
                conn.send('HTTP/1.1 200 OK\r\n')
                conn.send('Content-Type: text/html\r\n')
                conn.send('Connection: close\r\n')
                conn.send('Access-Control-Allow-Origin: *\r\n\r\n')
                conn.sendall(response)
                conn.close()
                gc.collect()
                led.off()
        elif port == 5555:
            if request['method'] == 'GET' and request['path'] == '/heat':
                actuation.heating_set(int(request['query']['value']))
                response = request['query']['value']
                conn.send('HTTP/1.1 200 OK\r\n')
                conn.send('Content-Type: text/html\r\n')
                conn.send('Connection: close\r\n')
                conn.send('Access-Control-Allow-Origin: *\r\n\r\n')
                conn.sendall(response)
                conn.close()
                gc.collect()
                led.off()
            elif request['method'] == 'GET' and request['path'] == '/fan':
                actuation.fan_set(int(request['query']['value']))
                response = request['query']['value']
                conn.send('HTTP/1.1 200 OK\r\n')
                conn.send('Content-Type: text/html\r\n')
                conn.send('Connection: close\r\n')
                conn.send('Access-Control-Allow-Origin: *\r\n\r\n')
                conn.sendall(response)
                conn.close()
                gc.collect()
                led.off()
            elif request['method'] == 'POST' and request['path'] == '/on-off-controller':
                body_str = request['body']
                body = dict(item.split('=') for item in body_str.split('&'))
                temperatureOnOff = float(body['temperature'])
                threshold = float(body['treshold'])
                ONOFFController.set_values(temperatureOnOff, threshold)
                ONOFFController.actuate(T_in, T_out)
                response = 'Settings updated'
                conn.send('HTTP/1.1 200 OK\r\n')
                conn.send('Content-Type: text/html\r\n')
                conn.send('Connection: close\r\n')
                conn.send('Access-Control-Allow-Origin: *\r\n\r\n')
                conn.sendall(response)
                conn.close()
                gc.collect()
                led.off()
            elif request['method'] == 'POST' and request['path'] == '/pid-controller':
                body_str = request['body']
                body = dict(item.split('=') for item in body_str.split('&'))
                proportional = float(body['proportional'])
                integral = float(body['integral'])
                derivative = float(body['derivative'])
                threshold = float(body['threshold'])
                temperaturePID = float(body['temperature'])
                response = 'PID controller settings updated'
                PIDController.set_values(proportional, integral, derivative, temperaturePID, threshold)
                PIDController.actuate(T_in, T_out)
                conn.send('HTTP/1.1 200 OK\r\n')
                conn.send('Content-Type: text/html\r\n')
                conn.send('Connection: close\r\n')
                conn.send('Access-Control-Allow-Origin: *\r\n\r\n')
                conn.sendall(response)
                conn.close()
                gc.collect()
                led.off()
            elif request['method'] == 'POST' and request['path'] == '/turn-off-controllers':
                PIDController.off()
                ONOFFController.off()
                response = 'Controllers turned off'
                conn.send('HTTP/1.1 200 OK\r\n')
                conn.send('Content-Type: text/html\r\n')
                conn.send('Connection: close\r\n')
                conn.send('Access-Control-Allow-Origin: *\r\n\r\n')
                conn.sendall(response)
                conn.close()
                gc.collect()
                led.off()
        
        
    except OSError as e:
        conn.close()
        print('Connection closed due to an error: ', e)

while True:
    try:
        r, w, e = select.select([s_main, s_data, s_control], [], [], 1)
        for sock in r:
            conn, addr = sock.accept()
            if sock == s_main:
                handle_request(conn, addr, 80)
            elif sock == s_data:
                handle_request(conn, addr, 4444)
            elif sock == s_control:
                handle_request(conn, addr, 5555)
    except OSError as e:
        print('Error in main loop: ', e)
