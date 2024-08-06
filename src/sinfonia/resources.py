import subprocess
import psutil
import GPUtil


def gpu_power() -> float:
    """Get GPU power in milli-watts
    
    Must have "nvidia-smi" installed.
    """
    def _output_to_list(x): return x.decode('ascii').split('\n')[:-1]
    COMMAND = "nvidia-smi --query-gpu=power.draw --format=csv"
    
    try:
        result = _output_to_list(subprocess.check_output(COMMAND.split()))[1:][0]
        power = float(result.split()[0]) * 1000  # to ensue its milliwatt as well
    except:
        power = -1
        
    return power


def has_gpu():
    gpus = GPUtil.getGPUs()
    if len(gpus) > 0:
        return True
    else:
        return False


def cpu_count() -> float:
    """Get number of virtual CPU cores in system
    """
    return psutil.cpu_count(logical=True)


def mem_count() -> float:
    """Get number of RAM in megabytes in system
    """
    return psutil.virtual_memory().total / (1024 * 1024)  # bytes to megabytes
