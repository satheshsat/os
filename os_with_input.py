import os
import subprocess
import shutil

# Notice the 'r' before the quotes to make it a raw string
asm_code = r"""
[BITS 16]
[ORG 0x7C00]

start:
    ; --- 1. Get Input Loop ---
.input_loop:
    mov ah, 0x00      ; BIOS keyboard function: wait for keypress
    int 0x16          ; Wait for key. ASCII character is returned in AL

    cmp al, 0x0D      ; Check if the pressed key is 'Enter' (Carriage Return)
    je .respond       ; If it is Enter, break the loop and respond

    mov ah, 0x0E      ; BIOS teletype function: print character
    int 0x10          ; Echo the typed character to the screen
    jmp .input_loop   ; Loop back to wait for the next key

    ; --- 2. Respond ---
.respond:
    mov ah, 0x0E
    mov al, 0x0D      ; Print Carriage Return (\r)
    int 0x10
    mov al, 0x0A      ; Print Line Feed (\n)
    int 0x10

    mov si, msg       ; Load address of our message
.print_char:
    lodsb             ; Load next byte from SI into AL
    or al, al         ; Check if the character is null (0)
    jz halt           ; If null, jump to halt
    mov ah, 0x0E      ; BIOS teletype output function
    int 0x10          ; Print character
    jmp .print_char   ; Loop to the next character

halt:
    cli               ; Clear interrupts
    hlt               ; Halt the CPU

msg db 'Hello World!', 0

; Pad the rest of the 512-byte boot sector with zeroes
times 510-($-$$) db 0
dw 0xAA55             ; Boot signature required by BIOS
"""

print("Writing boot.asm...")
with open("boot.asm", "w") as f:
    f.write(asm_code)

# 2. Compile assembly into a raw binary using NASM
print("Compiling assembly to binary...")
subprocess.run(["nasm", "-f", "bin", "boot.asm", "-o", "boot.bin"], check=True)

# 3. Create an ISO directory structure and pad binary to a 1.44MB floppy image
print("Padding boot sector to 1.44MB floppy size...")
os.makedirs("iso_root", exist_ok=True)

with open("boot.bin", "rb") as f:
    boot_sector = f.read()

floppy_image = boot_sector + b'\x00' * (1474560 - len(boot_sector))
with open("iso_root/os.img", "wb") as f:
    f.write(floppy_image)

# 4. Generate the bootable ISO using xorriso
print("Generating custom_os.iso...")
subprocess.run([
    "xorriso", "-as", "mkisofs",
    "-b", "os.img",          
    "-o", "custom_os.iso",   
    "iso_root/"              
], check=True)

# 5. Clean up temporary build files
print("Cleaning up build files...")
os.remove("boot.asm")
os.remove("boot.bin")
shutil.rmtree("iso_root")

print("\nSuccess! custom_os.iso is ready for VirtualBox. Type anything and press Enter to see the response.")