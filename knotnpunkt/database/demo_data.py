
from .material import KategorieSpezifisch, KategorieTypen


def seed_demo_data():
    S = KategorieTypen.create_new("S", "Seitenbahn")
    F = KategorieTypen.create_new("F", "Fensterbahn")
    E = KategorieTypen.create_new("E", "Erdbahn")
    D = KategorieTypen.create_new("D", "Dreiecksbahn")
    B = KategorieTypen.create_new("B", "Bodenplane")

    KategorieSpezifisch.create_new("E", "Einzel", S)
    KategorieSpezifisch.create_new("D", "Doppel", S)
    KategorieSpezifisch.create_new("E", "Einzel", F)
    KategorieSpezifisch.create_new("D", "Doppel", F)
    KategorieSpezifisch.create_new("E", "Einzel", E)
    KategorieSpezifisch.create_new("D", "Doppel", E)

    KategorieSpezifisch.create_new("O", "Ohne", D)
    KategorieSpezifisch.create_new("K", "Kurz", D)
    KategorieSpezifisch.create_new("M", "Mittel", D)
    KategorieSpezifisch.create_new("L", "Lang", D)

    KategorieSpezifisch.create_new("I", "Igel", B)
    KategorieSpezifisch.create_new("S", "Sudan", B)
    KategorieSpezifisch.create_new("J", "Jurte", B)
    KategorieSpezifisch.create_new("K", "Kohte", B)
    KategorieSpezifisch.create_new("P", "Pfusch", B)
