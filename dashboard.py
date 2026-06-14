import http.server
import socketserver
import json
import subprocess
import time
import os
import urllib.parse

PORT = 8089

class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Prevent default logging to stderr to keep terminal clean
        pass

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        if path == '/api/status':
            self.send_json(self.get_docker_status())
        elif path == '/api/system':
            self.send_json(self.get_system_stats())
        elif path == '/api/logs':
            query = urllib.parse.parse_qs(parsed_url.query)
            service = query.get('service', [None])[0]
            if service:
                self.send_text(self.get_docker_logs(service))
            else:
                self.send_error_response(400, "Falta el parámetro 'service'")
        else:
            # Serve static files
            if path == '/':
                path = '/index.html'
            
            # Prevent directory traversal
            clean_path = os.path.normpath(path).lstrip('/')
            file_path = os.path.join('/home/vboxuser/proyectoserver/dashboard', clean_path)
            
            if os.path.exists(file_path) and os.path.isfile(file_path):
                self.send_file(file_path)
            else:
                self.send_error_response(404, "Archivo no encontrado")

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        if path == '/api/restart':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                service = data.get('service')
                if service:
                    success, error = self.restart_docker_service(service)
                    self.send_json({"success": success, "error": error})
                else:
                    self.send_error_response(400, "Falta el campo 'service'")
            except Exception as e:
                self.send_error_response(400, str(e))
        else:
            self.send_error_response(404, "No encontrado")

    # Helper senders
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def send_text(self, text):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(text.encode('utf-8'))

    def send_file(self, file_path):
        mime_types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.ico': 'image/x-icon'
        }
        ext = os.path.splitext(file_path)[1]
        mime = mime_types.get(ext, 'application/octet-stream')
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error_response(500, str(e))

    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))

    # API implementers
    def get_docker_status(self):
        try:
            ps_out = subprocess.check_output(
                ['docker', 'compose', 'ps', '-a', '--format', 'json'],
                cwd='/home/vboxuser/proyectoserver'
            ).decode('utf-8')
            
            containers = []
            for line in ps_out.strip().split('\n'):
                if line.strip():
                    try:
                        containers.append(json.loads(line))
                    except:
                        pass
            
            stats_out = subprocess.check_output(
                ['docker', 'stats', '--no-stream', '--format', 'json']
            ).decode('utf-8')
            
            stats_map = {}
            for line in stats_out.strip().split('\n'):
                if line.strip():
                    try:
                        stat = json.loads(line)
                        name = stat.get('Name', '')
                        stats_map[name] = stat
                    except:
                        pass
            
            result = []
            for c in containers:
                name = c.get('Name') or c.get('Names', '')
                stat = stats_map.get(name, {})
                
                result.append({
                    "id": c.get('ID', ''),
                    "name": name,
                    "service": c.get('Service', ''),
                    "image": c.get('Image', ''),
                    "state": c.get('State', ''),
                    "status": c.get('Status', ''),
                    "ports": c.get('Ports', ''),
                    "cpu": stat.get('CPUPerc', '0.00%'),
                    "memory": stat.get('MemUsage', '0B / 0B'),
                    "memory_perc": stat.get('MemPerc', '0.00%')
                })
            return result
        except Exception as e:
            return {"error": str(e)}

    def get_docker_logs(self, service):
        try:
            # We enforce limits to avoid huge transfers
            logs = subprocess.check_output(
                ['docker', 'compose', 'logs', '--tail=100', service],
                cwd='/home/vboxuser/proyectoserver',
                stderr=subprocess.STDOUT
            ).decode('utf-8')
            return logs
        except Exception as e:
            return f"Error al obtener logs para el servicio '{service}': {str(e)}"

    def restart_docker_service(self, service):
        try:
            subprocess.check_call(
                ['docker', 'compose', 'restart', service],
                cwd='/home/vboxuser/proyectoserver'
            )
            return True, None
        except Exception as e:
            return False, str(e)

    def get_system_stats(self):
        # CPU
        cpu = 0.0
        try:
            with open('/proc/stat', 'r') as f:
                line1 = f.readline().split()
            idle1 = float(line1[4]) + float(line1[5])
            non_idle1 = float(line1[1]) + float(line1[2]) + float(line1[3]) + float(line1[6]) + float(line1[7]) + float(line1[8])
            total1 = idle1 + non_idle1
            
            time.sleep(0.1)
            
            with open('/proc/stat', 'r') as f:
                line2 = f.readline().split()
            idle2 = float(line2[4]) + float(line2[5])
            non_idle2 = float(line2[1]) + float(line2[2]) + float(line2[3]) + float(line2[6]) + float(line2[7]) + float(line2[8])
            total2 = idle2 + non_idle2
            
            total_delta = total2 - total1
            idle_delta = idle2 - idle1
            if total_delta > 0:
                cpu = round((total_delta - idle_delta) / total_delta * 100, 1)
        except Exception as e:
            pass

        # RAM
        ram_info = {"ram_total": 0.0, "ram_free": 0.0, "ram_percentage": 0.0}
        try:
            meminfo = {}
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    parts = line.split(':')
                    if len(parts) == 2:
                        name = parts[0].strip()
                        val = parts[1].split()[0].strip()
                        meminfo[name] = float(val)
            total = meminfo.get('MemTotal', 0.0) / (1024 * 1024)
            free = meminfo.get('MemAvailable', meminfo.get('MemFree', 0.0)) / (1024 * 1024)
            percentage = round((total - free) / total * 100, 1) if total > 0 else 0
            ram_info = {
                "ram_total": round(total, 2),
                "ram_free": round(free, 2),
                "ram_percentage": percentage
            }
        except Exception as e:
            pass

        # Disk
        disk_info = {"disk_total": "N/A", "disk_used": "N/A", "disk_free": "N/A", "disk_percentage": 0}
        try:
            out = subprocess.check_output(['df', '-BG', '/']).decode('utf-8')
            lines = out.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                total = parts[1].replace('G', '')
                used = parts[2].replace('G', '')
                avail = parts[3].replace('G', '')
                perc = parts[4].replace('%', '')
                disk_info = {
                    "disk_total": f"{total} GB",
                    "disk_used": f"{used} GB",
                    "disk_free": f"{avail} GB",
                    "disk_percentage": int(perc)
                }
        except:
            pass

        return {
            "cpu": cpu,
            **ram_info,
            **disk_info
        }

class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == '__main__':
    # Start server
    with ThreadingTCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"Servidor de control corriendo en puerto {PORT}...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nApagando servidor...")
