import os
import sys
import math
from PIL import Image
import numpy as np



def embed(image_path, output_path, message):
    print(f"\n[DEBUG] Wywołano embed()")
    print(f"  Wejście: {image_path}")
    print(f"  Wyjście: {output_path}")
    print(f"  Wiadomość: {message}")


    bit_stream = []
    for char in message:
        bits_string = format(ord(char), '08b') 
        for bit in bits_string:
            bit_stream.append(int(bit))
            
    # Load image
    img = Image.open(image_path).convert('RGB')
    pixels = np.array(img)
    original_shape = pixels.shape 
    flat_pixels = pixels.flatten()
    
    if len(bit_stream) > len(flat_pixels):
        print("Błąd: Wiadomość jest za długa!")
        return

    # change LSB
    for i in range(len(bit_stream)):
        flat_pixels[i] = (flat_pixels[i] & 0xFE) | bit_stream[i]
        
    # reshape and save
    new_pixels = flat_pixels.reshape(original_shape)
    stego_img = Image.fromarray(new_pixels.astype('uint8'), 'RGB')
    stego_img.save(output_path, format="PNG")
    print(f"Wiadomość została ukryta w pliku: {output_path}")

def extract(stego_path, message_length):
    print(f"\n[DEBUG] Wywołano extract()")
    print(f"  Plik stego: {stego_path}")
    print(f"  Długość: {message_length} znaków")
    
    # 
    img = Image.open(stego_path).convert('RGB')
    flat_pixels = np.array(img).flatten()
    
    total_bits = message_length * 8
    if total_bits > len(flat_pixels):
        print("Błąd: Żądana długość wiadomości jest większa niż rozmiar obrazu!")
        return None

    # Extract bits
    extracted_bits = []
    for i in range(total_bits):
        bit = flat_pixels[i] & 1
        extracted_bits.append(str(bit))

    message = ""
    for i in range(0, len(extracted_bits), 8):
        byte_string = "".join(extracted_bits[i:i+8])
        character = chr(int(byte_string, 2))
        message += character
        
    print(f"\n[SUKCES] Odczytana wiadomość: {message}")
    return message

def calculate_psnr(cover_path, stego_path):
    # LOAD PNG
    img1 = Image.open(cover_path).convert('RGB')
    img2 = Image.open(stego_path).convert('RGB')
    
    p1 = np.array(img1).astype(np.float64)
    p2 = np.array(img2).astype(np.float64)
    
    #Calculate MSE
    mse = np.mean((p1 - p2) ** 2)
    if mse == 0:
        print("Obrazy są identyczne! PSNR = Nieskończoność (inf)")
        return float('inf')
        
    #Calculate PSNR
    max_pixel = 255.0
    psnr = 20 * math.log10(max_pixel / math.sqrt(mse))
    
    print(f"\n--- WYNIK PORÓWNANIA WIZUALNEGO ---")
    print(f"Błąd średniokwadratowy (MSE): {mse:.6f}")
    print(f"Metryka PSNR: {psnr:.2f} dB")
    return psnr

def test_jpeg(stego_png_path, original_message):
    print("\n--- URUCHAMIANIE EKSPERYMENTU JPEG ---")
    
    orig_bits = []
    for char in original_message:
        for bit in format(ord(char), '08b'):
            orig_bits.append(int(bit))
            
    qualities = [95, 90, 75, 50, 25]
    msg_len = len(original_message)
    
    print(f"{'Jakość JPEG':<12} | {'Poprawne bity (%)':<18} | {'Czy tekst czytelny?'}")
    print("-" * 55)
    
    for q in qualities:
        temp_jpg = f"tmp_stego_q{q}.jpg"

        img = Image.open(stego_png_path)
        img.save(temp_jpg, "JPEG", quality=q)
        
        img_jpg = Image.open(temp_jpg).convert('RGB')
        flat_jpg = np.array(img_jpg).flatten()
        
        extracted_bits = []
        for i in range(msg_len * 8):
            extracted_bits.append(flat_jpg[i] & 1)
            
        correct_count = 0
        for b_orig, b_ext in zip(orig_bits, extracted_bits):
            if b_orig == b_ext:
                correct_count += 1
                
        accuracy = (correct_count / len(orig_bits)) * 100
        
        decoded_chars = []
        for i in range(0, len(extracted_bits), 8):
            byte_chunk = extracted_bits[i:i+8]
            byte_str = "".join(str(b) for b in byte_chunk)
            decoded_chars.append(chr(int(byte_str, 2)))
        decoded_msg = "".join(decoded_chars)
        
        status = "TAK" if decoded_msg == original_message else "NIE (szum)"
        print(f"{q:<12} | {accuracy:.2f}%{'' : <11} | {status}")
        
        if os.path.exists(temp_jpg):
            os.remove(temp_jpg)

def main():
    # EMBED
    # python stego.py embed cover.png stego.png "TajnyTekst"
    # EXTRACT
    # python stego.py extract stego.png 10
    
    if len(sys.argv) < 2:
        print("Sposób użycia:")
        print("  python stego.py embed cover.png stego.png \"Wiadomość\"")
        print("  python stego.py extract stego.png długość_wiadomości")
        sys.exit(1) 

    tryb = sys.argv[1] 

    if tryb == "embed":
        if len(sys.argv) < 5:
            print("Błąd: Za mało argumentów dla trybu embed!")
            sys.exit(1)
            
        img_in = sys.argv[2]
        img_out = sys.argv[3]
        msg = sys.argv[4]
        embed(img_in, img_out, msg)

    elif tryb == "extract":
        if len(sys.argv) < 4:
            print("Błąd: Za mało argumentów dla trybu extract!")
            sys.exit(1)
            
        img_stego = sys.argv[2]
        try:
            length = int(sys.argv[3]) 
            extract(img_stego, length)
        except ValueError:
            print("Błąd: Długość wiadomości musi być liczbą całkowitą!")
            sys.exit(1)
    
    elif tryb == "psnr":
        if len(sys.argv) < 4:
            print("Błąd: Za mało argumentów!")
            print("Użycie: python stego.py psnr <cover.png> <stego.png>")
            sys.exit(1)
        calculate_psnr(sys.argv[2], sys.argv[3])
    
    elif tryb == "jpeg_test":
        if len(sys.argv) < 4:
            print("Błąd: Za mało argumentów!")
            print("Użycie: python stego.py jpeg_test <stego.png> \"<oryginalna_wiadomosc>\"")
            sys.exit(1)
        test_jpeg(sys.argv[2], sys.argv[3])

    else:
        print(f"Błąd: Nieznany tryb '{tryb}'. Użyj 'embed' lub 'extract'.")
        sys.exit(1)

if __name__ == "__main__":
    main()