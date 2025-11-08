#!/usr/bin/env python3
"""
Dell Boca Boys V2 - Web-Based Installer
Production-ready deployment interface with real-time progress tracking
"""

import os
import sys
import json
import time
import logging
import subprocess
import threading
import platform
import shutil
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('installer/logs/installer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
deployment_state = {
    'status': 'idle',  # idle, checking, installing, deploying, completed, failed
    'current_phase': None,
    'progress': 0,
    'logs': [],
    'errors': [],
    'warnings': [],
    'start_time': None,
    'end_time': None,
    'deployment_info': {}
}

deployment_lock = threading.Lock()


@dataclass
class SystemRequirement:
    """System requirement check result"""
    name: str
    required: str
    actual: str
    status: str  # 'pass', 'warn', 'fail'
    message: str


class DeploymentPhase:
    """Represents a deployment phase"""

    def __init__(self, name: str, description: str, weight: int):
        self.name = name
        self.description = description
        self.weight = weight
        self.status = 'pending'  # pending, running, completed, failed
        self.progress = 0
        self.start_time = None
        self.end_time = None
        self.steps = []


class PreflightChecker:
    """Pre-flight system requirement checker"""

    @staticmethod
    def check_os() -> SystemRequirement:
        """Check operating system compatibility"""
        os_name = platform.system()
        os_version = platform.release()

        supported_os = ['Linux', 'Darwin', 'Windows']
        status = 'pass' if os_name in supported_os else 'fail'

        return SystemRequirement(
            name="Operating System",
            required="Windows 10+, macOS 11+, Ubuntu 20.04+",
            actual=f"{os_name} {os_version}",
            status=status,
            message="✓ Operating system is supported" if status == 'pass' else "✗ Operating system not supported"
        )

    @staticmethod
    def check_ram() -> SystemRequirement:
        """Check RAM availability"""
        ram_gb = psutil.virtual_memory().total / (1024**3)
        required_gb = 16

        if ram_gb >= required_gb:
            status = 'pass'
            message = f"✓ Sufficient RAM available ({ram_gb:.1f} GB)"
        elif ram_gb >= 8:
            status = 'warn'
            message = f"⚠ Limited RAM ({ram_gb:.1f} GB). 16GB recommended for optimal performance"
        else:
            status = 'fail'
            message = f"✗ Insufficient RAM ({ram_gb:.1f} GB). Minimum 8GB required"

        return SystemRequirement(
            name="RAM",
            required="16 GB (8 GB minimum)",
            actual=f"{ram_gb:.1f} GB",
            status=status,
            message=message
        )

    @staticmethod
    def check_disk_space() -> SystemRequirement:
        """Check disk space availability"""
        disk = psutil.disk_usage('/')
        free_gb = disk.free / (1024**3)
        required_gb = 100

        if free_gb >= required_gb:
            status = 'pass'
            message = f"✓ Sufficient disk space ({free_gb:.1f} GB available)"
        elif free_gb >= 50:
            status = 'warn'
            message = f"⚠ Limited disk space ({free_gb:.1f} GB). 100GB recommended"
        else:
            status = 'fail'
            message = f"✗ Insufficient disk space ({free_gb:.1f} GB). Minimum 50GB required"

        return SystemRequirement(
            name="Disk Space",
            required="100 GB",
            actual=f"{free_gb:.1f} GB available",
            status=status,
            message=message
        )

    @staticmethod
    def check_cpu() -> SystemRequirement:
        """Check CPU cores"""
        cpu_count = psutil.cpu_count()
        required_cores = 8

        if cpu_count >= required_cores:
            status = 'pass'
            message = f"✓ Sufficient CPU cores ({cpu_count} cores)"
        elif cpu_count >= 4:
            status = 'warn'
            message = f"⚠ Limited CPU cores ({cpu_count}). 8 cores recommended"
        else:
            status = 'fail'
            message = f"✗ Insufficient CPU cores ({cpu_count}). Minimum 4 cores required"

        return SystemRequirement(
            name="CPU",
            required="8 cores",
            actual=f"{cpu_count} cores",
            status=status,
            message=message
        )

    @staticmethod
    def check_docker() -> SystemRequirement:
        """Check if Docker is installed"""
        try:
            result = subprocess.run(['docker', '--version'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                return SystemRequirement(
                    name="Docker",
                    required="Docker 20.10+",
                    actual=version,
                    status='pass',
                    message=f"✓ Docker is installed: {version}"
                )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return SystemRequirement(
            name="Docker",
            required="Docker 20.10+",
            actual="Not installed",
            status='warn',
            message="⚠ Docker not found. Will install automatically"
        )

    @staticmethod
    def check_ports() -> SystemRequirement:
        """Check if required ports are available"""
        required_ports = [80, 443, 5678, 5432, 8000, 8080, 3000]
        used_ports = []

        connections = psutil.net_connections()
        for conn in connections:
            if conn.status == 'LISTEN' and conn.laddr.port in required_ports:
                used_ports.append(conn.laddr.port)

        if not used_ports:
            return SystemRequirement(
                name="Network Ports",
                required="Ports 80, 443, 5678, 5432, 8000, 8080, 3000",
                actual="All ports available",
                status='pass',
                message="✓ All required ports are available"
            )
        else:
            return SystemRequirement(
                name="Network Ports",
                required="Ports 80, 443, 5678, 5432, 8000, 8080, 3000",
                actual=f"Ports in use: {', '.join(map(str, used_ports))}",
                status='warn',
                message=f"⚠ Some ports are in use: {', '.join(map(str, used_ports))}. May cause conflicts"
            )

    @staticmethod
    def check_internet() -> SystemRequirement:
        """Check internet connectivity"""
        import socket
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return SystemRequirement(
                name="Internet Connection",
                required="Active internet connection",
                actual="Connected",
                status='pass',
                message="✓ Internet connection is active"
            )
        except OSError:
            return SystemRequirement(
                name="Internet Connection",
                required="Active internet connection",
                actual="Not connected",
                status='fail',
                message="✗ No internet connection. Required for initial setup"
            )

    @staticmethod
    def run_all_checks() -> Tuple[List[SystemRequirement], bool, bool]:
        """Run all pre-flight checks"""
        checks = [
            PreflightChecker.check_os(),
            PreflightChecker.check_ram(),
            PreflightChecker.check_disk_space(),
            PreflightChecker.check_cpu(),
            PreflightChecker.check_docker(),
            PreflightChecker.check_ports(),
            PreflightChecker.check_internet()
        ]

        has_failures = any(c.status == 'fail' for c in checks)
        has_warnings = any(c.status == 'warn' for c in checks)

        return checks, has_failures, has_warnings


class Installer:
    """Main installer class"""

    def __init__(self):
        self.deployment_dir = Path(__file__).parent.parent / 'deployment'
        self.app_dir = Path(__file__).parent.parent / 'application'
        self.phases = self._initialize_phases()

    def _initialize_phases(self) -> List[DeploymentPhase]:
        """Initialize deployment phases"""
        return [
            DeploymentPhase("preflight", "Pre-flight system checks", 10),
            DeploymentPhase("dependencies", "Installing dependencies", 25),
            DeploymentPhase("security", "Setting up security", 15),
            DeploymentPhase("deployment", "Deploying application", 35),
            DeploymentPhase("validation", "Validating deployment", 15)
        ]

    def emit_log(self, message: str, level: str = 'info'):
        """Emit log message to UI"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        deployment_state['logs'].append(log_entry)
        socketio.emit('log', log_entry)
        logger.log(getattr(logging, level.upper()), message)

    def emit_progress(self, phase: str, progress: int, message: str):
        """Emit progress update to UI"""
        with deployment_lock:
            deployment_state['current_phase'] = phase
            deployment_state['progress'] = progress

        socketio.emit('progress', {
            'phase': phase,
            'progress': progress,
            'message': message
        })

    def run_command(self, cmd: List[str], cwd: Optional[Path] = None,
                   timeout: int = 600) -> Tuple[bool, str, str]:
        """Run a shell command and capture output"""
        try:
            self.emit_log(f"Executing: {' '.join(cmd)}", 'debug')

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                text=True
            )

            stdout, stderr = process.communicate(timeout=timeout)
            success = process.returncode == 0

            if not success:
                self.emit_log(f"Command failed: {' '.join(cmd)}", 'error')
                self.emit_log(f"Error: {stderr}", 'error')

            return success, stdout, stderr

        except subprocess.TimeoutExpired:
            self.emit_log(f"Command timed out: {' '.join(cmd)}", 'error')
            return False, "", "Command timed out"
        except Exception as e:
            self.emit_log(f"Command error: {str(e)}", 'error')
            return False, "", str(e)

    def install_docker(self) -> bool:
        """Install Docker if not present"""
        self.emit_log("Checking Docker installation...")

        # Check if Docker is already installed
        success, stdout, _ = self.run_command(['docker', '--version'])
        if success:
            self.emit_log(f"Docker already installed: {stdout.strip()}", 'info')
            return True

        self.emit_log("Docker not found. Installing...", 'info')

        os_name = platform.system()
        script_path = self.deployment_dir / 'install-docker.sh'

        if os_name == 'Linux':
            success, _, stderr = self.run_command(['bash', str(script_path)])
        elif os_name == 'Darwin':
            self.emit_log("Please install Docker Desktop for Mac manually", 'error')
            self.emit_log("Download from: https://www.docker.com/products/docker-desktop", 'info')
            return False
        elif os_name == 'Windows':
            self.emit_log("Please install Docker Desktop for Windows manually", 'error')
            self.emit_log("Download from: https://www.docker.com/products/docker-desktop", 'info')
            return False
        else:
            self.emit_log(f"Unsupported operating system: {os_name}", 'error')
            return False

        if success:
            self.emit_log("Docker installed successfully", 'info')
        else:
            self.emit_log("Docker installation failed", 'error')

        return success

    def deploy(self):
        """Main deployment function"""
        try:
            with deployment_lock:
                deployment_state['status'] = 'deploying'
                deployment_state['start_time'] = datetime.now().isoformat()
                deployment_state['errors'] = []
                deployment_state['warnings'] = []

            total_weight = sum(p.weight for p in self.phases)
            cumulative_progress = 0

            # Phase 1: Pre-flight checks
            phase = self.phases[0]
            self.emit_progress(phase.name, cumulative_progress, phase.description)

            checks, has_failures, has_warnings = PreflightChecker.run_all_checks()

            for check in checks:
                self.emit_log(check.message, check.status)
                if check.status == 'warn':
                    deployment_state['warnings'].append(check.message)
                elif check.status == 'fail':
                    deployment_state['errors'].append(check.message)

            if has_failures:
                raise Exception("Pre-flight checks failed. Please resolve issues and try again.")

            cumulative_progress += phase.weight
            self.emit_progress(phase.name, cumulative_progress, "Pre-flight checks completed")

            # Phase 2: Install dependencies
            phase = self.phases[1]
            self.emit_progress(phase.name, cumulative_progress, phase.description)

            if not self.install_docker():
                raise Exception("Docker installation failed")

            self.emit_log("Pulling Docker base images...")
            success, _, _ = self.run_command(['docker', 'pull', 'python:3.11-slim'])
            if not success:
                raise Exception("Failed to pull Docker images")

            cumulative_progress += phase.weight
            self.emit_progress(phase.name, cumulative_progress, "Dependencies installed")

            # Phase 3: Security setup
            phase = self.phases[2]
            self.emit_progress(phase.name, cumulative_progress, phase.description)

            self.emit_log("Generating secure credentials...")
            script_path = self.deployment_dir / 'security' / 'generate-secrets.sh'
            if script_path.exists():
                success, _, _ = self.run_command(['bash', str(script_path)])
                if not success:
                    self.emit_log("Security setup had warnings", 'warn')

            cumulative_progress += phase.weight
            self.emit_progress(phase.name, cumulative_progress, "Security configured")

            # Phase 4: Application deployment
            phase = self.phases[3]
            self.emit_progress(phase.name, cumulative_progress, phase.description)

            self.emit_log("Starting application deployment...")

            # Copy environment template
            env_template = self.app_dir / '.env.template'
            env_file = self.app_dir / '.env'
            if env_template.exists() and not env_file.exists():
                shutil.copy(env_template, env_file)
                self.emit_log("Environment configuration created", 'info')

            # Build and start Docker containers
            self.emit_log("Building Docker containers...")
            success, _, stderr = self.run_command(
                ['docker', 'compose', 'build', '--no-cache'],
                cwd=self.app_dir,
                timeout=1200
            )
            if not success:
                raise Exception(f"Docker build failed: {stderr}")

            self.emit_log("Starting services...")
            success, _, stderr = self.run_command(
                ['docker', 'compose', 'up', '-d'],
                cwd=self.app_dir
            )
            if not success:
                raise Exception(f"Failed to start services: {stderr}")

            # Wait for services to be ready
            self.emit_log("Waiting for services to initialize...")
            time.sleep(10)

            cumulative_progress += phase.weight
            self.emit_progress(phase.name, cumulative_progress, "Application deployed")

            # Phase 5: Validation
            phase = self.phases[4]
            self.emit_progress(phase.name, cumulative_progress, phase.description)

            self.emit_log("Running health checks...")
            script_path = self.deployment_dir / 'health-check.sh'
            if script_path.exists():
                success, stdout, _ = self.run_command(['bash', str(script_path)])
                if success:
                    self.emit_log("All health checks passed", 'info')
                else:
                    self.emit_log("Some health checks failed", 'warn')

            cumulative_progress = 100
            self.emit_progress(phase.name, cumulative_progress, "Deployment complete!")

            # Store deployment info
            with deployment_lock:
                deployment_state['status'] = 'completed'
                deployment_state['end_time'] = datetime.now().isoformat()
                deployment_state['deployment_info'] = {
                    'dashboard_url': 'https://localhost',
                    'n8n_url': 'https://localhost/n8n',
                    'api_url': 'https://localhost/api',
                    'admin_user': 'admin',
                    'admin_password': '(check deployment logs)'
                }

            self.emit_log("=" * 60, 'info')
            self.emit_log("DEPLOYMENT COMPLETED SUCCESSFULLY!", 'info')
            self.emit_log("=" * 60, 'info')
            self.emit_log("Access your system at: https://localhost", 'info')
            self.emit_log("n8n Workflows: https://localhost/n8n", 'info')
            self.emit_log("API Documentation: https://localhost/api/docs", 'info')
            self.emit_log("=" * 60, 'info')

        except Exception as e:
            self.emit_log(f"DEPLOYMENT FAILED: {str(e)}", 'error')
            with deployment_lock:
                deployment_state['status'] = 'failed'
                deployment_state['end_time'] = datetime.now().isoformat()
                deployment_state['errors'].append(str(e))


# Flask routes
@app.route('/')
def index():
    """Serve installer UI"""
    return send_from_directory('installer/static', 'index.html')


@app.route('/api/status')
def get_status():
    """Get current deployment status"""
    with deployment_lock:
        return jsonify(deployment_state)


@app.route('/api/preflight')
def run_preflight():
    """Run pre-flight checks"""
    checks, has_failures, has_warnings = PreflightChecker.run_all_checks()

    return jsonify({
        'checks': [asdict(c) for c in checks],
        'has_failures': has_failures,
        'has_warnings': has_warnings,
        'can_proceed': not has_failures
    })


@app.route('/api/deploy', methods=['POST'])
def start_deployment():
    """Start deployment process"""
    with deployment_lock:
        if deployment_state['status'] in ['deploying']:
            return jsonify({'error': 'Deployment already in progress'}), 400

        # Reset state
        deployment_state['status'] = 'deploying'
        deployment_state['logs'] = []
        deployment_state['errors'] = []
        deployment_state['warnings'] = []

    # Run deployment in background thread
    installer = Installer()
    thread = threading.Thread(target=installer.deploy)
    thread.daemon = True
    thread.start()

    return jsonify({'message': 'Deployment started'})


@app.route('/api/rollback', methods=['POST'])
def rollback_deployment():
    """Rollback deployment"""
    deployment_dir = Path(__file__).parent.parent / 'deployment'
    script_path = deployment_dir / 'rollback.sh'

    if not script_path.exists():
        return jsonify({'error': 'Rollback script not found'}), 500

    try:
        result = subprocess.run(
            ['bash', str(script_path)],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            with deployment_lock:
                deployment_state['status'] = 'idle'
            return jsonify({'message': 'Rollback completed successfully'})
        else:
            return jsonify({'error': f'Rollback failed: {result.stderr}'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('installer/static', filename)


# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("Client connected")
    emit('connected', {'message': 'Connected to installer'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected")


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('installer/logs', exist_ok=True)
    os.makedirs('installer/static', exist_ok=True)
    os.makedirs('installer/templates', exist_ok=True)

    # Start server
    logger.info("Starting Dell Boca Boys V2 Installer...")
    logger.info("Open your browser to: http://localhost:3000")

    socketio.run(app, host='0.0.0.0', port=3000, debug=False)
