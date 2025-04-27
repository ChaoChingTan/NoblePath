import subprocess

def run_telnetd_container():
    container_name = "telnetd_container"
    network_name = "root_websploit"
    ip_address = "10.6.6.66"
    image_name = "wistic/telnetd"
    
    # Stop and remove existing container if it exists
    subprocess.run(["docker", "rm", "-f", container_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Pull the latest image
    # print("Pulling wistic/telnetd image...")
    print("Pulling image...")
    subprocess.run(["docker", "pull", image_name], check=True)
    print("Image pulled successfully!")
    
    # Start the container with the specified network and IP
    print("Starting the container...")
    subprocess.run([
        "docker", "run", "-d", "--name", container_name,
        "--network", network_name, "--ip", ip_address,
        image_name
    ], check=True)
    
    print(f"Container started successfully with IP {ip_address} on network {network_name}!")

if __name__ == "__main__":
    run_telnetd_container()

