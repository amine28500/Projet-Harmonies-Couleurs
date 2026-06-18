import math
import colorsys


def gaussian(lmbda, mu, sigma, amplitude=1.0):
    return amplitude * math.exp(-0.5 * ((lmbda - mu) / sigma) ** 2)


def wavelength_to_xyz(wavelength):
    if wavelength < 380 or wavelength > 780:
        return 0.0, 0.0, 0.0

    X = (
        gaussian(wavelength, 595.8, 33.33, 1.056)
        + gaussian(wavelength, 446.8, 19.44, 0.362)
    )

    Y = (
        gaussian(wavelength, 556.3, 28.75, 0.821)
        + gaussian(wavelength, 449.8, 19.44, 0.286)
    )

    Z = gaussian(wavelength, 449.8, 19.44, 1.217)

    return X, Y, Z


def xyz_to_srgb(X, Y, Z):
    r_lin =  3.2406 * X - 1.5372 * Y - 0.4986 * Z
    g_lin = -0.9689 * X + 1.8758 * Y + 0.0415 * Z
    b_lin =  0.0557 * X - 0.2040 * Y + 1.0570 * Z

    r_lin = max(0.0, r_lin)
    g_lin = max(0.0, g_lin)
    b_lin = max(0.0, b_lin)

    def gamma_correct(c):
        if c <= 0.0031308:
            return 12.92 * c
        return 1.055 * (c ** (1 / 2.4)) - 0.055

    r = gamma_correct(r_lin)
    g = gamma_correct(g_lin)
    b = gamma_correct(b_lin)

    max_rgb = max(r, g, b)
    if max_rgb > 1:
        r /= max_rgb
        g /= max_rgb
        b /= max_rgb

    return (
        int(round(r * 255)),
        int(round(g * 255)),
        int(round(b * 255))
    )


def rgb_to_hex(r, g, b):
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


def rgb_to_hsv(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return h * 360, s * 100, v * 100


def rgb_to_cmyk(r, g, b):
    if (r, g, b) == (0, 0, 0):
        return 0, 0, 0, 100

    r_n = r / 255
    g_n = g / 255
    b_n = b / 255

    k = 1 - max(r_n, g_n, b_n)
    c = (1 - r_n - k) / (1 - k)
    m = (1 - g_n - k) / (1 - k)
    y = (1 - b_n - k) / (1 - k)

    return c * 100, m * 100, y * 100, k * 100


def xyz_to_lab(X, Y, Z):
    """
    Conversion XYZ -> CIE Lab.
    Référence : blanc D65.
    """

    Xn = 0.95047
    Yn = 1.00000
    Zn = 1.08883

    x = X / Xn
    y = Y / Yn
    z = Z / Zn

    def f(t):
        delta = 6 / 29
        if t > delta ** 3:
            return t ** (1 / 3)
        return t / (3 * delta ** 2) + 4 / 29

    fx = f(x)
    fy = f(y)
    fz = f(z)

    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)

    return L, a, b


def main():
    try:
        wavelength = float(input("Entre une longueur d'onde en nm : ").replace(",", "."))

        X, Y, Z = wavelength_to_xyz(wavelength)

        if X == 0 and Y == 0 and Z == 0:
            print("Longueur d’onde hors du visible approximatif : 380 à 780 nm.")
            return

        r, g, b = xyz_to_srgb(X, Y, Z)

        hsv = rgb_to_hsv(r, g, b)
        hexa = rgb_to_hex(r, g, b)
        cmyk = rgb_to_cmyk(r, g, b)
        lab = xyz_to_lab(X, Y, Z)

        print("\n--- Résultats ---")
        print(f"Longueur d'onde : {wavelength:.1f} nm")
        print(f"XYZ : ({X:.4f}, {Y:.4f}, {Z:.4f})")
        print(f"RGB : ({r}, {g}, {b})")
        print(f"HEX : {hexa}")
        print(f"HSV : ({hsv[0]:.1f}°, {hsv[1]:.1f}%, {hsv[2]:.1f}%)")
        print(f"CMYK : ({cmyk[0]:.1f}%, {cmyk[1]:.1f}%, {cmyk[2]:.1f}%, {cmyk[3]:.1f}%)")
        print(f"Lab : (L={lab[0]:.2f}, a={lab[1]:.2f}, b={lab[2]:.2f})")

    except ValueError:
        print("Erreur : entre une valeur numérique valide.")


if __name__ == "__main__":
    main()