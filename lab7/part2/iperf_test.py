from parser import parser


MAX_SPREAD_PERCENT = -1.0


def test_tcp_uniformity(client):
    output, error = client

    print("\n=== Результати iperf ===")
    print(output)

    assert not error, f"Помилка клієнта: {error}"

    parsed_data = parser(output)
    assert parsed_data, "Не отримано даних для аналізу."

    intervals = []

    for item in parsed_data:
        start, end = map(
            float, item["Interval"].split("-")
        )

        if 0.9 <= end - start <= 1.1:
            intervals.append(item)

    assert len(intervals) == 10, (
        f"Очікувалося 10 інтервалів, отримано {len(intervals)}."
    )

    for item in intervals:
        assert item["Transfer"] > 2.0, (
            f"Інтервал {item['Interval']}: "
            f"Transfer={item['Transfer']:.3f} Мбайт, "
            "очікується > 2 Мбайт."
        )

        assert item["Bitrate"] > 20.0, (
            f"Інтервал {item['Interval']}: "
            f"Bitrate={item['Bitrate']:.3f} Мбіт/с, "
            "очікується > 20 Мбіт/с."
        )

    bitrates = [item["Bitrate"] for item in intervals]

    min_bitrate = min(bitrates)
    max_bitrate = max(bitrates)

    spread = (
        (max_bitrate - min_bitrate)
        / max_bitrate
        * 100
    )

    print(f"Мінімальна швидкість: {min_bitrate:.3f} Мбіт/с")
    print(f"Максимальна швидкість: {max_bitrate:.3f} Мбіт/с")
    print(f"Розкид швидкості: {spread:.2f}%")

    assert spread <= MAX_SPREAD_PERCENT, (
        f"Розкид {spread:.2f}% перевищує "
        f"допустимі {MAX_SPREAD_PERCENT}%."
    )
