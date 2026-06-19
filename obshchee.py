
import cv2
import numpy as np
import psycopg2

# Podkljuchenie k baze PostgreSQL (Postgres.app slushaet soket v /tmp).
DB_DSN = "dbname=mestnost host=/tmp"


def podkljuchenie():
    return psycopg2.connect(DB_DSN)


def sozdat_tablicu(conn) -> None:

    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS mesta (
                id         SERIAL PRIMARY KEY,
                nazvanie   TEXT   NOT NULL,
                otpechatok BIGINT NOT NULL,
                kartinka   BYTEA  NOT NULL
            );
            """
        )
    conn.commit()


def otpechatok_kartinki(put_k_fajlu: str) -> int:
    img = cv2.imread(put_k_fajlu, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Ne udalos otkryt kartinku: {put_k_fajlu}")
    small = cv2.resize(img, (8, 8), interpolation=cv2.INTER_AREA)
    avg = small.mean()
    bits = (small > avg).flatten()
    value = 0
    for bit in bits:
        value = (value << 1) | int(bit)
    # PostgreSQL BIGINT znakovyj, poetomu sdvigaem diapazon v otricatelnuju zonu.
    return value - (1 << 63)


def razlichie(otp_a: int, otp_b: int) -> int:

    return bin((otp_a ^ otp_b) & ((1 << 64) - 1)).count("1")
