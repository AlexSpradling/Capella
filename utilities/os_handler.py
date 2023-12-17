import platform

def get_os_type():
    os_name = platform.system()

    if os_name == "Windows":
        return "Windows"
    elif os_name in ["Linux", "Darwin"]:  # Darwin is for macOS
        return "Unix"
    else:
        return "Unknown"

# Example usage
os_type = get_os_type()
print(f"The operating system is: {os_type}")