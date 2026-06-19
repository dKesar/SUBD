from pathlib import Path

import cv2
import numpy as np
import psycopg2

from obshchee import otpechatok_kartinki, podkljuchenie, sozdat_tablicu

OBRAZTSY_DIR = Path("obraztsy")

MESTA = [
    ("Les",     (34, 139, 34),  "circles"),
    ("Pustynja", (60, 180, 230), "stripes"),
    ("Gorod",   (130, 130, 130), "grid"),
    ("More",    (180, 120, 40),  "waves"),
    ("Gory",    (110, 110, 130), "triangles"),
    ("Pole",    (90, 200, 200),  "dots"),
]


def sdelat_kartinku(color, pattern, seed):
    """Sozdat uznavaemuju kartinku 400x400 dlja konkretnogo mesta."""
    rng = np.random.default_rng(seed)
    img = np.full((400, 400, 3), color, dtype=np.uint8)
    if pattern == "circles":
        for _ in range(40):
            c = (int(rng.integers(0, 400)), int(rng.integers(0, 400)))
            cv2.circle(img, c, int(rng.integers(5, 30)), (20, 90, 20), -1)
    elif pattern == "stripes":
        for x in range(0, 400, 30):
            cv2.line(img, (x, 0), (x, 400), (40, 150, 200), 8)
    elif pattern == "grid":
        for p in range(0, 400, 40):
            cv2.line(img, (p, 0), (p, 400), (80, 80, 80), 3)
            cv2.line(img, (0, p), (400, p), (80, 80, 80), 3)
    elif pattern == "waves":
        for y in range(0, 400, 20):
            pts = np.array([[x, int(y + 10 * np.sin(x / 20))] for x in range(0, 400, 5)])
            cv2.polylines(img, [pts], False, (200, 140, 60), 3)
    elif pattern == "triangles":
        for _ in range(20):
            x, y = int(rng.integers(0, 350)), int(rng.integers(0, 350))
            pts = np.array([[x, y + 50], [x + 25, y], [x + 50, y + 50]])
            cv2.fillPoly(img, [pts], (140, 140, 160))
    elif pattern == "dots":
        for _ in range(200):
            c = (int(rng.integers(0, 400)), int(rng.integers(0, 400)))
            cv2.circle(img, c, 4, (60, 160, 160), -1)
    return img


def main() -> None:
    OBRAZTSY_DIR.mkdir(exist_ok=True)
    conn = podkljuchenie()
    sozdat_tablicu(conn)

    # Chistim tablicu, chtoby povtornyj zapusk ne plodil dubli.
    with conn.cursor() as cur:
        cur.execute("TRUNCATE mesta RESTART IDENTITY;")
    conn.commit()

    for i, (nazvanie, color, pattern) in enumerate(MESTA):
        img = sdelat_kartinku(color, pattern, seed=i)
        path = OBRAZTSY_DIR / f"{nazvanie}.png"
        cv2.imwrite(str(path), img)

        otp = otpechatok_kartinki(str(path))
        bajty = path.read_bytes()

        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO mesta (nazvanie, otpechatok, kartinka) "
                "VALUES (%s, %s, %s)",
                (nazvanie, otp, psycopg2.Binary(bajty)),
            )
        conn.commit()
        print(f"  + {nazvanie:9} ({len(bajty)} bajt)  -> {path}")

    conn.close()
    print(f"\nGotovo. V baze {len(MESTA)} mest. Kartinki lezhat v {OBRAZTSY_DIR}/")


if __name__ == "__main__":
    main()
# SELECT id, nazvanie, length(kartinka) AS bajt FROM mesta ORDER BY id;