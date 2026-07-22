import platform
import logging

logger = logging.getLogger(__name__)

class SystemMonitor:
    """Approximates system resources without requiring psutil."""
    
    @staticmethod
    def get_cpu_load() -> float:
        if platform.system() == "Linux":
            try:
                with open('/proc/loadavg', 'r') as f:
                    return float(f.read().split()[0])
            except Exception:
                pass
        elif platform.system() == "Darwin":
            try:
                import subprocess
                res = subprocess.run(['sysctl', '-n', 'vm.loadavg'], capture_output=True, text=True)
                # Output format: { 1.23 1.45 1.56 }
                parts = res.stdout.strip().replace('{', '').replace('}', '').strip().split()
                if parts:
                    return float(parts[0])
            except Exception:
                pass
        return 0.0
        
    @staticmethod
    def get_memory_usage_mb() -> float:
        # Just return the current process memory using built-ins (basic approximation)
        try:
            import resource
            usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            if platform.system() == "Darwin":
                return usage / (1024 * 1024) # bytes to MB
            else:
                return usage / 1024 # KB to MB
        except ImportError:
            return 0.0
