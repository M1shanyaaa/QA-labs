import re


NUMBER = r"\d+(?:\.\d+)?"

PATTERN = re.compile(
    rf"^\s*\[\s*\d+\]\s+"
    rf"(?P<start>{NUMBER})\s*-\s*"
    rf"(?P<end>{NUMBER})\s+sec\s+"
    rf"(?P<transfer>{NUMBER})\s+"
    rf"(?P<transfer_unit>[KMGT]?Bytes)\s+"
    rf"(?P<bitrate>{NUMBER})\s+"
    rf"(?P<bitrate_unit>[KMGT]?bits/sec)"
)

BYTE_FACTORS = {
    "Bytes": 1,
    "KBytes": 1024,
    "MBytes": 1024 ** 2,
    "GBytes": 1024 ** 3,
    "TBytes": 1024 ** 4,
}

BIT_FACTORS = {
    "bits/sec": 1,
    "Kbits/sec": 1000,
    "Mbits/sec": 1000 ** 2,
    "Gbits/sec": 1000 ** 3,
    "Tbits/sec": 1000 ** 4,
}


def parser(output_text):
    """
    Повертає список записів iperf.

    Transfer — Мбайт (1 Мбайт = 10^6 байтів).
    Bitrate — Мбіт/с.
    """
    results = []

    for line in output_text.splitlines():
        match = PATTERN.search(line)

        if not match:
            continue

        data = match.groupdict()

        transfer = (
            float(data["transfer"])
            * BYTE_FACTORS[data["transfer_unit"]]
            / 1_000_000
        )

        bitrate = (
            float(data["bitrate"])
            * BIT_FACTORS[data["bitrate_unit"]]
            / 1_000_000
        )

        results.append({
            "Interval": f'{data["start"]}-{data["end"]}',
            "Transfer": transfer,
            "Bitrate": bitrate,
        })

    return results
