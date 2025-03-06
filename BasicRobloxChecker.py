import requests
import time
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# GUI Class
class UsernameCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Roblox Username Checker")
        self.root.geometry("500x450")

        # Select File Button
        self.file_label = tk.Label(root, text="Select a file with usernames:")
        self.file_label.pack(pady=5)
        
        self.file_button = tk.Button(root, text="Browse", command=self.select_file)
        self.file_button.pack(pady=5)

        # Display Selected File
        self.file_path = tk.StringVar()
        self.file_display = tk.Label(root, textvariable=self.file_path, fg="blue")
        self.file_display.pack()

        # Start & Stop Buttons
        self.start_button = tk.Button(root, text="Start Checking", command=self.start_checking, state=tk.DISABLED)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop Checking", command=self.stop_checking, state=tk.DISABLED, bg="red", fg="white")
        self.stop_button.pack(pady=5)

        # Progress Bar
        self.progress = ttk.Progressbar(root, length=300, mode="determinate")
        self.progress.pack(pady=10)

        # Output Text Box
        self.output_box = tk.Text(root, height=10, width=50)
        self.output_box.pack()

        # Safe Exit Flag
        self.safe_exit = False

    def select_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filename:
            self.file_path.set(filename)
            self.start_button.config(state=tk.NORMAL)  # Enable start button

    def check_username(self, username):
        url = f"https://auth.roblox.com/v1/usernames/validate?Username={username}&Birthday=2000-01-01"
        try:
            response = requests.get(url, timeout=10)
            response_data = response.json()

            code = response_data.get("code")
            if code == 0:
                self.output_box.insert(tk.END, f"✅ VALID: {username}\n")
                return username  
            elif code == 1:
                self.output_box.insert(tk.END, f"❌ TAKEN: {username}\n")
            elif code == 2:
                self.output_box.insert(tk.END, f"🚫 CENSORED: {username}\n")
            else:
                self.output_box.insert(tk.END, f"⚠️ ERROR ({code}): {username}\n")
        except requests.exceptions.RequestException as e:
            self.output_box.insert(tk.END, f"⚠️ Network Error: {e}\n")

    def get_unique_filename(self, base_name):
        counter = 1
        new_filename = base_name
        while os.path.exists(new_filename):
            new_filename = f"available_usernames_{counter}.txt"
            counter += 1
        return new_filename

    def start_checking(self):
        file = self.file_path.get()
        if not os.path.exists(file):
            messagebox.showerror("Error", "File not found!")
            return

        with open(file, "r") as f:
            usernames = f.read().splitlines()

        if not usernames:
            messagebox.showerror("Error", "File is empty!")
            return

        self.output_box.delete(1.0, tk.END)  # Clear output box
        self.progress["maximum"] = len(usernames)  # Set progress bar max
        self.progress["value"] = 0
        self.safe_exit = False  # Reset the stop flag

        self.start_button.config(state=tk.DISABLED)  # Disable start button
        self.stop_button.config(state=tk.NORMAL)  # Enable stop button

        output_file = self.get_unique_filename("available_usernames.txt")
        available_usernames = []

        def run_check():
            for username in usernames:
                if self.safe_exit:
                    break  
                result = self.check_username(username)
                if result:
                    available_usernames.append(result)

                self.progress["value"] += 1  # Update progress bar
                self.root.update_idletasks()
                time.sleep(0.01)  # Prevent rate-limiting

            with open(output_file, "w") as f:
                f.write("\n".join(available_usernames) + "\n")

            messagebox.showinfo("Done", f"Finished! Available usernames saved to '{output_file}'")

            # Re-enable the start button
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

        # Run in a separate thread so GUI doesn't freeze
        threading.Thread(target=run_check).start()

    def stop_checking(self):
        self.safe_exit = True
        self.output_box.insert(tk.END, "🛑 Stopping process...\n")
        self.stop_button.config(state=tk.DISABLED)

# Run GUI
root = tk.Tk()
app = UsernameCheckerApp(root)
root.mainloop()
