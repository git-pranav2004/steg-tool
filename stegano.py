from PIL import Image

DELIM = '0000000011111110'

def _text_to_bits(text):
    return ''.join(f'{ord(c):08b}' for c in text) + DELIM

def _bits_to_text(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join(chr(int(b, 2)) for b in chars)

def embed_message(in_path, out_path, msg):
    img = Image.open(in_path)
    img = img.convert('RGB')
    pixels = img.load()
    bits = _text_to_bits(msg)
    w, h = img.size

    if len(bits) > w * h * 3:
        raise ValueError("Message too long for image")

    bit_idx = 0
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            rgb = [r, g, b]
            for i in range(3):
                if bit_idx < len(bits):
                    rgb[i] = (rgb[i] & ~1) | int(bits[bit_idx])
                    bit_idx += 1
            pixels[x, y] = tuple(rgb)
            if bit_idx >= len(bits):
                img.save(out_path)
                return

def extract_message(img_path):
    img = Image.open(img_path)
    img = img.convert('RGB')
    pixels = img.load()

    bits = ''
    for y in range(img.height):
        for x in range(img.width):
            for val in pixels[x, y]:
                bits += str(val & 1)
                if bits.endswith(DELIM):
                    return _bits_to_text(bits[:-len(DELIM)])
    raise ValueError("No hidden message found")