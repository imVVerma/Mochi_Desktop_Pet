import os
from PIL import Image, ImageDraw

def create_mochi_icon(size: int) -> Image.Image:
    """Generates high-res Mochi bunny icon with soft squircle background."""
    base_size = 512
    img = Image.new("RGBA", (base_size, base_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 0. Soft Pastel Lavender/Peach Circular Background
    bg_padding = 16
    draw.ellipse(
        [bg_padding, bg_padding, base_size - bg_padding, base_size - bg_padding],
        fill="#FFF0F3",
        outline="#FFCCD5",
        width=12
    )

    # Scale factor from 256 coords
    scale = (base_size - 100) / 256.0
    offset_x = 50
    offset_y = 65

    def s(coord):
        return (coord[0] * scale + offset_x, coord[1] * scale + offset_y)

    def s_pts(pts):
        return [s(p) for p in pts]

    def s_box(box):
        p1 = s((box[0], box[1]))
        p2 = s((box[2], box[3]))
        return [p1[0], p1[1], p2[0], p2[1]]

    # 1. Bunny Ears
    # Left Outer Ear
    draw.polygon(s_pts([(65, 120), (50, 40), (75, 15), (95, 45), (100, 110)]), fill="#FFB7B2", outline="#222228", width=int(6 * scale))
    # Left Inner Ear
    draw.polygon(s_pts([(70, 110), (58, 45), (75, 25), (88, 48), (92, 105)]), fill="#FFD1DC")

    # Right Outer Ear (Flopping slightly)
    draw.polygon(s_pts([(155, 110), (160, 45), (180, 15), (205, 40), (190, 120)]), fill="#FFB7B2", outline="#222228", width=int(6 * scale))
    # Right Inner Ear
    draw.polygon(s_pts([(162, 105), (168, 48), (180, 25), (198, 45), (185, 110)]), fill="#FFD1DC")

    # 2. Main Bunny Chubby Body
    draw.ellipse(s_box([32, 70, 256 - 32, 236]), fill="#FFB7B2", outline="#222228", width=int(7 * scale))

    # 3. Soft Cream Belly Patch
    draw.ellipse(s_box([65, 140, 191, 230]), fill="#FFF9F2")

    # 4. Rosy Cheeks
    draw.ellipse(s_box([45, 150, 75, 172]), fill="#FF9AA2")
    draw.ellipse(s_box([181, 150, 211, 172]), fill="#FF9AA2")

    # 5. Whiskers
    w1 = s((50, 158)); w2 = s((20, 154))
    draw.line([w1, w2], fill="#222228", width=int(4 * scale))
    w3 = s((50, 166)); w4 = s((22, 174))
    draw.line([w3, w4], fill="#222228", width=int(4 * scale))

    w5 = s((206, 158)); w6 = s((236, 154))
    draw.line([w5, w6], fill="#222228", width=int(4 * scale))
    w7 = s((206, 166)); w8 = s((234, 174))
    draw.line([w7, w8], fill="#222228", width=int(4 * scale))

    # 6. Big Sparkly Anime Eyes
    # Left Eye
    draw.ellipse(s_box([76, 115, 108, 155]), fill="#18181D")
    draw.ellipse(s_box([82, 120, 94, 132]), fill="#FFFFFF")  # Big glint
    draw.ellipse(s_box([96, 142, 102, 148]), fill="#FFFFFF")  # Baby glint

    # Right Eye
    draw.ellipse(s_box([148, 115, 180, 155]), fill="#18181D")
    draw.ellipse(s_box([154, 120, 166, 132]), fill="#FFFFFF")
    draw.ellipse(s_box([168, 142, 174, 148]), fill="#FFFFFF")

    # 7. Bunny Nose & Split Mouth
    draw.polygon(s_pts([(122, 155), (134, 155), (128, 162)]), fill="#FF7597")
    m1 = s((128, 162)); m2 = s((128, 168))
    draw.line([m1, m2], fill="#222228", width=int(4 * scale))

    arc1 = s_box([114, 162, 128, 176])
    arc2 = s_box([128, 162, 142, 176])
    draw.arc(arc1, start=0, end=180, fill="#222228", width=int(4 * scale))
    draw.arc(arc2, start=0, end=180, fill="#222228", width=int(4 * scale))

    # Resize with high-quality Lanczos resampling
    if size != base_size:
        return img.resize((size, size), Image.Resampling.LANCZOS)
    return img

def export_android_icons():
    res_dir = "mobile/flutter_companion/android/app/src/main/res"
    densities = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192,
    }

    for folder, px in densities.items():
        out_dir = os.path.join(res_dir, folder)
        os.makedirs(out_dir, exist_ok=True)
        icon_img = create_mochi_icon(px)
        out_file = os.path.join(out_dir, "ic_launcher.png")
        icon_img.save(out_file, format="PNG")
        print(f"Generated {out_file} ({px}x{px})")

if __name__ == "__main__":
    export_android_icons()
