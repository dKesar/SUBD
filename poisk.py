import subprocess
import tempfile

import napolnit
from obshchee import otpechatok_kartinki, podkljuchenie, razlichie, sozdat_tablicu


def podgotovit_bazu() -> None:
    """Podgotovit bazu: sozdat tablicu i, esli ona pustaja, napolnit."""
    conn = podkljuchenie()
    sozdat_tablicu(conn)
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM mesta")
        skolko = cur.fetchone()[0]
    conn.close()
    if skolko == 0:
        print("Baza pustaja — napolnjaju kartinkami...")
        napolnit.main()


def vybrat_fajl() -> str | None:
    """Pokazat rodnoj dialog macOS dlja vybora PNG-fajla."""
    script = (
        'set f to choose file with prompt "Vyberite snimok mestnosti (PNG)" '
        'of type {"png", "public.png"}\n'
        'POSIX path of f'
    )
    result = subprocess.run(
        ["osascript", "-e", script], capture_output=True, text=True
    )
    if result.returncode != 0:
        return None  # polzovatel nazhal «Otmena»
    return result.stdout.strip()


def pokazat_okno(soobshhenie: str) -> None:
    """Pokazat okno s rezultatom."""
    subprocess.run(
        ["osascript", "-e",
         f'display dialog "{soobshhenie}" buttons {{"OK"}} default button "OK" '
         f'with title "Rezultat poiska"'],
    )


def najti_pohozhee(otpechatok_zaprosa: int):
    """Najti v baze kartinku s samym blizkim otpechatkom."""
    conn = podkljuchenie()
    with conn.cursor() as cur:
        cur.execute("SELECT id, nazvanie, otpechatok, kartinka FROM mesta")
        rows = cur.fetchall()
    conn.close()

    if not rows:
        return None

    # Schitaem rasstojanie do kazhdoj kartinki i sortiruem.
    scored = []
    for row_id, nazvanie, otp, kartinka in rows:
        dist = razlichie(otpechatok_zaprosa, otp)
        pohozhest = round((64 - dist) / 64 * 100)
        scored.append((dist, pohozhest, nazvanie, bytes(kartinka)))
    scored.sort(key=lambda r: r[0])      # menshe rasstojanie = bolshe pohozhe
    return scored


def main() -> None:
    podgotovit_bazu()

    path = vybrat_fajl()
    if not path:
        print("Fajl ne vybran.")
        return

    print(f"Vybran fajl: {path}")
    otp = otpechatok_kartinki(path)

    rezultaty = najti_pohozhee(otp)
    if rezultaty is None:
        pokazat_okno("Baza pustaja. Snachala zapustite napolnit.py")
        return

    # Luchshee sovpadenie — pervoe v otsortirovannom spiske.
    dist, pohozhest, nazvanie, bajty = rezultaty[0]

    # Pechataem tablicu vseh sovpadenij v terminal.
    print("\nPohozhest na mesta iz bazy:")
    print(f"  {'Mesto':10} {'Rasstojanie':>11} {'Pohozhest':>10}")
    for d, p, nm, _ in rezultaty:
        print(f"  {nm:10} {d:>11} {p:>9}%")

    # Pokazyvaem rezultat v okne.
    pokazat_okno(
        f"Blizhajshee mesto: {nazvanie}  —  pohozhest {pohozhest}%  "
        f"(razlichie {dist} iz 64 bitov)"
    )

    # Otkryvaem najdennuju kartinku (dostajom bajty iz bazy) v Prosmotre.
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.write(bajty)
    tmp.close()
    subprocess.run(["open", tmp.name])


if __name__ == "__main__":
    main()
