"""
Macros for EPL2 commands
"""
import qrcode
import math

def generate_qr_code(data, box_size=3, border=0):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image()

def get_pixels_as_bits(img):
    pixels = img.getdata()
    width, height = img.size
    width_bytes = math.ceil(width / 8) * 8
    for row in range(height):
        yield ''.join('1' if pixel else '0' for pixel in pixels[row*width : (row+1)*width]).ljust(width_bytes, '1')

def bits_to_bytes(bits):
    return bytes([int(bits[i:i+8], 2) for i in range(0, len(bits), 8)])

def qr(x, y, data, box_size=3, border=0):
    img = generate_qr_code(data, box_size, border)
    bits = '\n'.join(get_pixels_as_bits(img))
    bytes_ = bits_to_bytes(bits)

    result = f"GW{x},{y},{len(bytes_)},{img.size[1]}\n"
    result += bytes_.decode()
    result += '\n'

    return result.decode("ISO-8859-1")
