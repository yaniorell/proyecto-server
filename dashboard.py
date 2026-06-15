from flask import Flask, render_template_string, jsonify, request
import subprocess
import json
import time
import psutil
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# ==================== TEMPLATES ====================

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="10">
    <title>Infrastructure Control Panel</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        slate: {
                            950: '#030712'
                        }
                    },
                    backdropBlur: {
                        'sm': '4px'
                    }
                }
            }
        }
    </script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: linear-gradient(135deg, #030712 0%, #0f172a 100%);
            color: #e2e8f0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow-x: hidden;
        }

        /* Glassmorphism effect */
        .glass {
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(30, 41, 59, 0.8);
            border-radius: 12px;
        }

        .glass-hover {
            transition: all 0.3s ease;
        }

        .glass-hover:hover {
            background: rgba(15, 23, 42, 0.8);
            border-color: rgba(34, 211, 238, 0.3);
            box-shadow: 0 0 20px rgba(34, 211, 238, 0.1);
        }

        /* LED indicator */
        .led {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
            box-shadow: 0 0 8px currentColor;
            animation: pulse 2s infinite;
        }

        .led.up {
            background-color: #10b981;
            color: #10b981;
        }

        .led.down {
            background-color: #ef4444;
            color: #ef4444;
        }

        .led.exited {
            background-color: #ef4444;
            color: #ef4444;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        /* Monospace for technical data */
        .font-mono-tech {
            font-family: 'Courier New', monospace;
            font-size: 13px;
            letter-spacing: 0.5px;
        }

        /* Accent colors */
        .text-cyan-accent {
            color: #06b6d4;
        }

        .text-emerald-accent {
            color: #10b981;
        }

        .border-cyan-accent {
            border-color: rgba(6, 182, 212, 0.3);
        }

        /* Bento grid layout */
        .bento-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 16px;
            padding: 24px;
        }

        .bento-grid-item {
            min-height: 200px;
        }

        .bento-grid-item.span-2 {
            grid-column: span 2;
        }

        @media (max-width: 1024px) {
            .bento-grid-item.span-2 {
                grid-column: span 1;
            }
        }

        /* Status bar animations */
        .status-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .status-badge.running {
            background: rgba(16, 185, 129, 0.15);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .status-badge.exited {
            background: rgba(239, 68, 68, 0.15);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(15, 23, 42, 0.4);
        }

        ::-webkit-scrollbar-thumb {
            background: rgba(34, 211, 238, 0.4);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: rgba(34, 211, 238, 0.6);
        }

        /* Metric display */
        .metric {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .metric-label {
            font-size: 12px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .metric-value {
            font-size: 24px;
            font-weight: 700;
            color: #06b6d4;
        }

        .metric-unit {
            font-size: 12px;
            color: #64748b;
        }

        /* Progress bar */
        .progress-bar {
            height: 6px;
            background: rgba(30, 41, 59, 0.8);
            border-radius: 3px;
            overflow: hidden;
            margin-top: 8px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #06b6d4, #10b981);
            transition: width 0.3s ease;
        }

        /* Container classes */
        .card-title {
            font-size: 14px;
            font-weight: 600;
            color: #e2e8f0;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 16px;
        }

        .card-subtitle {
            font-size: 12px;
            color: #94a3b8;
            margin-bottom: 12px;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="glass sticky top-0 z-50 border-b border-slate-800">
        <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div>
                <h1 class="text-2xl font-bold text-cyan-accent">⚡ Infrastructure Control</h1>
                <p class="text-sm text-slate-400 mt-1">Real-time system monitoring & management</p>
            </div>
            <div class="text-right">
                <div class="text-sm text-slate-400">Uptime</div>
                <div class="text-2xl font-bold text-emerald-accent" id="uptime">--:--:--</div>
            </div>
        </div>
    </div>

    <!-- Main content -->
    <div class="bento-grid">
        
        <!-- Docker Services Status (Span 2) -->
        <div class="bento-grid-item span-2 glass glass-hover p-6">
            <h2 class="card-title">🐳 Docker Services</h2>
            <div id="services-container" class="space-y-3">
                <p class="text-slate-400 text-sm">Loading services...</p>
            </div>
        </div>

        <!-- CPU Usage -->
        <div class="bento-grid-item glass glass-hover p-6">
            <h2 class="card-title">⚙️ CPU Usage</h2>
            <div class="metric">
                <div class="metric-value" id="cpu-value">--</div>
                <div class="metric-unit">percent</div>
            </div>
            <div class="progress-bar mt-4">
                <div class="progress-fill" id="cpu-bar" style="width: 0%"></div>
            </div>
            <p class="text-xs text-slate-500 mt-3">System processor load</p>
        </div>

        <!-- RAM Usage -->
        <div class="bento-grid-item glass glass-hover p-6">
            <h2 class="card-title">🧠 Memory</h2>
            <div class="metric">
                <div class="metric-value" id="ram-value">--</div>
                <div class="metric-unit" id="ram-usage">-- GB / -- GB</div>
            </div>
            <div class="progress-bar mt-4">
                <div class="progress-fill" id="ram-bar" style="width: 0%"></div>
            </div>
            <p class="text-xs text-slate-500 mt-3">Available memory</p>
        </div>

        <!-- Disk Usage -->
        <div class="bento-grid-item glass glass-hover p-6">
            <h2 class="card-title">💾 Disk Space</h2>
            <div class="metric">
                <div class="metric-value" id="disk-value">--</div>
                <div class="metric-unit" id="disk-usage">-- / --</div>
            </div>
            <div class="progress-bar mt-4">
                <div class="progress-fill" id="disk-bar" style="width: 0%"></div>
            </div>
            <p class="text-xs text-slate-500 mt-3">Root partition</p>
        </div>

        <!-- Service Logs (Span 2) -->
        <div class="bento-grid-item span-2 glass glass-hover p-6">
            <h2 class="card-title">📋 Service Logs</h2>
            <div class="mb-4">
                <select id="log-service" class="bg-slate-800 text-slate-200 rounded px-3 py-2 text-sm border border-slate-700 w-full">
                    <option value="">Select a service...</option>
                </select>
            </div>
            <div id="logs-container" class="bg-slate-950 rounded p-3 h-64 overflow-y-auto border border-slate-800">
                <p class="text-slate-500 text-xs font-mono-tech">Select a service to view logs</p>
            </div>
        </div>

    </div>

    <!-- Footer -->
    <div class="max-w-7xl mx-auto px-6 py-6 text-center text-slate-500 text-xs">
        <p>Last updated: <span id="last-update">--:--:--</span> | Auto-refresh every 10 seconds</p>
    </div>

    <!-- Scripts -->
    <script>
        const API_BASE = '/api';
        const START_TIME = new Date({{ start_time_ms }});

        function formatUptime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = seconds % 60;
            return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        }

        function updateUptime() {
            const now = new Date();
            const diff = Math.floor((now - START_TIME) / 1000);
            document.getElementById('uptime').textContent = formatUptime(diff);
        }

        function updateLastUpdate() {
            const now = new Date();
            document.getElementById('last-update').textContent = 
                now.toLocaleTimeString('es-ES');
        }

        async function fetchDashboardData() {
            try {
                const statusRes = await fetch(`${API_BASE}/status`);
                const status = await statusRes.json();
                updateServicesUI(status);
                populateLogServices(status);

                const systemRes = await fetch(`${API_BASE}/system`);
                const system = await systemRes.json();
                updateSystemUI(system);

                updateLastUpdate();
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }

        function updateServicesUI(services) {
            const container = document.getElementById('services-container');
            
            if (!Array.isArray(services) || services.length === 0) {
                container.innerHTML = '<p class="text-slate-400 text-sm">No services found</p>';
                return;
            }

            container.innerHTML = services.map(service => `
                <div class="flex items-start justify-between p-3 bg-slate-800 bg-opacity-30 rounded border border-slate-700">
                    <div class="flex items-start gap-3 flex-1">
                        <div class="led ${service.state === 'running' ? 'up' : 'down'}"></div>
                        <div class="flex-1">
                            <p class="font-mono-tech text-cyan-accent font-semibold">${service.name}</p>
                            <p class="text-xs text-slate-400 mt-1">${service.image}</p>
                            <div class="flex gap-2 mt-2 flex-wrap">
                                <span class="status-badge ${service.state === 'running' ? 'running' : 'exited'}">
                                    ${service.state}
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="text-right ml-4">
                        <div class="metric">
                            <div class="metric-label">CPU</div>
                            <div class="metric-value text-sm">${service.cpu}</div>
                        </div>
                        <div class="metric mt-2">
                            <div class="metric-label">RAM</div>
                            <div class="metric-value text-sm">${service.memory_perc}</div>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        function updateSystemUI(system) {
            if (system.error) {
                console.error('System stats error:', system.error);
                return;
            }

            // CPU
            document.getElementById('cpu-value').textContent = system.cpu + '%';
            document.getElementById('cpu-bar').style.width = system.cpu + '%';

            // RAM
            const ramPerc = system.ram_percentage || 0;
            document.getElementById('ram-value').textContent = ramPerc.toFixed(1) + '%';
            document.getElementById('ram-usage').textContent = 
                `${system.ram_total - system.ram_free} GB / ${system.ram_total} GB`;
            document.getElementById('ram-bar').style.width = ramPerc + '%';

            // Disk
            const diskPerc = system.disk_percentage || 0;
            document.getElementById('disk-value').textContent = diskPerc + '%';
            document.getElementById('disk-usage').textContent = 
                `${system.disk_used} / ${system.disk_total}`;
            document.getElementById('disk-bar').style.width = diskPerc + '%';
        }

        function populateLogServices(services) {
            const select = document.getElementById('log-service');
            const currentValue = select.value;
            
            select.innerHTML = '<option value="">Select a service...</option>';
            
            if (Array.isArray(services)) {
                services.forEach(service => {
                    const option = document.createElement('option');
                    option.value = service.name;
                    option.textContent = service.name;
                    select.appendChild(option);
                });
            }
            
            if (currentValue) {
                select.value = currentValue;
            }
        }

        document.getElementById('log-service').addEventListener('change', async (e) => {
            const service = e.target.value;
            const container = document.getElementById('logs-container');
            
            if (!service) {
                container.innerHTML = '<p class="text-slate-500 text-xs font-mono-tech">Select a service to view logs</p>';
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/logs?service=${service}`);
                const logs = await response.text();
                container.innerHTML = `<pre class="font-mono-tech text-xs text-emerald-accent whitespace-pre-wrap break-words">${logs}</pre>`;
            } catch (error) {
                container.innerHTML = `<p class="text-red-500 text-xs">Error loading logs: ${error.message}</p>`;
            }
        });

        // Initial fetch and auto-refresh
        updateUptime();
        fetchDashboardData();
        setInterval(updateUptime, 1000);
    </script>
</body>
</html>
"""

# ==================== BACKEND LOGIC ====================

def get_docker_status():
    """Get Docker Compose service status and statistics."""
    try:
        # Get container info from docker compose
        ps_output = subprocess.check_output(
            ['docker', 'compose', 'ps', '-a', '--format', 'json'],
            cwd='/home/vboxuser/proyectoserver',
            stderr=subprocess.DEVNULL
        ).decode('utf-8')
        
        containers = []
        for line in ps_output.strip().split('\n'):
            if line.strip():
                try:
                    containers.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        
        # Get stats from docker stats
        try:
            stats_output = subprocess.check_output(
                ['docker', 'stats', '--no-stream', '--format', 'json'],
                stderr=subprocess.DEVNULL
            ).decode('utf-8')
            
            stats_map = {}
            for line in stats_output.strip().split('\n'):
                if line.strip():
                    try:
                        stat = json.loads(line)
                        name = stat.get('Name', '')
                        stats_map[name] = stat
                    except json.JSONDecodeError:
                        pass
        except subprocess.CalledProcessError:
            stats_map = {}
        
        # Combine data
        result = []
        for container in containers:
            name = container.get('Name') or container.get('Names', '')
            stat = stats_map.get(name, {})
            
            result.append({
                "id": container.get('ID', '')[:12],
                "name": name,
                "service": container.get('Service', ''),
                "image": container.get('Image', ''),
                "state": container.get('State', 'unknown'),
                "status": container.get('Status', ''),
                "ports": container.get('Ports', ''),
                "cpu": stat.get('CPUPerc', '0.00%'),
                "memory": stat.get('MemUsage', '0B / 0B'),
                "memory_perc": stat.get('MemPerc', '0.00%')
            })
        
        return result
    except Exception as e:
        return {"error": str(e)}


def get_system_stats():
    """Get system CPU, RAM, and Disk usage."""
    stats = {}
    
    # CPU usage
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        stats['cpu'] = round(cpu_percent, 1)
    except Exception:
        stats['cpu'] = 0.0
    
    # RAM usage
    try:
        ram = psutil.virtual_memory()
        stats['ram_total'] = round(ram.total / (1024**3), 2)
        stats['ram_free'] = round(ram.available / (1024**3), 2)
        stats['ram_percentage'] = round(ram.percent, 1)
    except Exception:
        stats['ram_total'] = 0.0
        stats['ram_free'] = 0.0
        stats['ram_percentage'] = 0.0
    
    # Disk usage
    try:
        disk = psutil.disk_usage('/')
        stats['disk_total'] = f"{round(disk.total / (1024**3), 1)} GB"
        stats['disk_used'] = f"{round(disk.used / (1024**3), 1)} GB"
        stats['disk_free'] = f"{round(disk.free / (1024**3), 1)} GB"
        stats['disk_percentage'] = int(disk.percent)
    except Exception:
        stats['disk_total'] = "N/A"
        stats['disk_used'] = "N/A"
        stats['disk_free'] = "N/A"
        stats['disk_percentage'] = 0
    
    return stats


def get_docker_logs(service):
    """Get the last 100 lines of logs for a service."""
    try:
        logs = subprocess.check_output(
            ['docker', 'compose', 'logs', '--tail=100', service],
            cwd='/home/vboxuser/proyectoserver',
            stderr=subprocess.STDOUT
        ).decode('utf-8')
        return logs
    except Exception as e:
        return f"Error al obtener logs para '{service}': {str(e)}"


def restart_docker_service(service):
    """Restart a Docker Compose service."""
    try:
        subprocess.check_call(
            ['docker', 'compose', 'restart', service],
            cwd='/home/vboxuser/proyectoserver',
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True, None
    except Exception as e:
        return False, str(e)


# ==================== FLASK ROUTES ====================

@app.route('/')
def dashboard():
    """Render the main dashboard."""
    start_time_ms = int(datetime.now().timestamp() * 1000)
    return render_template_string(DASHBOARD_TEMPLATE, start_time_ms=start_time_ms)


@app.route('/api/status')
def api_status():
    """API endpoint for Docker service status."""
    status = get_docker_status()
    return jsonify(status)


@app.route('/api/system')
def api_system():
    """API endpoint for system statistics."""
    system = get_system_stats()
    return jsonify(system)


@app.route('/api/logs')
def api_logs():
    """API endpoint for service logs."""
    service = request.args.get('service')
    if not service:
        return jsonify({"error": "Missing 'service' parameter"}), 400
    
    logs = get_docker_logs(service)
    return logs, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route('/api/restart', methods=['POST'])
def api_restart():
    """API endpoint to restart a service."""
    data = request.get_json()
    service = data.get('service') if data else None
    
    if not service:
        return jsonify({"error": "Missing 'service' field"}), 400
    
    success, error = restart_docker_service(service)
    return jsonify({"success": success, "error": error}), 200 if success else 500


# ==================== MAIN ====================

if __name__ == '__main__':
    print("🚀 Infrastructure Control Panel running on http://localhost:5000")
    print("⚙️  Auto-refresh enabled: every 10 seconds")
    app.run(host='0.0.0.0', port=5000, debug=False)
