import argparse

from iperf_client import client
from traffic_parser import parser


def check_traffic(
    server_ip,
    min_transfer=2.0,
    min_bitrate=20.0,
):
    output, error = client(server_ip)

    print("=== Початковий вивід iperf ===")
    print(output)

    if error:
        print(f"FAILED: {error}")
        return False

    parsed_data = parser(output)

    # Для тесту тривалістю 10 секунд з -i 1
    # залишаємо інтервали приблизно по одній секунді.
    # Підсумок 0-10 секунд та короткий залишковий
    # інтервал не використовуємо.
    intervals = []

    for item in parsed_data:
        start, end = map(
            float, item["Interval"].split("-")
        )

        if 0.9 <= end - start <= 1.1:
            intervals.append(item)

    # Не дозволяємо тесту пройти через порожній
    # або неповний результат парсингу.
    if len(intervals) != 10:
        print(
            "FAILED: очікувалося 10 щосекундних "
            f"інтервалів, отримано {len(intervals)}."
        )
        return False

    print(
        "=== Інтервали, для яких "
        f"Transfer > {min_transfer} Мбайт та "
        f"Bitrate > {min_bitrate} Мбіт/с ==="
    )

    failed = []

    for item in intervals:
        if (
            item["Transfer"] > min_transfer
            and item["Bitrate"] > min_bitrate
        ):
            print(item)
        else:
            failed.append(item)

    if failed:
        for item in failed:
            print(
                f"FAILED: інтервал {item['Interval']}; "
                f"Transfer={item['Transfer']:.3f} Мбайт; "
                f"Bitrate={item['Bitrate']:.3f} Мбіт/с."
            )

        return False

    print("PASSED: усі 10 інтервалів відповідають вимогам.")
    return True


def main():
    arguments = argparse.ArgumentParser()

    arguments.add_argument(
        "--server", default="127.0.0.1"
    )
    arguments.add_argument(
        "--min-transfer", type=float, default=2.0
    )
    arguments.add_argument(
        "--min-bitrate", type=float, default=20.0
    )

    args = arguments.parse_args()

    success = check_traffic(
        server_ip=args.server,
        min_transfer=args.min_transfer,
        min_bitrate=args.min_bitrate,
    )

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
