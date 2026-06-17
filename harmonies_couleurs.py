from PIL import Image, ImageDraw, ImageFont
import colorsys

def get_harmonies(r, g, b):
    # Conversion RGB (0-255) vers HLS (0-1) comme vu en cours
    h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)

    def hls_to_rgb255(h_val, l_val, s_val):
        # Utilise le modulo 1.0 pour rester sur le cercle chromatique
        rgb = colorsys.hls_to_rgb(h_val % 1.0, l_val, s_val)
        return (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))

    # Application des formules d'harmonies
    return {
        "MONOCHROMATIQUE": [
            hls_to_rgb255(h, l, s), 
            hls_to_rgb255(h, min(1, l*1.3), s*0.8), 
            hls_to_rgb255(h, l*0.7, s)
        ],
        "ANALOGUE": [
            hls_to_rgb255(h - 0.08, l, s), # -30 degrés approx
            hls_to_rgb255(h, l, s), 
            hls_to_rgb255(h + 0.08, l, s)  # +30 degrés approx
        ],
        "COMPLÉMENTAIRE": [
            hls_to_rgb255(h, l, s), 
            hls_to_rgb255(h + 0.5, l, s)    # +180 degrés (exact opposé)
        ],
        "TRIADIQUE": [
            hls_to_rgb255(h, l, s), 
            hls_to_rgb255(h + 0.33, l, s), # +120 degrés
            hls_to_rgb255(h + 0.66, l, s)  # +240 degrés
        ]
    }

def generate_color_harmonies():
    # --- DEMANDE DES VALEURS À L'UTILISATEUR ---
    print("--- Configuration de la couleur de base BestPractice ---")
    try:
        r = int(input("Entrez la valeur Rouge (0-255) : "))
        g = int(input("Entrez la valeur Vert (0-255) : "))
        b = int(input("Entrez la valeur Bleu (0-255) : "))
        
        if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
            print("Erreur : Les valeurs doivent être entre 0 et 255.")
            return
    except ValueError:
        print("Erreur : Veuillez entrer des nombres entiers.")
        return

    # Calcul des harmonies
    user_color = (r, g, b)
    harmonies = get_harmonies(r, g, b)

    # Configuration de l'image (hauteur augmentée pour la couleur de départ)
    width, height = 800, 750
    canvas = Image.new('RGB', (width, height), '#F5F5F5')
    draw = ImageDraw.Draw(canvas)
    
    circle_radius = 40
    
    # 1. DESSINER LA COULEUR DONNÉE PAR L'UTILISATEUR
    draw.text((50, 40), "VOTRE COULEUR DE DÉPART :", fill="black")
    draw.ellipse([250, 20, 250 + circle_radius*2, 20 + circle_radius*2], fill=user_color, outline="black")
    draw.text((250, 105), f"RGB{user_color}", fill="black")

    # Ligne de séparation
    draw.line((50, 140, 750, 140), fill="grey")

    # 2. DESSINER LES HARMONIES RÉSULTANTES
    y_offset = 180
    for title, colors in harmonies.items():
        draw.text((50, y_offset + 20), title, fill="black")
        
        x_offset = 250
        for color in colors:
            coords = [x_offset, y_offset, x_offset + circle_radius*2, y_offset + circle_radius*2]
            draw.ellipse(coords, fill=color, outline="black")
            draw.text((x_offset, y_offset + 85), f"RGB{color}", fill="grey")
            x_offset += 120
            
        y_offset += 130

    # Sauvegarde et affichage
    canvas.save("mes_harmonies_completes.png")
    canvas.show()
    print(f"\nSuccès ! L'image 'mes_harmonies_completes.png' a été générée.")

if __name__ == "__main__":
    generate_color_harmonies()