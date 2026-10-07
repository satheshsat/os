import os
import subprocess
import shutil

# 1. Write the raw x86 Assembly code
asm_code = """
[BITS 16]
[ORG 0x7C00]

start:
    mov si, msg
    mov ah, 0x0E      ; BIOS teletype output function

.print_char:
    lodsb             ; Load next byte from SI into AL
    or al, al         ; Check if the character is null (0)
    jz halt           ; If null, jump to halt
    int 0x10          ; Call BIOS interrupt to print character
    jmp .print_char   ; Loop to the next character

halt:
    cli               ; Clear interrupts
    hlt               ; Halt the CPU

msg db 'Hello World! Built from Python.', 0

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
# (VirtualBox El Torito emulation requires standard floppy sizing)
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
    "-b", "os.img",          # Specify the boot image
    "-o", "custom_os.iso",   # Output file
    "iso_root/"              # Directory to pack
], check=True)

# 5. Clean up temporary build files
print("Cleaning up build files...")
os.remove("boot.asm")
os.remove("boot.bin")
shutil.rmtree("iso_root")

print("\nSuccess! custom_os.iso is ready for VirtualBox.")