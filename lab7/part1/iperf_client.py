import os
import subprocess


def client(server_ip, duration=10, port=5001):
    """
    Запускає iperf-клієнт у режимі TCP.

    Повертає:
        (stdout, error)

    error порожній, якщо команда завершилася успішно
    і не сформувала повідомлень у stderr.
    """
    command = [
        "iperf",
        "-c", server_ip,
        "-p", str(port),
        "-t", str(duration),
        "-i", "1",
    ]

    environment = os.environ.copy()
    environment["LC_ALL"] = "C"

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=environment,
        )
    except OSError as error:
        return "", f"Не вдалося запустити iperf: {error}"

    try:
        output, error = process.communicate(
            timeout=duration + 10
        )
    except subprocess.TimeoutExpired:
        process.kill()
        output, error = process.communicate()

        message = "Перевищено час очікування iperf."
        if error.strip():
            message += f" {error.strip()}"

        return output, message

    # Порожній stderr не гарантує успіх:
    # додатково перевіряємо код завершення процесу.
    if process.returncode != 0:
        message = error.strip() or output.strip()
        return output, (
            f"iperf завершився з кодом "
            f"{process.returncode}: {message}"
        )

    return output, error.strip()
