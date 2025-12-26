from PIL import Image

def convert_to_transparent(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    datas = img.getdata()
    
    # The background in the logo is very dark but not pure black
    # Let's target anything dark enough
    new_data = []
    for item in datas:
        # If the pixel is very dark (r,g,b < 40)
        if item[0] < 45 and item[1] < 45 and item[2] < 45:
            new_data.append((0, 0, 0, 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    img.save(output_path, "PNG")
    print(f"Created {output_path}")

if __name__ == "__main__":
    convert_to_transparent("Logo Face.jpg", "logo_transparent.png")
