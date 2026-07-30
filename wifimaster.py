import subprocess
import os
import json

CONNECTION_PATH = "/etc/NetworkManager/system-connections/"
BACKUP_FILE = "wifi_profiles_backup.json"

def scan_wifi_detailed():
    print("="*65)
    print("   DEEP WI-FI SCANNER (2.4GHz & 5GHz BAND DETECTION)")
    print("="*65)
    print("[*] Scanning nearby networks with full details...")
    
    try:
        # Rescan to get fresh surrounding networks
        subprocess.run(['nmcli', 'device', 'wifi', 'rescan'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Get detailed network metrics
        output = subprocess.check_output(['nmcli', '-t', '-f', 'SSID,BSSID,CHAN,FREQ,SIGNAL,SECURITY', 'dev', 'wifi']).decode('utf-8')
        
        networks = []
        seen_ssids = set()
        
        for line in output.strip().split('\n'):
            if line:
                parts = line.split(':')
                if len(parts) >= 6:
                    ssid = parts[0].strip()
                    bssid = parts[1].strip()
                    chan = parts[2].strip()
                    freq = parts[3].strip()
                    signal = parts[4].strip()
                    security = parts[5].strip()
                    
                    if ssid and ssid not in seen_ssids:
                        seen_ssids.add(ssid)
                        
                        # Determine Wi-Fi Band (2.4 GHz or 5 GHz) based on Frequency
                        band = "Unknown"
                        try:
                            freq_val = int(freq.split()[0])
                            if 2400 <= freq_val <= 2500:
                                band = "2.4 GHz"
                            elif 5000 <= freq_val <= 5850:
                                band = "5 GHz"
                        except:
                            pass
                        
                        networks.append({
                            "SSID": ssid,
                            "BSSID": bssid,
                            "Channel": chan,
                            "Frequency": freq,
                            "Band": band,
                            "Signal": signal,
                            "Security": security if security else "Open / Free"
                        })
        
        print(f"\n[+] Found {len(networks)} Unique Wi-Fi Networks:\n")
        for idx, net in enumerate(networks, 1):
            print(f"{idx}. SSID: {net['SSID']}")
            print(f"   -> Band / Frequency: {net['Band']} ({net['Frequency']} | Channel {net['Channel']})")
            print(f"   -> Signal Strength: {net['Signal']}% | Security: {net['Security']}")
            print(f"   -> BSSID (MAC Address): {net['BSSID']}")
            print("-" * 55)
            
    except Exception as e:
        print(f"[-] Error during scanning: {e}")

def backup_profiles():
    print("\n[*] Backing up saved Wi-Fi profiles (including secure passwords)...")
    if not os.path.exists(CONNECTION_PATH):
        print("[-] Error: NetworkManager path not accessible. Run with sudo!")
        return
        
    try:
        files = os.listdir(CONNECTION_PATH)
        backup_data = {}
        
        for f in files:
            file_path = os.path.join(CONNECTION_PATH, f)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r') as file_obj:
                        backup_data[f] = file_obj.read()
                except Exception as ex:
                    print(f"[-] Skipping file {f} due to permission error.")
                    
        # Save into a JSON backup file
        with open(BACKUP_FILE, 'w') as bf:
            json.dump(backup_data, bf, indent=4)
            
        print(f"[+] SUCCESS! {len(backup_data)} Wi-Fi configurations successfully backed up to '{BACKUP_FILE}'.")
        print("[*] TIP: Copy this 'wifi_profiles_backup.json' file to a USB flash drive before reinstalling Windows/Linux!")
        
    except Exception as e:
        print(f"[-] Backup failed: {e}")

def restore_profiles():
    print("\n[*] Restoring Wi-Fi profiles and passwords from backup file...")
    if not os.path.exists(BACKUP_FILE):
        print(f"[-] Error: Backup file '{BACKUP_FILE}' not found in current directory!")
        return
        
    try:
        with open(BACKUP_FILE, 'r') as bf:
            backup_data = json.load(bf)
            
        for filename, content in backup_data.items():
            dest_path = os.path.join(CONNECTION_PATH, filename)
            with open(dest_path, 'w') as dest_file:
                dest_file.write(content)
            # Setting strict permissions required by Linux NetworkManager
            os.chmod(dest_path, 0o600)
            
        # Reload NetworkManager to instantly apply restored networks
        subprocess.run(['sudo', 'nmcli', 'connection', 'reload'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[+] SUCCESS! Restored {len(backup_data)} Wi-Fi profiles. All passwords and network settings are back!")
        
    except Exception as e:
        print(f"[-] Restore failed: {e}")

def main():
    while True:
        print("\n" + "="*50)
        print("   ADVANCED WI-FI BACKUP & SCANNER TOOL")
        print("="*50)
        print("1. Deep Scan Wi-Fi (2.4GHz/5GHz & Full Details)")
        print("2. Backup Wi-Fi Profiles & Passwords (Before Fresh OS)")
        print("3. Restore Wi-Fi Profiles & Passwords (After Fresh OS)")
        print("4. Exit")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == '1':
            scan_wifi_detailed()
        elif choice == '2':
            backup_profiles()
        elif choice == '3':
            restore_profiles()
        elif choice == '4':
            print("[*] Exiting program. Goodbye!")
            break
        else:
            print("[-] Invalid choice! Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()
