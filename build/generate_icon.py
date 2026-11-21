from PIL import Image, ImageDraw
import os

def generate_icon(output_path="build/icon.ico"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Bunny Ears
    # Left Outer Ear
    draw.polygon([(65, 120), (50, 40), (75, 15), (95, 45), (100, 110)], fill="#FFB7B2", outline="#222228", width=6)
    # Left Inner Ear
    draw.polygon([(70, 110), (58, 45), (75, 25), (88, 48), (92, 105)], fill="#FFD1DC")

    # Right Outer Ear (Flopping slightly)
    draw.polygon([(155, 110), (160, 45), (180, 15), (205, 40), (190, 120)], fill="#FFB7B2", outline="#222228", width=6)
    # Right Inner Ear
    draw.polygon([(162, 105), (168, 48), (180, 25), (198, 45), (185, 110)], fill="#FFD1DC")

    # 2. Main Bunny Chubby Body
    padding_x = 32
    padding_y = 70
    draw.ellipse([padding_x, padding_y, size - padding_x, size - 20], fill="#FFB7B2", outline="#222228", width=7)

    # 3. Soft Cream Belly Patch
    draw.ellipse([65, 140, 191, 230], fill="#FFF9F2")

    # 4. Rosy Cheeks
    draw.ellipse([45, 150, 75, 172], fill="#FF9AA2")
    draw.ellipse([181, 150, 211, 172], fill="#FF9AA2")

    # 5. Whiskers
    draw.line([50, 158, 20, 154], fill="#222228", width=4)
    draw.line([50, 166, 22, 174], fill="#222228", width=4)
    draw.line([206, 158, 236, 154], fill="#222228", width=4)
    draw.line([206, 166, 234, 174], fill="#222228", width=4)

    # 6. Big Sparkly Anime Eyes
    # Left Eye
    draw.ellipse([76, 115, 108, 155], fill="#18181D")
    draw.ellipse([82, 120, 94, 132], fill="#FFFFFF")  # Big glint
    draw.ellipse([96, 142, 102, 148], fill="#FFFFFF")  # Baby glint

    # Right Eye
    draw.ellipse([148, 115, 180, 155], fill="#18181D")
    draw.ellipse([154, 120, 166, 132], fill="#FFFFFF")
    draw.ellipse([168, 142, 174, 148], fill="#FFFFFF")

    # 7. Bunny Nose & Split Mouth
    draw.polygon([(122, 155), (134, 155), (128, 162)], fill="#FF7597")
    draw.line([128, 162, 128, 168], fill="#222228", width=4)
    draw.arc([114, 162, 128, 176], start=0, end=180, fill="#222228", width=4)
    draw.arc([128, 162, 142, 176], start=0, end=180, fill="#222228", width=4)

    # Save as multi-size ICO
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(output_path, format="ICO", sizes=icon_sizes)
    print(f"Generated icon: {output_path}")

if __name__ == "__main__":
    generate_icon()
