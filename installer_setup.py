# -*- coding: utf-8 -*-
"""
Shivansh Astro-Vastu Professional - 1-Click Setup & Installer
Creates Desktop & Start Menu shortcuts with official icon and launches software.
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

def create_windows_shortcut(target, shortcut_path, icon_path, description, work_dir):
    try:
        temp_dir = os.environ.get("TEMP", os.path.dirname(shortcut_path))
        vbs_path = os.path.join(temp_dir, f"_mk_sc_{os.getpid()}.vbs")
        vbs_content = (
            'Set ws = CreateObject("WScript.Shell")\r\n'
            f'Set s = ws.CreateShortcut("{shortcut_path}")\r\n'
            f's.TargetPath = "{target}"\r\n'
            f's.WorkingDirectory = "{work_dir}"\r\n'
            f's.IconLocation = "{icon_path},0"\r\n'
            f's.Description = "{description}"\r\n'
            's.Save\r\n'
        )
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_content)
        
        subprocess.run(["cscript", "//nologo", vbs_path], check=True, capture_output=True)
        if os.path.exists(vbs_path):
            os.remove(vbs_path)
        return os.path.exists(shortcut_path)
    except Exception:
        # Fallback to PowerShell
        ps_cmd = (
            f"$ws = New-Object -ComObject WScript.Shell; "
            f"$s = $ws.CreateShortcut('{shortcut_path}'); "
            f"$s.TargetPath = '{target}'; "
            f"$s.WorkingDirectory = '{work_dir}'; "
            f"$s.IconLocation = '{icon_path},0'; "
            f"$s.Description = '{description}'; "
            f"$s.Save()"
        )
        try:
            res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
                                 capture_output=True, text=True)
            return res.returncode == 0 and os.path.exists(shortcut_path)
        except Exception:
            return False

def install_app():
    base_dir = get_base_dir()
    exe_target = os.path.join(base_dir, "ShivanshAstroVastu.exe")
    if not os.path.exists(exe_target):
        parent_exe = os.path.join(os.path.dirname(base_dir), "ShivanshAstroVastu.exe")
        if os.path.exists(parent_exe):
            exe_target = parent_exe
            base_dir = os.path.dirname(base_dir)

    icon_path = os.path.join(base_dir, "app_icon.ico")
    if not os.path.exists(icon_path):
        icon_path = exe_target

    desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    desktop_shortcut = os.path.join(desktop_dir, "Shivansh Astro-Vastu Professional.lnk")

    appdata_programs = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs")
    start_shortcut = os.path.join(appdata_programs, "Shivansh Astro-Vastu Professional.lnk")

    s1 = create_windows_shortcut(
        target=exe_target,
        shortcut_path=desktop_shortcut,
        icon_path=icon_path,
        description="Shivansh Astro-Vastu Professional - CRM & Kundli Software",
        work_dir=base_dir
    )

    s2 = create_windows_shortcut(
        target=exe_target,
        shortcut_path=start_shortcut,
        icon_path=icon_path,
        description="Shivansh Astro-Vastu Professional - CRM & Kundli Software",
        work_dir=base_dir
    )

    return s1 or s2, exe_target, base_dir

def show_gui():
    root = tk.Tk()
    root.title("Shivansh Astro-Vastu Professional - Setup")
    root.geometry("540x450")
    root.resizable(False, False)
    root.configure(bg="#0c111d")

    # Center window
    root.eval('tk::PlaceWindow . center')

    # Brand Title
    lbl_title = tk.Label(
        root,
        text="शिवंश ॲस्ट्रो-वास्तू प्रोफेशनल",
        font=("Segoe UI", 18, "bold"),
        fg="#e0a943",
        bg="#0c111d"
    )
    lbl_title.pack(pady=(25, 5))

    lbl_sub = tk.Label(
        root,
        text="PC Edition — Setup & Installation Wizard",
        font=("Segoe UI", 11),
        fg="#94a3b8",
        bg="#0c111d"
    )
    lbl_sub.pack(pady=(0, 20))

    # Info frame
    info_frame = tk.Frame(root, bg="#161f30", bd=1, relief="solid")
    info_frame.pack(fill="x", padx=30, pady=10)

    desc_text = (
        "या सेटअपमुळे आपल्या कॉम्प्युटरच्या डेस्कटॉपवर आणि स्टार्ट मेनूमध्ये\n"
        "शिवंश ॲस्ट्रो-वास्तू सॉफ्टवेअरचा थेट शॉर्टकट आयकॉन तयार होईल.\n\n"
        "• 100% ऑफलाइन वैदिक व लाल किताब कुंडली इंजिन\n"
        "• 78-पानी व्हीआयपी मराठी पत्रिका निर्मिती\n"
        "• केपी 249 सब-डिव्हिजन आणि 4-लेव्हल सिग्निफिकेटर्स\n"
        "• 36-गुण अष्टकूट मिलन व संपूर्ण वास्तू शास्त्र रिपोर्ट"
    )
    lbl_desc = tk.Label(
        info_frame,
        text=desc_text,
        font=("Segoe UI", 10),
        fg="#f1f5f9",
        bg="#161f30",
        justify="left",
        padx=15,
        pady=15
    )
    lbl_desc.pack(anchor="w")

    # Credential Box
    cred_frame = tk.Frame(root, bg="#111c2e", bd=1, relief="ridge")
    cred_frame.pack(fill="x", padx=30, pady=5)
    cred_text = "लॉगिन माहिती:   वापरकर्ता (Username): Admin   |   पासवर्ड: Harman"
    lbl_cred = tk.Label(cred_frame, text=cred_text, font=("Segoe UI", 9, "bold"), fg="#fbbf24", bg="#111c2e", pady=8)
    lbl_cred.pack()

    status_var = tk.StringVar(value="")
    lbl_status = tk.Label(root, textvariable=status_var, font=("Segoe UI", 10, "bold"), fg="#10b981", bg="#0c111d")
    lbl_status.pack(pady=5)

    def on_install_and_launch():
        success, exe_target, base_dir = install_app()
        if success:
            status_var.set("डेस्कटॉप शॉर्टकट यशस्वीरित्या तयार झाला! सॉफ्टवेअर सुरू होत आहे...")
            root.update()
            if os.path.exists(exe_target):
                subprocess.Popen([exe_target], cwd=base_dir)
            root.after(1200, root.destroy)
        else:
            messagebox.showwarning("सूचना", "शॉर्टकट तयार करता आला नाही, तरी आपण थेट ShivanshAstroVastu.exe चालवू शकता.")
            if os.path.exists(exe_target):
                subprocess.Popen([exe_target], cwd=base_dir)
            root.destroy()

    def on_install_only():
        success, exe_target, base_dir = install_app()
        if success:
            messagebox.showinfo(
                "यशस्वी (Success)",
                "अभिनंदन! शिवंश ॲस्ट्रो-वास्तू सॉफ्टवेअरचा डेस्कटॉप आयकॉन यशस्वीरित्या तयार झाला आहे!\n\n"
                "आता आपण डेस्कटॉपवरील 'Shivansh Astro-Vastu Professional' आयकॉनवर डबल क्लिक करून सॉफ्टवेअर वापरू शकता.\n\n"
                "लॉगिन माहिती:\nUsername: Admin\nPassword: Harman"
            )
            root.destroy()
        else:
            messagebox.showwarning("सूचना", "शॉर्टकट तयार करता आला नाही, तरी आपण थेट ShivanshAstroVastu.exe चालवू शकता.")

    btn_frame = tk.Frame(root, bg="#0c111d")
    btn_frame.pack(pady=15)

    btn_launch = tk.Button(
        btn_frame,
        text="इन्स्टॉल करा आणि सुरू करा (Install & Launch)",
        font=("Segoe UI", 11, "bold"),
        bg="#e0a943",
        fg="#0b0f19",
        activebackground="#f59e0b",
        padx=15,
        pady=8,
        cursor="hand2",
        command=on_install_and_launch
    )
    btn_launch.pack(side="left", padx=10)

    btn_setup = tk.Button(
        btn_frame,
        text="केवळ शॉर्टकट बनवा",
        font=("Segoe UI", 10),
        bg="#1e293b",
        fg="#cbd5e1",
        activebackground="#334155",
        padx=12,
        pady=8,
        cursor="hand2",
        command=on_install_only
    )
    btn_setup.pack(side="left", padx=5)

    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--silent":
        success, exe_target, base_dir = install_app()
        print(f"Setup completed with status: {success}")
    else:
        show_gui()
