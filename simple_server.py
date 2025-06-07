import socket
import threading
import json
import pyautogui
import time

class SimpleOSRSController:
    def __init__(self):
        # OSRS window coordinates
        self.osrs_window = {
            'x': 100,
            'y': 100, 
            'width': 765,
            'height': 503
        }
        
        self.last_click_time = 0
        self.last_key_time = 0
        self.click_cooldown = 0.5
        self.key_cooldown = 0.2  # Faster for arrow keys
        
        # Safety
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
    
    def setup_osrs_window(self):
        print("=== OSRS Window Setup ===")
        print("1. Open OSRS and set to Fixed mode")
        print("2. Position window where you want it")
        print("3. Press ENTER when ready...")
        input()
        
        print("Move mouse to TOP-LEFT corner of OSRS game area and press ENTER...")
        input()
        x1, y1 = pyautogui.position()
        print(f"Top-left: ({x1}, {y1})")
        
        print("Move mouse to BOTTOM-RIGHT corner of OSRS game area and press ENTER...")
        input()
        x2, y2 = pyautogui.position()
        print(f"Bottom-right: ({x2}, {y2})")
        
        self.osrs_window = {
            'x': x1,
            'y': y1,
            'width': x2 - x1,
            'height': y2 - y1
        }
        
        print(f"OSRS window configured: {self.osrs_window}")
    
    def handle_click(self, x, y):
        current_time = time.time()
        
        if current_time - self.last_click_time < self.click_cooldown:
            return False
        
        # Convert to actual coordinates
        actual_x = self.osrs_window['x'] + x
        actual_y = self.osrs_window['y'] + y
        
        # Validate
        if (x < 0 or x > self.osrs_window['width'] or 
            y < 0 or y > self.osrs_window['height']):
            return False
        
        try:
            pyautogui.click(actual_x, actual_y)
            self.last_click_time = current_time
            print(f"Click: ({x}, {y}) -> ({actual_x}, {actual_y})")
            return True
        except Exception as e:
            print(f"Click error: {e}")
            return False
    
    def handle_key(self, key):
        current_time = time.time()
        
        if current_time - self.last_key_time < self.key_cooldown:
            return False
        
        try:
            # Map arrow keys
            key_mapping = {
                'ArrowUp': 'up',
                'ArrowDown': 'down', 
                'ArrowLeft': 'left',
                'ArrowRight': 'right'
            }
            
            if key in key_mapping:
                pyautogui.press(key_mapping[key])
                self.last_key_time = current_time
                print(f"Key pressed: {key} -> {key_mapping[key]}")
                return True
            else:
                print(f"Unknown key: {key}")
                return False
                
        except Exception as e:
            print(f"Key error: {e}")
            return False

# HTTP Server for simple setup
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

controller = SimpleOSRSController()

class ClickHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/click':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                x = data.get('x', 0)
                y = data.get('y', 0)
                
                success = controller.handle_click(x, y)
                
                response = {'success': success, 'x': x, 'y': y}
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                print(f"Click error: {e}")
        
        elif self.path == '/key':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                key = data.get('key', '')
                
                success = controller.handle_key(key)
                
                response = {'success': success, 'key': key}
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                print(f"Key error: {e}")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress HTTP logs

def main():
    print("=== $OSRS Simple Controller ===")
    
    setup = input("Setup OSRS window? (y/n): ")
    if setup.lower() == 'y':
        controller.setup_osrs_window()
    
    print("Starting HTTP server on http://localhost:8000")
    print("Handles clicks AND arrow keys!")
    print("Click coordinates and arrow key presses will be sent to OSRS")
    
    server = HTTPServer(('localhost', 8000), ClickHandler)
    print("🚀 Server running! Open index.html in your browser")
    server.serve_forever()

if __name__ == "__main__":
    main()