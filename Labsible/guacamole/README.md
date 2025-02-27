# Apache Guacamole Setup Guide
This guide shows how to setup [Apache Guacamole](https://guacamole.apache.org/).  Apache Guacamole is a clientless remote desktop gateway. It supports standard protocols like VNC, RDP, and SSH.

This document describe the setup of guacamole on:
- [RHEL 9 physical machine, managed via ansible](#rhel-9-physical-machine-managed-via-ansible)

## Pre-requisites
### User requirement
Ensure that the user running the ansible playbook is created with sudo privileges.

### ansible setup in control node
Ensure tha ansible is setup on control node.  
To verify run:

```bash
ansible --version
```
If ansible is installed, you should see an output similar to this:
```bash
ansible [core 2.14.17]
  config file = /etc/ansible/ansible.cfg
  .
  .
  .
  jinja version = 3.1.2
  libyaml = True
```

If ansible is not installed, consult the appropriate documentations to set it up prior to proceeding.  

## RHEL 9 physical machine, managed via ansible

### Installing software
The following example playbook installs podman software on the machine:

```
- name: Install software
  hosts: localhost
  become: yes

  tasks:
  - name: Install podman
    package:
      name: podman
      state: present
```

We will be running guacamole in container via `podman-compose`.  

The following playbook snippet installs the `podman-compose` tool via `pip`.  

```
  - name: Install podman-compose python package
    pip:
      name: podman-compose
```

### compose.yml
`podman-compose` will start containers according to the definition in the `compose.yml` file.  

The following `compose.yml` will start the three services for our guacamole system.  

**The passwords are kept simple for demo purpose, be sure to use strong passwords, if you are deploying in production.**

```
services:
  mysql:
    image: docker.io/mysql:8.0
    container_name: mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: guacamole_db
      MYSQL_USER: guacamole
      MYSQL_PASSWORD: password
    volumes:
      - ./initdb.sql:/docker-entrypoint-initdb.d/initdb.sql:Z
      - guac-mysql-data:/var/lib/mysql
      - guac-schema:/tmp/schema
    networks:
      - guacamole-net

  guacd:
    image: docker.io/guacamole/guacd
    container_name: guacd
    restart: always
    ports:
      - "4822:4822"
    networks:
      - guacamole-net


  guacamole:
    image: docker.io/guacamole/guacamole
    container_name: guacamole
    restart: always
    ports:
      - "8080:8080"
    environment:
      GUACD_HOSTNAME: guacd
      MYSQL_HOSTNAME: mysql
      MYSQL_PORT: 3306
      MYSQL_DATABASE: guacamole_db
      MYSQL_USER: guacamole
      MYSQL_PASSWORD: password
    networks:
      - guacamole-net
    volumes:
      - guac-config:/config

networks:
  guacamole-net:
    driver: bridge
volumes:
  guac-mysql-data:
  guac-schema:
  guac-config:
```

Notice that there is a bind mount in the `compose.yml` file above:

```
    volumes:
      - ./initdb.sql:/docker-entrypoint-initdb.d/initdb.sql:Z
```

This SQL script file is used on container startup to initialize the MySQL database for authentication.  A sample of this script is provided [here](./initdb.sql)

`:Z` is required to take care of SELinux file context.  

An ansible playbook snippet to download this file is shown below:

```
  - name: Download SQL initialization file
    ansible.builtin.get_url:
      become: no
      url: https://raw.githubusercontent.com/ChaoChingTan/NoblePath/refs/heads/master/Labsible/guacamole/initdb.sql
      dest: ./initdb.sql
      mode: '0644'
```

### Start the guacamole services using podman-compose
With the previous steps complete, the necessary files and software will be available to start guacamole.

```bash
podman-compose up -d
```

### Automate further using ansible

We can automate the process of starting the containers by writing the ansible playbook.  

To create the `mysql` container and the required network, we can use the following playbook snippet.  The `generate_systemd` option creates the systemd files for the service.  

**The passwords are kept simple for demo purpose, be sure to use strong passwords, if you are deploying in production.**

```
  - name: Create a podman network
    containers.podman.podman_network:
      name: guacamole-net
      driver: bridge

  - name: Ensure MySQL container present and create systemd unit file
    containers.podman.podman_container:
      name: mysql
      image: docker.io/mysql:8.0
      state: stopped
      volume:
        -  ./initdb.sql:/docker-entrypoint-initdb.d/initdb.sql:Z
        - guac-mysql-data:/var/lib/mysql
        - guac-schema:/tmp/schema
      env:
        MYSQL_ROOT_PASSWORD: "password"
        MYSQL_DATABASE: "guacamole_db"
        MYSQL_USER: "guacamole"
        MYSQL_PASSWORD: "password"
      network:
        - guacamole-net
      generate_systemd:
        path: ~/.config/systemd/user/
        restart_policy: always
```

We can then start and enable the service.  
```
  - name: mysql container must be started and enabled on systemd
    ansible.builtin.systemd:
      name: container-mysql
      scope: user
      daemon_reload: true
      state: started
      enabled: true
```

Repeat the process for the `guacd` and `guacamole` services.

## Putting it together
This [playbook](guacamole.yml) automates the install of guacamole services using ansible. 

Run the playbook:

```bash
ansible-playbook guacamole.yml
```

Output:

```
[chao@xtra ~]$ ansible-playbook guacamole.yml 
[WARNING]: provided hosts list is empty, only localhost is available. Note that the implicit localhost does not
match 'all'

PLAY [Install Apache Guacamole on localhost] *******************************************************************

TASK [Gathering Facts] *****************************************************************************************
ok: [localhost]

TASK [Install podman] ******************************************************************************************
ok: [localhost]

TASK [Install podman-compose python package] *******************************************************************
ok: [localhost]

TASK [Download SQL initialization file] ************************************************************************
ok: [localhost]

TASK [Create a podman network] *********************************************************************************
ok: [localhost]

TASK [Ensure MySQL container present and create systemd unit file] *********************************************
changed: [localhost]

TASK [Ensure guacd container present and create systemd unit file] *********************************************
changed: [localhost]

TASK [Ensure guacamole container present and create systemd unit file] *****************************************
changed: [localhost]

TASK [mysql container must be started and enabled on systemd] **************************************************
changed: [localhost]

TASK [guacd container must be started and enabled on systemd] **************************************************
changed: [localhost]

TASK [guacamole container must be started and enabled on systemd] **********************************************
changed: [localhost]

PLAY RECAP *****************************************************************************************************
localhost                  : ok=11   changed=6    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```

You can then access the guacamole web frontend via port 8080.  The path is `/guacamole`, for example:  `http://127.0.0.1:8080/guacamole`


## Conclusion
In this guide, we have walked through an ansible playbook which automates and initial setup of Apache Guacamole.  

Hope you had fun.