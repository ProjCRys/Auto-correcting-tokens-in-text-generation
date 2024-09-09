
import random
import tkinter as tk
from tkinter import scrolledtext
import time
import re
import threading
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MAX_ATTEMPTS = 100000
UPDATE_INTERVAL = 0.1

class SentenceGeneratorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Sentence Generator")
        master.geometry("800x400")

        # Create left frame for input
        left_frame = tk.Frame(master)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        input_label = tk.Label(left_frame, text="Target Text:")
        input_label.pack()

        self.input_area = scrolledtext.ScrolledText(left_frame, wrap=tk.NONE, width=40, height=20)
        self.input_area.pack(fill=tk.BOTH, expand=True)
        self.input_area.insert(tk.END, "The quick brown fox\n\tjumps over\n  the lazy dog!")

        # Create right frame for output and button
        right_frame = tk.Frame(master)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        output_label = tk.Label(right_frame, text="Generation Output:")
        output_label.pack()

        self.output_area = scrolledtext.ScrolledText(right_frame, wrap=tk.NONE, width=40, height=18)
        self.output_area.pack(fill=tk.BOTH, expand=True)

        self.start_button = tk.Button(right_frame, text="Start Generation", command=self.start_generation)
        self.start_button.pack(side=tk.BOTTOM, pady=10)

        self.running = False

        # Load transformer model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
        self.model = AutoModelForCausalLM.from_pretrained("gpt2")

    def start_generation(self):
        if self.running:
            return  # Avoid starting a new generation while one is already running

        self.output_area.delete('1.0', tk.END)
        target_text = self.input_area.get('1.0', tk.END).rstrip()
        self.target_tokens = self.tokenize(target_text)

        initial_tokens = [self.target_tokens[0]]
        self.running = True

        # Start the generation in a separate thread
        threading.Thread(target=self.iterative_generation, args=(initial_tokens, self.target_tokens)).start()

    def tokenize(self, text):
        return self.tokenizer.tokenize(text)

    def detokenize(self, tokens):
        return self.tokenizer.convert_tokens_to_string(tokens)

    def generate_next_token(self, current_tokens):
        input_ids = self.tokenizer.convert_tokens_to_ids(current_tokens)
        input_ids = torch.tensor([input_ids])
        with torch.no_grad():
            outputs = self.model(input_ids)
            next_token_logits = outputs.logits[0, -1, :]
            next_token_id = torch.argmax(next_token_logits).item()
        return self.tokenizer.convert_ids_to_tokens(next_token_id)

    def update_output(self, tokens):
        self.output_area.delete('1.0', tk.END)
        self.output_area.insert(tk.END, self.detokenize(tokens))
        self.output_area.yview_pickplace(tk.END)  # Scroll to the end
        self.master.update_idletasks()

    def iterative_generation(self, tokens, target):
        attempts = 0
        while tokens != target and attempts < MAX_ATTEMPTS:
            attempts += 1
            
            if len(tokens) < len(target):
                next_token = self.generate_next_token(tokens)
                tokens.append(next_token)
            
            for i in range(len(tokens)):
                if i < len(target) and tokens[i] != target[i]:
                    if random.random() < 0.5:  # 50% chance to update
                        tokens[i] = target[i]
            
            i = 0
            while i < len(tokens) - 1:
                if i + 1 < len(target) and tokens[i] == target[i] and tokens[i + 1] != target[i + 1]:
                    if random.random() < 0.5:  # 50% chance to insert the correct next token
                        tokens.insert(i + 1, target[i + 1])
                i += 1

            if len(tokens) > len(target):
                tokens = tokens[:len(target)]

            if attempts % int(UPDATE_INTERVAL * 10) == 0:  # Update every UPDATE_INTERVAL seconds
                self.update_output(tokens)
                time.sleep(UPDATE_INTERVAL)

        self.update_output(tokens)
        if tokens == target:
            self.output_area.insert(tk.END, "\nGeneration complete!")
        else:
            self.output_area.insert(tk.END, f"\nReached maximum attempts ({MAX_ATTEMPTS}).")

        self.running = False

root = tk.Tk()
gui = SentenceGeneratorGUI(root)
root.mainloop()
