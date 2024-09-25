import subprocess

def disconnect_active_connections():
    try:
        # Get the list of active connections
        result = subprocess.run(["nmcli", "connection", "show", "--active"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode().strip()

        # If there's an active connection, extract the connection name and disconnect it
        if "wlan0" in output:
            lines = output.split("\n")
            for line in lines:
                if "wlan0" in line:
                    connection_name = line.split()[0]
                    print(f"Disconnecting from active connection: {connection_name}")
                    subprocess.run(["nmcli", "connection", "down", connection_name], check=True)
                    break
    except subprocess.CalledProcessError as e:
        print(f"Error while disconnecting active connections: {e}")

def start_hotspot(ssid, password):
    try:
        # Disconnect any active connections on wlan0
        disconnect_active_connections()

        # Start the hotspot without turning off Wi-Fi
        subprocess.run([
            "nmcli", "dev", "wifi", "hotspot",
            "ifname", "wlan0",  # Adjust wlan0 if necessary
            "con-name", ssid,
            "ssid", ssid,
            "password", password
        ], check=True)

        print(f"Hotspot '{ssid}' started successfully with password '{password}'")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start hotspot. Error: {e}")
        print(e.stdout.decode())
        print(e.stderr.decode())

if __name__ == "__main__":
    # Replace with your desired SSID and password
    ssid = "Robot"
    password = "123456789"
    
    start_hotspot(ssid, password)
