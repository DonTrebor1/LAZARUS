# LAZARUS
```
██╗      █████╗ ███████╗ █████╗ ██████╗ ██╗   ██╗███████╗
██║     ██╔══██╗╚════██║██╔══██╗██╔══██╗██║   ██║██╔════╝
██║     ███████║    ██╔╝███████║██████╔╝██║   ██║███████╗
██║     ██╔══██║   ██╔╝ ██╔══██║██╔══██╗██║   ██║╚════██║
███████╗██║  ██║   ██║  ██║  ██║██║  ██║╚██████╔╝███████║
╚══════╝╚═╝  ╚═╝   ╚═╝  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
```

**AD Attack Chain Automation · DonTrebor1**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Kali%20%7C%20Parrot-red)
![Use](https://img.shields.io/badge/Use-Authorized%20labs%20only-yellow)

> Solo para entornos controlados y autorizados: HackTheBox, TryHackMe, VulnHub y labs propios.

---

## ¿Qué es LAZARUS?

LAZARUS automatiza la cadena completa de ataque sobre Active Directory en entornos de práctica. Su output está diseñado para que de un vistazo sepas exactamente qué está pasando: los comandos aparecen en cajas diferenciadas, los hallazgos importantes se resaltan en verde, y los vectores de escalada de privilegios en rojo.

### Lo que diferencia a LAZARUS

| Característica | LAZARUS |
|---|---|
| Output visual claro (cajas, colores, separadores) | ✅ |
| Findings resaltados vs. output de comandos | ✅ |
| Vectores de escalada destacados visualmente | ✅ |
| BadSuccessor / dMSA (CVE-2025-26647) | ✅ |
| ADCS ESC1-8 con certipy | ✅ |
| ACL analysis (WriteDacl, GenericAll, GenericWrite) | ✅ |
| Pass-the-Hash nativo | ✅ |
| Estado persistente entre sesiones | ✅ |
| OPSEC labels por fase | ✅ |

---

## Requisitos

```bash
# Python 3.10+
python3 --version

# Herramientas externas (Kali/Parrot)
sudo apt install nmap netexec impacket-scripts evil-winrm hashcat bloodhound-python certipy-ad
```

---

## Uso

### Cadena completa automática
```bash
python3 lazarus.py -t 10.10.11.x -d corp.local --auto
```

### Con credenciales ya conocidas
```bash
python3 lazarus.py -t 10.10.11.x -d corp.local --creds 'jsmith:Password123' --auto
```

### Pass-the-Hash
```bash
python3 lazarus.py -t 10.10.11.x -d corp.local --hash 'administrator:8846f7eaee8fb117ad06bdd830b7586c' --auto
```

### Con lista de usuarios
```bash
python3 lazarus.py -t 10.10.11.x -d corp.local --users users.txt --auto
```

### Ver plan de ataque sin ejecutar nada
```bash
python3 lazarus.py -t 10.10.11.x -d corp.local --plan
```

### Reanudar sesión anterior
```bash
python3 lazarus.py --resume lazarus_output/lazarus_state.json
```

### Re-analizar vectores de escalada sobre sesión existente
```bash
python3 lazarus.py --resume lazarus_output/lazarus_state.json --reanalyze
```

---

## Fases de ataque

| # | Fase | Herramientas | OPSEC |
|---|---|---|---|
| 1 | Reconocimiento | nmap | MEDIUM |
| 2 | Enumeración de usuarios | netexec RID brute, LDAP anónimo | MEDIUM |
| 3 | AS-REP Roasting | impacket-GetNPUsers | MEDIUM |
| 4 | Kerberoasting | impacket-GetUserSPNs | MEDIUM |
| 5 | Cracking | hashcat (18200/13100) | LOW |
| 6 | Validación de credenciales | netexec smb/winrm | MEDIUM |
| 7 | Post-enum | netexec, BloodHound, certipy, dacledit, dMSA | LOW-HIGH |
| 8 | Análisis y escalada | Mapa priv/grupos/ADCS/ACL | — |

---

## Output

```
lazarus_output/
├── lazarus_state.json      # Estado completo (resume con --resume)
├── nmap.txt                # Escaneo nmap
├── enum_users.txt          # Enumeración de usuarios
├── users.txt               # Lista de usuarios del dominio
├── asrep.txt               # AS-REP Roasting
├── asrep_hashes.txt        # Hashes AS-REP
├── asrep.pot               # Potfile hashcat
├── kerberoast.txt          # Kerberoasting
├── kerb_hashes.txt         # Hashes Kerberoast
├── kerb.pot                # Potfile hashcat
├── validate.txt            # Validación de credenciales
├── post_enum.txt           # Post-acceso
├── smb_shares.txt          # Shares SMB
├── bloodhound/             # Datos BloodHound
├── adcs.txt                # ADCS ESC1-8
├── dmsa.txt                # BadSuccessor/dMSA
└── acl.txt                 # ACLs peligrosas
```

---

## Aviso legal

Este software es exclusivamente para uso en entornos de práctica controlados y autorizados (HackTheBox, TryHackMe, VulnHub, laboratorios propios). El uso contra sistemas sin autorización explícita es ilegal.

---

## Autor

**DonTrebor1** · Offensive Security · ISO/IEC 27001:2022 LA · ISO/IEC 42001:2023 LA

[![HackTheBox](https://img.shields.io/badge/HackTheBox-whynotplay1-9fef00?logo=hackthebox)](https://app.hackthebox.com/profile/whynotplay1)
