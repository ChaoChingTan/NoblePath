import subprocess

def run_container():
    container_name = "week3"
    network_name = "root_websploit"
    ip_address = "10.6.6.68"
    image_name = "chaoching/lab"
    
    # Stop and remove existing container if it exists
    subprocess.run(["docker", "rm", "-f", container_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Pull the latest image
    # print("Pulling image...")
    print("Pulling image...")
    subprocess.run(["docker", "pull", image_name], check=True, stdout=subprocess.DEVNULL)
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
    run_container()

