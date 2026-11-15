import getpass
import subprocess
import time

import paramiko
import pytest


SERVER_IP = "127.0.0.1"
USERNAME = "mishanya"
PORT = 5002


@pytest.fixture(scope="function")
def server():
    """Запускає iperf-сервер через SSH."""
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())

    password = getpass.getpass("Пароль SSH: ")

    pid = None
    stdout = None

    try:
        ssh.connect(
            hostname=SERVER_IP,
            username=USERNAME,
            password=password,
            look_for_keys=False,
            allow_agent=False,
            timeout=10,
        )

        # exec зберігає PID процесу після запуску iperf.
        _, stdout, stderr = ssh.exec_command(
            f"echo $$; exec iperf -s -B {SERVER_IP} -p {PORT}"
        )

        pid_text = stdout.readline().strip()

        if not pid_text.isdigit():
            pytest.fail("Не вдалося отримати PID сервера.")

        pid = int(pid_text)
        time.sleep(1)

        if stdout.channel.exit_status_ready():
            error = stderr.read().decode(errors="replace")
            pytest.fail(f"Сервер не запустився: {error}")

        print(f"\nСервер запущено, PID={pid}")

        yield SERVER_IP, PORT

    finally:
        try:
            if (
                pid is not None
                and stdout is not None
                and not stdout.channel.exit_status_ready()
            ):
                _, stop_out, _ = ssh.exec_command(
                    f"kill -TERM {pid}"
                )
                stop_out.channel.recv_exit_status()
                print("\nСервер зупинено.")
        finally:
            ssh.close()
            print("SSH-з'єднання закрито.")


@pytest.fixture(scope="function")
def client(server):
    """Генерує TCP-трафік і повертає вивід та помилку."""
    host, port = server

    process = subprocess.Popen(
        [
            "iperf",
            "-c", host,
            "-p", str(port),
            "-t", "10",
            "-i", "1",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        output, error = process.communicate(timeout=20)
    except subprocess.TimeoutExpired:
        process.kill()
        output, error = process.communicate()
        return output, "Перевищено час очікування iperf."

    if process.returncode != 0:
        error = (
            error.strip()
            or f"Код завершення iperf: {process.returncode}"
        )

    return output, error.strip()
