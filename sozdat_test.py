
from pathlib import Path

import cv2
import numpy as np

SRC = Path("obraztsy/Les.png")
OUT = Path("proverka/pohozhij_les.png")


def main() -> None:
    img = cv2.imread(str(SRC))
    if img is None:
        raise SystemExit("Snachala zapustite napolnit.py — net Les.png")

    # 1. Chut povyshaem jarkost.
    img = cv2.convertScaleAbs(img, alpha=1.0, beta=25)
    # 2. Ljogkoe razmytie (kak budto foto nechjotkoe).
    img = cv2.GaussianBlur(img, (5, 5), 0)
    # 3. Dobavljaem neskolko novyh tjomnyh pjaten (derevev).
    rng = np.random.default_rng(123)
    for _ in range(15):
        c = (int(rng.integers(0, 400)), int(rng.integers(0, 400)))
        cv2.circle(img, c, int(rng.integers(8, 20)), (15, 70, 15), -1)

    OUT.parent.mkdir(exist_ok=True)
    cv2.imwrite(str(OUT), img)
    print(f"Gotovo: {OUT}")


if __name__ == "__main__":
    main()
