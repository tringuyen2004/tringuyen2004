import psutil
import requests
import platform
import socket
import time
import os

root_drive = os.path.abspath(os.sep)

def getSystemInfo():
    # Get system info
    hostname = socket.gethostname()
    system = platform.system()
    release = platform.release()

    # Measure each core in the CPU for 5 seconds
    cpu_usage = psutil.cpu_percent(interval=5, percpu=True)

    # Get memory usage in percentages
    memory_usage = psutil.virtual_memory().percent

    # Get disk usage
    disk_usage = psutil.disk_usage(root_drive).percent

    # Get system current uptime
    uptime_seconds = time.time() - psutil.boot_time()
    uptime_string = time.strftime('%d days, %H:%M:%S', time.gmtime(uptime_seconds))

    # Get top processes by memory usage
    process_list = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            process_list.append({
                "pid": proc.info['pid'],
                "name": proc.info['name'],
                "memory": proc.info['memory_info'].rss / (1024 * 1024)  # Convert bytes to MB
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Sort processes by memory usage (descending)
    process_list = sorted(process_list, key=lambda x: x['memory'], reverse=True)

    # Prepare a readable list of the top 10 memory-consuming processes
    top_processes = "\n".join(
        [f"{p['name']} (PID: {p['pid']}): {p['memory']:.2f} MB" for p in process_list[:5]]
    )

    # Create the message
    message = (
        f"**System Health Report**\n"
        f"**Hostname**: {hostname}\n"
        f"**System**: {system} {release}\n"
        f"**CPU Usage (per core)**: {', '.join([f'{core}%' for core in cpu_usage])}\n"
        f"**Memory Usage**: {memory_usage}%\n"
        f"**Disk Usage**: {disk_usage}%\n"
        f"**Uptime**: {uptime_string}\n\n"
        f"**Top Processes by Memory Usage**:\n{top_processes}"
    )

    return message 

def sendtoDiscord(webhook_url, message):
    data = {"content": message}
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message: {response.status_code}, {response.text}")

if __name__ == "__main__":
    # Set your Discord webhook URL here
    discordwebhook = "Discord Webhook goes here"

    # Check system health and send to Discord
    system_info = getSystemInfo()
    sendtoDiscord(discordwebhook, system_info)  # Send the report to Discord
