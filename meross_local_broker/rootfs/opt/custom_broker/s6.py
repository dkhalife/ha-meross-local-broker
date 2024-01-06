from asyncio import subprocess
from asyncore import read
from subprocess import Popen, PIPE
from typing import Dict, Optional, List, Tuple
from os import path
from db_helper import dbhelper
from model.exception import BadRequestError
from model.enums import EventType


class ServiceDescriptor:
    def __init__(self, name: str, service_dir: str, log_dir: str, description: str = None) -> None:
        self._name = name
        self._service_dir = service_dir
        self._log_dir = log_dir
        self._description = description

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def service_dir(self) -> str:
        return self._service_dir

    @property
    def log_dir(self) -> str:
        return self._log_dir

    def serialize(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description
        }


class ServiceInfo:
    def __init__(self, descriptor: ServiceDescriptor, up: bool, ready: bool, pid: int, exit_code: int = None) -> None:
        self._descriptor = descriptor
        self._up = up
        self._ready = ready
        self._pid = pid
        self._exit_code = exit_code
    
    @property
    def descriptor(self) -> ServiceDescriptor:
        return self._descriptor

    @property
    def status(self):
        if self._up:
            return "RUNNING"
        elif self._ready:
            return "STOPPED"
        else:
            return "DOWN"
    
    @property
    def exit_code(self) -> Optional[int]:
        if self._up:
            return None
        return self._exit_code

    @property
    def pid(self) -> Optional[int]:
        if self._up:
            return self._pid
        return None

    def serialize(self) -> Dict:
        return {
            "name": self._descriptor.name,
            "description": self.descriptor.description,
            "status": self.status,
            "exitCode": self.exit_code,
            "pid": self.pid
        }


class ServiceManager:
    _SERVICE_DIRS = {
        "Local API": ServiceDescriptor("Local API", "/var/run/s6/legacy-services/api", "/var/log/api", "Local HTTP web API server"),
        "Local Agent": ServiceDescriptor("Local Agent", "/var/run/s6/legacy-services/broker", "/var/log/broker", "Local Meross Agent running over MQTT service"),
        "Web UI Proxy": ServiceDescriptor("Web UI Proxy", "/var/run/s6/legacy-services/nginx", "/var/log/nginx", "Web UI reverse proxy")
    }

    def get_service_info(self, service_name: str) -> Optional[ServiceInfo]:
        service_descriptor=self._SERVICE_DIRS.get(service_name)
        if service_descriptor is None:
            return None
        process = Popen(['s6-svstat', '-o', 'up,ready,pid,exitcode', service_descriptor.service_dir], stdout=PIPE, universal_newlines=True)
        stdout, stderr = process.communicate()
        up, ready, pid, exitcode = stdout.split()
        pid = int (pid) if pid is not None else None
        exitcode = int (exitcode) if exitcode is not None else None
        return ServiceInfo(descriptor=service_descriptor, up=up.lower()=='true', ready=ready.lower()=='true', pid=pid, exit_code=exitcode)

    def get_services_info(self) -> List[ServiceInfo]:
        return [self.get_service_info(s) for s in self._SERVICE_DIRS]

    def stop_service(self, service_name: str, wait: bool = True) -> Tuple[Optional[int], Optional[str]]:
        """Stops the process"""
        service_descriptor=self._SERVICE_DIRS.get(service_name)
        if service_descriptor is None:
            raise BadRequestError("Invalid service name specified.")
        process = Popen(['/usr/bin/s6-svc', '-wD', '-d', service_descriptor.service_dir], shell=False, stdout=PIPE, stderr=subprocess.STDOUT)
        if wait:
            stdout, stderr = process.communicate()
            dbhelper.store_event(event_type=EventType.SERVICE_STOP, details=f"Service {service_name}; stop command returned {process.returncode}.")
            return process.returncode, stdout.decode('utf-8')
        
        dbhelper.store_event(event_type=EventType.SERVICE_STOP, details=f"Service {service_name}; stop result not awaited.")
        return None, None

    def start_service(self, service_name: str, wait: bool = True) -> Tuple[Optional[int], Optional[str]]:
        """Starts the process"""
        service_descriptor=self._SERVICE_DIRS.get(service_name)
        if service_descriptor is None:
            raise BadRequestError("Invalid service name specified.")
        process = Popen(['/usr/bin/s6-svc', '-wU', '-u', service_descriptor.service_dir], shell=False, stdout=PIPE, stderr=subprocess.STDOUT)
        if wait:
            stdout, stderr = process.communicate()
            dbhelper.store_event(event_type=EventType.SERVICE_START, details=f"Service {service_name}; start command returned {process.returncode}.")
            return process.returncode, stdout.decode('utf-8')
        dbhelper.store_event(event_type=EventType.SERVICE_START, details=f"Service {service_name}; start result not awaited.")
        return None, None

    def restart_service(self, service_name: str, wait: bool = True) -> Tuple[Optional[int], Optional[str]]:
        """Starts the process"""
        service_descriptor = self._SERVICE_DIRS.get(service_name)
        if service_descriptor is None:
            raise BadRequestError("Invalid service name specified.")
        process = Popen(['/usr/bin/s6-svc', '-wR', '-r', service_descriptor.service_dir], shell=False, stdout=PIPE, stderr=subprocess.STDOUT)
        if wait:
            stdout, stderr = process.communicate()
            dbhelper.store_event(event_type=EventType.SERVICE_RESTART, details=f"Service {service_name}; restart command returned {process.returncode}.")
            return process.returncode, stdout.decode('utf-8')
        dbhelper.store_event(event_type=EventType.SERVICE_RESTART, details=f"Service {service_name}; restart command not awaited.")
        return None, None

    def get_log(self, service_name: str, tail: Optional[int] = 100) -> List[str]:
        """Retrieves the s6 log of that process/service"""
        service_descriptor = self._SERVICE_DIRS.get(service_name)
        if service_descriptor is None:
            raise BadRequestError("Invalid service name specified.")

        # In case log_dir is None, it means that we have no logs for that service
        if service_descriptor.log_dir is None:
            return []

        log_file = path.join(service_descriptor.log_dir, "current")
        with open(log_file, "r") as f:
            lines = f.readlines()
            if tail is not None:
                return lines[-tail:]
            return lines


service_manager = ServiceManager()
