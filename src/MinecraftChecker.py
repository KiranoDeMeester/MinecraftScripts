import subprocess

def is_minecraft_running():
    """Checks if Minecraft process (javaw.exe or minecraft.exe) is active on Windows"""
    try:
        output = subprocess.check_output('tasklist /FI "IMAGENAME eq javaw.exe"', shell=True).decode()
        if "javaw.exe" in output.lower():
            return True
        output_mc = subprocess.check_output('tasklist /FI "IMAGENAME eq Minecraft.exe"', shell=True).decode()
        if "minecraft.exe" in output_mc.lower():
            return True
    except Exception:
        pass
    return False
