import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import colorsys
import math


# =========================================================
# 1) Correspondance RYB <-> RGB pour la teinte
# =========================================================

RYB_TO_RGB_TABLE = [
    (0, 0),
    (15, 8),
    (30, 17),
    (45, 26),
    (60, 34),
    (75, 41),
    (90, 48),
    (105, 54),
    (120, 60),
    (135, 81),
    (150, 103),
    (165, 123),
    (180, 138),
    (195, 155),
    (210, 171),
    (225, 187),
    (240, 204),
    (255, 219),
    (270, 234),
    (285, 251),
    (300, 267),
    (315, 282),
    (330, 298),
    (345, 329),
    (360, 360),
]


def interpolate(value, table):
    value = value % 360
    for i in range(len(table) - 1):
        x0, y0 = table[i]
        x1, y1 = table[i + 1]
        if x0 <= value <= x1:
            if x1 == x0:
                return y0
            t = (value - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)
    return table[-1][1]


def invert_table(table):
    inv = [(y, x) for x, y in table]
    inv.sort(key=lambda p: p[0])
    return inv


RGB_TO_RYB_TABLE = invert_table(RYB_TO_RGB_TABLE)


# =========================================================
# 2) Conversions
# =========================================================

def hsv_deg_to_rgb(h_deg, s, v):
    h = (h_deg % 360) / 360
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (
        int(round(r * 255)),
        int(round(g * 255)),
        int(round(b * 255))
    )


def rgb_to_hsv_deg(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return h * 360, s, v


def rgb_to_hex(rgb):
    r, g, b = rgb
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


def ryb_hsv_to_rgb(h_ryb_deg, s, v):
    """
    Teinte choisie sur un cercle RYB, puis affichage RGB.
    On convertit la teinte RYB en teinte RGB avant d'utiliser HSV.
    """
    h_rgb_deg = interpolate(h_ryb_deg, RYB_TO_RGB_TABLE)
    return hsv_deg_to_rgb(h_rgb_deg, s, v)


def complementary_ryb_rgb(h_ryb_deg, s, v):
    """
    Complémentaire artistique :
    opposition de 180° sur le cercle RYB.
    """
    h_comp_ryb = (h_ryb_deg + 180) % 360
    return ryb_hsv_to_rgb(h_comp_ryb, s, v), h_comp_ryb


# =========================================================
# 3) Génération du cercle chromatique RYB
# =========================================================

def build_ryb_wheel(size=700, value=1.0):
    """
    Cercle chromatique artistique :
    - angle = teinte RYB
    - rayon = saturation
    - valeur = luminosité (fixée ici, gérée ensuite par slider)
    """
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, y)

    R = np.sqrt(X**2 + Y**2)
    Theta = np.arctan2(Y, X)

    img = np.ones((size, size, 3), dtype=float)

    inside = R <= 1
    h_ryb = (np.degrees(Theta) % 360)
    s = np.clip(R, 0, 1)

    for i in range(size):
        for j in range(size):
            if inside[i, j]:
                rgb = ryb_hsv_to_rgb(h_ryb[i, j], s[i, j], value)
                img[i, j] = np.array(rgb) / 255.0
            else:
                img[i, j] = [1, 1, 1]

    return img


# =========================================================
# 4) Affichage principal
# =========================================================

wheel_value_for_display = 1.0
wheel_img = build_ryb_wheel(size=500, value=wheel_value_for_display)

fig = plt.figure(figsize=(12, 7))

ax_wheel = fig.add_axes([0.05, 0.18, 0.42, 0.72])
ax_info = fig.add_axes([0.53, 0.18, 0.42, 0.72])
ax_slider_v = fig.add_axes([0.10, 0.07, 0.30, 0.03])
ax_slider_s = fig.add_axes([0.58, 0.07, 0.30, 0.03])

ax_wheel.imshow(wheel_img, extent=[-1, 1, -1, 1], origin="lower")
ax_wheel.set_title("Cercle chromatique artistique RYB\nClique pour choisir une couleur")
ax_wheel.set_aspect("equal")
ax_wheel.set_xticks([])
ax_wheel.set_yticks([])

marker, = ax_wheel.plot([], [], "ko", markersize=8, markerfacecolor="none", markeredgewidth=2)

ax_info.set_xlim(0, 1)
ax_info.set_ylim(0, 1)
ax_info.axis("off")

# Aperçus
preview_selected = np.ones((200, 200, 3))
preview_comp = np.ones((200, 200, 3))

img_selected = ax_info.imshow(preview_selected, extent=[0.05, 0.45, 0.50, 0.90], origin="lower")
img_comp = ax_info.imshow(preview_comp, extent=[0.55, 0.95, 0.50, 0.90], origin="lower")

ax_info.text(0.14, 0.93, "Couleur choisie", fontsize=11, weight="bold")
ax_info.text(0.60, 0.93, "Complémentaire RYB", fontsize=11, weight="bold")

info_text = ax_info.text(
    0.05, 0.42,
    "Clique dans le cercle,\npuis ajuste luminosité et saturation.",
    fontsize=11,
    va="top"
)

slider_v = Slider(ax_slider_v, "Luminosité (V)", 0.0, 1.0, valinit=1.0)
slider_s = Slider(ax_slider_s, "Saturation (S)", 0.0, 1.0, valinit=1.0)


# =========================================================
# 5) État courant
# =========================================================

selected_h_ryb = 0.0
selected_radius = 1.0
has_selection = False


# =========================================================
# 6) Mise à jour
# =========================================================

def update_display():
    global has_selection

    if not has_selection:
        return

    v = slider_v.val
    s_slider = slider_s.val

    # On combine :
    # - teinte : choisie par angle dans le cercle RYB
    # - saturation : pilotée par slider
    # - luminosité : pilotée par slider
    rgb_selected = ryb_hsv_to_rgb(selected_h_ryb, s_slider, v)
    rgb_comp, h_comp_ryb = complementary_ryb_rgb(selected_h_ryb, s_slider, v)

    # Mise à jour des aperçus
    patch1 = np.ones((200, 200, 3))
    patch1[:, :] = np.array(rgb_selected) / 255
    img_selected.set_data(patch1)

    patch2 = np.ones((200, 200, 3))
    patch2[:, :] = np.array(rgb_comp) / 255
    img_comp.set_data(patch2)

    # HSV côté affichage RGB
    h_rgb_sel, s_rgb_sel, v_rgb_sel = rgb_to_hsv_deg(*rgb_selected)
    h_rgb_comp, s_rgb_comp, v_rgb_comp = rgb_to_hsv_deg(*rgb_comp)

    info_text.set_text(
        f"--- Couleur choisie ---\n"
        f"Teinte RYB : {selected_h_ryb:.1f}°\n"
        f"RGB : {rgb_selected}\n"
        f"HEX : {rgb_to_hex(rgb_selected)}\n"
        f"HSV affiché : ({h_rgb_sel:.1f}°, {s_rgb_sel:.2f}, {v_rgb_sel:.2f})\n\n"
        f"--- Complémentaire artistique ---\n"
        f"Teinte RYB complémentaire : {h_comp_ryb:.1f}°\n"
        f"RGB : {rgb_comp}\n"
        f"HEX : {rgb_to_hex(rgb_comp)}\n"
        f"HSV affiché : ({h_rgb_comp:.1f}°, {s_rgb_comp:.2f}, {v_rgb_comp:.2f})"
    )

    fig.canvas.draw_idle()


def on_click(event):
    global selected_h_ryb, selected_radius, has_selection

    if event.inaxes != ax_wheel or event.xdata is None or event.ydata is None:
        return

    x = event.xdata
    y = event.ydata
    r = math.sqrt(x**2 + y**2)

    if r > 1:
        return

    theta = math.degrees(math.atan2(y, x)) % 360

    selected_h_ryb = theta
    selected_radius = r
    has_selection = True

    marker.set_data([x], [y])
    update_display()


slider_v.on_changed(lambda val: update_display())
slider_s.on_changed(lambda val: update_display())
fig.canvas.mpl_connect("button_press_event", on_click)

plt.show()