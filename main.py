import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class IMEICheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("IMEI Checker")
        self.imei_process_thread = None

        # Frame for buttons and progress
        self.frame = ttk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        self.choose_file_button = ttk.Button(self.frame, text="Choose IMEI File", command=self.load_file)
        self.choose_file_button.pack(side=tk.LEFT, padx=5)

        self.start_button = ttk.Button(self.frame, text="Start", command=self.start_process, state=tk.DISABLED)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.end_button = ttk.Button(self.frame, text="End", command=self.end_process, state=tk.DISABLED)
        self.end_button.pack(side=tk.LEFT, padx=5)
        self.save_button = ttk.Button(self.frame, text="Save As", command=self.save_output, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)

        # Progress bar and percentage label
        self.progress_frame = ttk.Frame(self.root)
        self.progress_frame.pack(padx=10, pady=5)
        self.progress = ttk.Progressbar(self.progress_frame, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(side=tk.LEFT)
        self.progress_label = ttk.Label(self.progress_frame, text="0%")
        self.progress_label.pack(side=tk.LEFT, padx=5)

        self.output_text = tk.Text(self.root, height=15, width=50)
        self.output_text.pack(padx=10, pady=10)

        self.file_path = ''

    def load_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.start_button['state'] = tk.NORMAL
            self.output_text.delete('1.0', tk.END)

    def start_process(self):
        if self.file_path:
            self.progress["value"] = 0
            self.progress_label["text"] = "0%"
            self.imei_process_thread = threading.Thread(target=self.process_file, args=(self.file_path,), daemon=True)
            self.imei_process_thread.start()
            self.end_button['state'] = tk.NORMAL
            self.save_button['state'] = tk.NORMAL
            self.start_button['state'] = tk.DISABLED

    def end_process(self):
        # This function is intended to stop the process.
        # Implementing a safe stop might require more complex thread management.
        # A simple way to "stop" is to disable further actions or close the application.
        messagebox.showwarning("End Process", "The process will be terminated.")
        self.root.destroy()  # This will close the application.

    def process_file(self, file_path):
        with open(file_path, 'r') as file:
            imeis = file.readlines()
            total = len(imeis)
            for i, imei in enumerate(imeis, start=1):
                imei = imei.strip()
                if imei:
                    try:
                        result = self.check_imei(imei)
                        self.append_output(f"Result for IMEI {imei}: {result}\n")
                    except Exception as e:
                        self.append_output(f"Error checking IMEI {imei}: {e}\n")
                progress_percent = (i / total) * 100
                self.progress["value"] = progress_percent
                self.progress_label["text"] = f"{progress_percent:.2f}%"
                self.root.update_idletasks()
            messagebox.showinfo("Completion", "All IMEI checks are completed.")
            self.start_button['state'] = tk.DISABLED
            self.end_button['state'] = tk.DISABLED

    def check_imei(self, imei_number):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service, options=chrome_options)
        browser.get('http://imei.sy')



        imei_input = browser.find_element(By.ID, 'imei')
        submit_button = browser.find_element(By.CSS_SELECTOR, 'button.searchbtn')

        imei_input.clear()
        imei_input.send_keys(imei_number)
        submit_button.click()
        time.sleep(5)

        result = browser.find_element(By.ID, 'sts').text
        browser.quit()
        return result

    def append_output(self, text):
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)

    def save_output(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.output_text.get("1.0", tk.END))
            messagebox.showinfo("Save As", "Output saved successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = IMEICheckerGUI(root)
    root.mainloop()
