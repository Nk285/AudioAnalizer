import os

import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import pygame
import pydub
from pydub import AudioSegment

import threading

# from audioprocessor import improve_audio, convert_and_transcribe, whisper_to_texts
# from textprocessor import classify_text


class AudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Processing App")

        self.root.geometry("800x600")  # Set initial size

        self.load_screen()

        self.file_path = None
        self.enhanced_audio_path = None

        self.create_widgets()

        pygame.mixer.init()
        self.is_paused = False

    def load_screen(self):
        load_label = tk.Label(self.root, text="Loading models, please wait...")
        load_label.pack(pady=20)

        self.root.update()

        from audioprocessor import improve_audio, convert_and_transcribe, whisper_to_texts
        from textprocessor import classify_text

        self.improve_audio = improve_audio
        self.transcribe = convert_and_transcribe
        self.whisper_to_texts = whisper_to_texts
        self.classify_text = classify_text

        load_label.destroy()

    def create_widgets(self):
        self.select_button = tk.Button(self.root, text="Select Audio File", command=self.select_file)
        self.select_button.pack(pady=10)

        self.process_button = tk.Button(self.root, text="Process Audio", command=self.process_audio, state=tk.DISABLED)
        self.process_button.pack(pady=10)

        # Create a frame to hold the play, pause, and restart buttons horizontally
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=10)

        self.play_button = tk.Button(self.control_frame, text="Play", command=self.play_audio, state=tk.DISABLED)
        self.play_button.grid(row=0, column=0, padx=5)

        self.pause_button = tk.Button(self.control_frame, text="Pause", command=self.pause_audio, state=tk.DISABLED)
        self.pause_button.grid(row=0, column=1, padx=5)

        self.restart_button = tk.Button(self.control_frame, text="Restart", command=self.stop_audio,
                                        state=tk.DISABLED)
        self.restart_button.grid(row=0, column=2, padx=5)

        self.transcript_label = tk.Label(self.root, text="Transcription:")
        self.transcript_label.pack(pady=10)

        self.transcript_text = scrolledtext.ScrolledText(self.root, width=60, height=20)
        self.transcript_text.pack(pady=10, expand=True, fill='both')

        self.result_label = tk.Label(self.root, text="", font=("Helvetica", 12))
        self.result_label.pack(pady=10)

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
        if self.file_path:
            self.process_button.config(state=tk.NORMAL)

    def process_audio(self):
        if not self.file_path:
            messagebox.showerror("Error", "No file selected")
            return

        threading.Thread(target=self.dummy_audio_processing).start()

    def dummy_audio_processing(self):
        self.process_button.config(state=tk.DISABLED)
        self.play_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.DISABLED)
        self.transcript_text.delete(1.0, tk.END)
        self.transcript_text.insert(tk.END, "Processing audio, please wait...\n")
        self.result_label.config(text="", fg="green")

        path_parts = self.file_path.split("/")
        pre, _ = os.path.splitext(path_parts[-1])
        path_parts[-1] = "better_" + pre + ".wav"
        self.enhanced_audio_path = "/".join(path_parts)

        audio = AudioSegment.from_file(self.file_path)
        audio = self.improve_audio(audio, True, self.enhanced_audio_path)
        audio.export(self.enhanced_audio_path, format="wav")

        _, texts = self.whisper_to_texts(self.transcribe(self.file_path, False))
        text = "\n\n".join(texts)
        self.transcript_text.delete(1.0, tk.END)
        self.transcript_text.insert(tk.END, text)

        violation_detected = self.classify_text(text)
        self.update_result_label(violation_detected)

        self.process_button.config(state=tk.NORMAL)
        self.play_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.NORMAL)
        self.restart_button.config(state=tk.NORMAL)

    def update_result_label(self, violation_detected):
        if violation_detected:
            self.result_label.config(text="Обнаружены нарушения регламента", fg="red")
        else:
            self.result_label.config(text="Нарушений регламента не обнаружено", fg="green")

    def play_audio(self):
        if self.enhanced_audio_path:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
            else:
                pygame.mixer.music.load(self.enhanced_audio_path)
                pygame.mixer.music.play()

    def pause_audio(self):
        if not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
        else:
            pygame.mixer.music.unpause()
            self.is_paused = False

    def stop_audio(self):
        pygame.mixer.music.stop()
        self.is_paused = False


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioApp(root)
    root.mainloop()