#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import paramiko
from scp import SCPClient

from dotenv import load_dotenv


def deploy():
    load_dotenv()

    server = os.getenv("SSH_HOST")
    user = os.getenv("SSH_USERNAME")
    password = os.getenv("SSH_PASSWORD")
    port = os.getenv("WEB_SERVER_PORT")
    remote_dir = "ha-broker-dashboard"

    project_root = Path(__file__).parent
    items_to_copy = [
        "ha_broker_dashboard",
        "test",
        "deploy.sh",
        "pyproject.toml",
        "uv.lock",
        "config.yaml",
        "Dockerfile",
    ]

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f"Connected to {user}@{server}...")

    try:
        ssh.connect(server, username=user, password=password)
        ssh.exec_command(f"mkdir -p ~/{remote_dir}")

        print(f"Copying files to ~/{remote_dir}...")
        with SCPClient(ssh.get_transport()) as scp:
            for item in items_to_copy:
                local_path = project_root / item
                if local_path.exists():
                    print(f"  Copying {item}...")
                    if local_path.is_dir():
                        scp.put(str(local_path), remote_path=f"~/{remote_dir}/", recursive=True)
                    else:
                        scp.put(str(local_path), remote_path=f"~/{remote_dir}/")
                else:
                    print(f"  Warning: {item} not found, skipping...")

        print("Files copied. Running deploy script...")

        stdin, stdout, stderr = ssh.exec_command(
            f"cd ~/{remote_dir} && echo '{password}' | sudo -S bash deploy.sh {port}",
            get_pty=True
        )

        for line in stdout:
            print(line.strip())

        exit_status = stdout.channel.recv_exit_status()

        if exit_status == 0:
            print("\nDeployment complete!")
        else:
            print(f"\nDeployment failed with exit code {exit_status}")
            for line in stderr:
                print(line.strip())
            sys.exit(1)

    except paramiko.AuthenticationException:
        print("Error: Authentication failed. Check your password.")
        sys.exit(1)
    except paramiko.SSHException as e:
        print(f"Error: SSH connection failed: {e}")
        sys.exit(1)
    finally:
        ssh.close()


if __name__ == "__main__":
    deploy()
