"""
MCP Clipboard - Collect LLM JSON responses
"""
import tkinter as tk
from tkinter import scrolledtext, filedialog, simpledialog
import pyperclip
import json
import os
import webbrowser

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False

class MCPClipboard:
    def __init__(self):
        self.responses = []  # List of {"source": "GPT", "content": "..."} dicts
        self.prompt = ""
        self.feature_folder = None  # Stores path for Save function
        self.attachments = []  # List of (filename, content, lines) tuples

        # LLM sources for tagging responses
        self.llm_sources = ["ChatGPT", "Claude", "Gemini", "Perplexity", "Grok", "DeepSeek", "Mistral", "Other"]

        # Use TkinterDnD if available for drag-drop support
        if HAS_DND:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()
        self.root.title("MCP Clipboard")
        self.root.configure(bg='#010409')
        self.root.geometry("400x700")
        self.root.resizable(True, True)

        # Title
        title = tk.Label(
            self.root,
            text="MCP Clipboard",
            font=('Segoe UI', 16, 'bold'),
            fg='#f0f6fc',
            bg='#010409'
        )
        title.pack(pady=(20, 5))

        # Favorites bar
        fav_frame = tk.Frame(self.root, bg='#010409')
        fav_frame.pack(pady=(5, 15))

        self.favorites = [
            ("docs-mcp", "C:/Users/willh/.mcp-servers/docs-mcp/coderef/working"),
            ("gridiron", "C:/Users/willh/Desktop/latest-sim/gridiron-franchise/coderef"),
            ("scraper", "C:/Users/willh/Desktop/projects - current-location/next-scraper/coderef"),
            ("★", None),
            ("★", None),
        ]

        for i, (label, path) in enumerate(self.favorites):
            btn = tk.Button(
                fav_frame,
                text=label if path else "★",
                bg='#161b22' if path else '#161b22',
                fg='#58a6ff' if path else '#6e7681',
                activebackground='#21262d',
                font=('Segoe UI', 8),
                width=8,
                cursor='hand2',
                command=lambda p=path: self.open_favorite(p)
            )
            btn.pack(side=tk.LEFT, padx=2)

        # Prompt section
        prompt_frame = tk.Frame(self.root, bg='#010409')
        prompt_frame.pack(fill=tk.X, padx=20, pady=(0, 5))

        prompt_label = tk.Label(
            prompt_frame,
            text="Prompt (optional)",
            font=('Segoe UI', 9),
            fg='#8b949e',
            bg='#010409'
        )
        prompt_label.pack(anchor=tk.W)

        prompt_row = tk.Frame(prompt_frame, bg='#010409')
        prompt_row.pack(fill=tk.X, pady=(2, 10))

        self.prompt_status = tk.Label(
            prompt_row,
            text="No prompt",
            font=('Segoe UI', 10),
            fg='#6e7681',
            bg='#0d1117',
            padx=10,
            pady=5,
            width=25,
            anchor=tk.W
        )
        self.prompt_status.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(
            prompt_row, text="Load",
            bg='#1a7f37', fg='white', activebackground='#238636',
            font=('Segoe UI', 9), width=6, cursor='hand2',
            command=self.load_prompt
        ).pack(side=tk.LEFT, padx=(5, 0))

        tk.Button(
            prompt_row, text="Set",
            bg='#161b22', fg='#c9d1d9', activebackground='#21262d',
            font=('Segoe UI', 9), width=6, cursor='hand2',
            command=self.set_prompt
        ).pack(side=tk.LEFT, padx=(5, 0))

        tk.Button(
            prompt_row, text="Clear",
            bg='#161b22', fg='#8b949e', activebackground='#21262d',
            font=('Segoe UI', 9), width=6, cursor='hand2',
            command=self.clear_prompt
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Separator line
        separator1 = tk.Frame(self.root, bg='#21262d', height=1)
        separator1.pack(fill=tk.X, padx=20, pady=(15, 10))

        # Responses section label
        responses_label = tk.Label(
            self.root,
            text="LLM Responses",
            font=('Segoe UI', 9),
            fg='#8b949e',
            bg='#010409'
        )
        responses_label.pack(anchor=tk.W, padx=20)

        # Counter
        self.counter = tk.Label(
            self.root,
            text="0 responses",
            font=('Segoe UI', 20, 'bold'),
            fg='#58a6ff',
            bg='#010409'
        )
        self.counter.pack(pady=(10, 5))

        # Char count
        self.char_count = tk.Label(
            self.root,
            text="0 chars",
            font=('Segoe UI', 11),
            fg='#8b949e',
            bg='#010409'
        )
        self.char_count.pack(pady=(0, 15))

        # Button frame
        btn_frame = tk.Frame(self.root, bg='#010409')
        btn_frame.pack(pady=10)

        # Buttons
        btn_style = {'font': ('Segoe UI', 10), 'width': 10, 'cursor': 'hand2'}

        tk.Button(
            btn_frame, text="Paste",
            bg='#1a7f37', fg='white', activebackground='#238636',
            command=self.paste, **btn_style
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="View",
            bg='#161b22', fg='#8b949e', activebackground='#21262d',
            command=self.toggle_view, **btn_style
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="Clear",
            bg='#161b22', fg='#f85149', activebackground='#f85149',
            command=self.clear, **btn_style
        ).pack(side=tk.LEFT, padx=5)

        # Separator line
        separator2 = tk.Frame(self.root, bg='#21262d', height=1)
        separator2.pack(fill=tk.X, padx=20, pady=(15, 10))

        # Attachments section
        attach_frame = tk.Frame(self.root, bg='#010409')
        attach_frame.pack(fill=tk.X, padx=20, pady=(0, 5))

        attach_label = tk.Label(
            attach_frame,
            text="Attachments (code for review)",
            font=('Segoe UI', 9),
            fg='#8b949e',
            bg='#010409'
        )
        attach_label.pack(anchor=tk.W)

        attach_row = tk.Frame(attach_frame, bg='#010409')
        attach_row.pack(fill=tk.X, pady=(2, 10))

        # Drop zone / status area
        self.attach_status = tk.Label(
            attach_row,
            text="No attachments",
            font=('Segoe UI', 10),
            fg='#6e7681',
            bg='#0d1117',
            padx=10,
            pady=5,
            width=25,
            anchor=tk.W
        )
        self.attach_status.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Enable drag-drop if available
        if HAS_DND:
            self.attach_status.drop_target_register(DND_FILES)
            self.attach_status.dnd_bind('<<Drop>>', self.handle_drop)

        tk.Button(
            attach_row, text="Load",
            bg='#1a7f37', fg='white', activebackground='#238636',
            font=('Segoe UI', 9), width=6, cursor='hand2',
            command=self.attach_file
        ).pack(side=tk.LEFT, padx=(5, 0))

        tk.Button(
            attach_row, text="Paste",
            bg='#161b22', fg='#c9d1d9', activebackground='#21262d',
            font=('Segoe UI', 9), width=6, cursor='hand2',
            command=self.paste_code
        ).pack(side=tk.LEFT, padx=(5, 0))

        tk.Button(
            attach_row, text="View",
            bg='#161b22', fg='#8b949e', activebackground='#21262d',
            font=('Segoe UI', 9), width=6, cursor='hand2',
            command=self.view_attachments
        ).pack(side=tk.LEFT, padx=(5, 0))

        tk.Button(
            attach_row, text="Clear",
            bg='#161b22', fg='#8b949e', activebackground='#21262d',
            font=('Segoe UI', 9), width=6, cursor='hand2',
            command=self.clear_attachments
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Copy All button at bottom
        copy_frame = tk.Frame(self.root, bg='#010409')
        copy_frame.pack(pady=(15, 5))

        tk.Button(
            copy_frame, text="Copy All",
            bg='#1a7f37', fg='white', activebackground='#238636',
            font=('Segoe UI', 12, 'bold'), width=20, cursor='hand2',
            command=self.copy_all
        ).pack()

        # Browser launch buttons
        browser_frame = tk.Frame(self.root, bg='#010409')
        browser_frame.pack(pady=(10, 10))

        browser_label = tk.Label(
            browser_frame,
            text="Quick Launch",
            font=('Segoe UI', 8),
            fg='#6e7681',
            bg='#010409'
        )
        browser_label.pack(pady=(0, 5))

        btn_row = tk.Frame(browser_frame, bg='#010409')
        btn_row.pack()

        self.llm_urls = [
            ("GPT", "https://chat.openai.com"),
            ("Claude", "https://claude.ai"),
            ("Gemini", "https://gemini.google.com"),
            ("Pplx", "https://perplexity.ai"),
            ("Grok", "https://grok.x.ai"),
            ("Deep", "https://chat.deepseek.com"),
            ("Mistral", "https://chat.mistral.ai"),
        ]

        for name, url in self.llm_urls:
            tk.Button(
                btn_row,
                text=name,
                bg='#161b22',
                fg='#8b949e',
                activebackground='#21262d',
                font=('Segoe UI', 7),
                width=6,
                cursor='hand2',
                command=lambda u=url: webbrowser.open(u)
            ).pack(side=tk.LEFT, padx=1)

        # Open All button
        tk.Button(
            browser_frame,
            text="Open All LLMs",
            bg='#1a7f37',
            fg='white',
            activebackground='#238636',
            font=('Segoe UI', 9, 'bold'),
            width=15,
            cursor='hand2',
            command=self.open_all_llms
        ).pack(pady=(8, 0))

        # Preview (hidden by default)
        self.preview_frame = tk.Frame(self.root, bg='#010409')
        self.preview = scrolledtext.ScrolledText(
            self.preview_frame,
            font=('Consolas', 10),
            bg='#0d1117',
            fg='#c9d1d9',
            insertbackground='#c9d1d9',
            height=8,
            wrap=tk.WORD
        )
        self.preview.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.preview_visible = False

        # Status
        self.status = tk.Label(
            self.root,
            text="",
            font=('Segoe UI', 9),
            fg='#8b949e',
            bg='#010409'
        )
        self.status.pack(side=tk.BOTTOM, pady=10)

    def open_favorite(self, path):
        if path:
            filepath = filedialog.askopenfilename(
                title="Select llm-prompt.json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialdir=path
            )
            if filepath:
                self._load_file(filepath)
        else:
            self.show_status("Favorite not set")

    def _load_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.prompt = content.strip()
            self.feature_folder = os.path.dirname(filepath)
            feature_name = os.path.basename(self.feature_folder)
            preview = self.prompt[:30] + "..." if len(self.prompt) > 30 else self.prompt
            self.prompt_status.config(text=preview, fg='#58a6ff')
            self.show_status(f"Loaded from {feature_name}")
        except Exception as e:
            self.show_status(f"Error: {e}")

    def load_prompt(self):
        filepath = filedialog.askopenfilename(
            title="Select llm-prompt.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~/.mcp-servers/docs-mcp/coderef/working")
        )
        if filepath:
            self._load_file(filepath)

    def set_prompt(self):
        try:
            text = pyperclip.paste()
            if text and text.strip():
                self.prompt = text.strip()
                # Show truncated preview
                preview = self.prompt[:30] + "..." if len(self.prompt) > 30 else self.prompt
                self.prompt_status.config(text=preview, fg='#58a6ff')
                self.show_status("Prompt set")
            else:
                self.show_status("Clipboard empty")
        except Exception as e:
            self.show_status(f"Error: {e}")

    def clear_prompt(self):
        self.prompt = ""
        self.prompt_status.config(text="No prompt", fg='#6e7681')
        self.show_status("Prompt cleared")

    def attach_file(self):
        """Open file picker to attach code file."""
        filetypes = [
            ("Code files", "*.py *.js *.ts *.tsx *.jsx *.json *.md *.txt *.html *.css"),
            ("Python", "*.py"),
            ("JavaScript", "*.js *.jsx"),
            ("TypeScript", "*.ts *.tsx"),
            ("All files", "*.*")
        ]
        filepath = filedialog.askopenfilename(
            title="Select file to attach",
            filetypes=filetypes,
            initialdir=self.feature_folder or os.path.expanduser("~")
        )
        if filepath:
            self._attach_from_path(filepath)

    def _attach_from_path(self, filepath):
        """Read and attach a file from path."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            filename = os.path.basename(filepath)
            lines = len(content.splitlines())
            self.attachments.append((filename, content, lines))
            self.update_attach_status()
            self.show_status(f"Attached {filename}")
        except Exception as e:
            self.show_status(f"Error: {e}")

    def handle_drop(self, event):
        """Handle files dropped onto the window."""
        files = self.root.tk.splitlist(event.data)
        for filepath in files:
            # Remove curly braces if present (Windows path handling)
            filepath = filepath.strip('{}')
            self._attach_from_path(filepath)

    def paste_code(self):
        """Paste code from clipboard as attachment."""
        try:
            text = pyperclip.paste()
            if text and text.strip():
                # Ask for filename
                filename = simpledialog.askstring(
                    "Paste Code",
                    "Enter filename for this code:",
                    initialvalue="code.txt"
                )
                if filename:
                    content = text.strip()
                    lines = len(content.splitlines())
                    self.attachments.append((filename, content, lines))
                    self.update_attach_status()
                    self.show_status(f"Attached {filename}")
            else:
                self.show_status("Clipboard empty")
        except Exception as e:
            self.show_status(f"Error: {e}")

    def clear_attachments(self):
        """Clear all attachments."""
        self.attachments = []
        self.update_attach_status()
        self.show_status("Attachments cleared")

    def view_attachments(self):
        """Show attached files in a popup window."""
        if not self.attachments:
            self.show_status("No attachments")
            return

        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Attached Files")
        popup.configure(bg='#010409')
        popup.geometry("500x400")

        # File list
        for filename, content, lines in self.attachments:
            frame = tk.Frame(popup, bg='#0d1117', padx=10, pady=5)
            frame.pack(fill=tk.X, padx=10, pady=5)

            tk.Label(
                frame,
                text=f"📎 {filename} ({lines} lines)",
                font=('Segoe UI', 10, 'bold'),
                fg='#58a6ff',
                bg='#0d1117'
            ).pack(anchor=tk.W)

            # Preview of content
            preview = content[:300] + "..." if len(content) > 300 else content
            text = scrolledtext.ScrolledText(
                frame,
                font=('Consolas', 9),
                bg='#161b22',
                fg='#c9d1d9',
                height=6,
                wrap=tk.WORD
            )
            text.pack(fill=tk.X, pady=(5, 0))
            text.insert('1.0', preview)
            text.config(state=tk.DISABLED)

    def update_attach_status(self):
        """Update the attachment status label."""
        count = len(self.attachments)
        if count == 0:
            self.attach_status.config(text="No attachments", fg='#6e7681')
        else:
            total_lines = sum(a[2] for a in self.attachments)
            names = ", ".join(a[0] for a in self.attachments[:2])
            if count > 2:
                names += f" +{count-2}"
            self.attach_status.config(
                text=f"📎 {names} ({total_lines} lines)",
                fg='#58a6ff'
            )
        if self.preview_visible:
            self.update_preview()

    def paste(self):
        try:
            text = pyperclip.paste()
            if text and text.strip():
                # Show source selection dialog
                self.show_source_dialog(text.strip())
            else:
                self.show_status("Clipboard empty")
        except Exception as e:
            self.show_status(f"Error: {e}")

    def show_source_dialog(self, content):
        """Show dialog to select LLM source for the response."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select LLM Source")
        dialog.configure(bg='#010409')
        dialog.geometry("250x280")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Which LLM is this from?",
            font=('Segoe UI', 10),
            fg='#c9d1d9',
            bg='#010409'
        ).pack(pady=(15, 10))

        for source in self.llm_sources:
            tk.Button(
                dialog,
                text=source,
                bg='#161b22',
                fg='#c9d1d9',
                activebackground='#21262d',
                font=('Segoe UI', 9),
                width=15,
                cursor='hand2',
                command=lambda s=source: self.add_response_with_source(dialog, s, content)
            ).pack(pady=2)

    def add_response_with_source(self, dialog, source, content):
        """Add response with LLM source tag."""
        dialog.destroy()
        self.responses.append({"source": source, "content": content})
        self.update_counter()
        self.show_status(f"Added {source} response")

    def copy_all(self):
        if self.responses or self.prompt or self.attachments:
            # Build structured JSON output
            output = {
                "prompt": self.prompt if self.prompt else None,
                "attachments": [
                    {
                        "filename": filename,
                        "lines": lines,
                        "content": content
                    }
                    for filename, content, lines in self.attachments
                ] if self.attachments else [],
                "responses": [
                    {
                        "source": resp["source"],
                        "content": resp["content"]
                    }
                    for resp in self.responses
                ] if self.responses else [],
                "metadata": {
                    "response_count": len(self.responses),
                    "attachment_count": len(self.attachments),
                    "sources": list(set(resp["source"] for resp in self.responses)) if self.responses else []
                }
            }

            # Remove None values
            if output["prompt"] is None:
                del output["prompt"]

            combined = json.dumps(output, indent=2)
            pyperclip.copy(combined)
            count = len(self.responses)
            attach_count = len(self.attachments)
            status_parts = []
            if self.prompt:
                status_parts.append("prompt")
            if attach_count:
                status_parts.append(f"{attach_count} files")
            if count:
                status_parts.append(f"{count} responses")
            self.show_status(f"Copied JSON: {' + '.join(status_parts)}")
        else:
            self.show_status("Nothing to copy")

    def toggle_view(self):
        if self.preview_visible:
            self.preview_frame.pack_forget()
            self.root.geometry("400x700")
        else:
            self.preview_frame.pack(fill=tk.BOTH, expand=True)
            self.root.geometry("400x900")
            self.update_preview()
        self.preview_visible = not self.preview_visible

    def clear(self):
        self.responses = []
        self.attachments = []
        self.update_counter()
        self.update_attach_status()
        self.update_preview()
        self.show_status("Cleared")

    def update_counter(self):
        count = len(self.responses)
        text = f"{count} response" if count == 1 else f"{count} responses"
        self.counter.config(text=text)

        # Update char count
        total_chars = sum(len(r["content"]) for r in self.responses)
        self.char_count.config(text=f"{total_chars:,} chars")

        if self.preview_visible:
            self.update_preview()

    def update_preview(self):
        self.preview.delete('1.0', tk.END)
        parts = []
        if self.prompt:
            parts.append(f"=== PROMPT ===\n{self.prompt}")
        if self.attachments:
            attach_parts = []
            for filename, content, lines in self.attachments:
                # Truncate content for preview if too long
                preview_content = content[:500] + "..." if len(content) > 500 else content
                attach_parts.append(f"--- {filename} ({lines} lines) ---\n{preview_content}")
            parts.append(f"=== ATTACHMENTS ===\n" + '\n\n'.join(attach_parts))
        if self.responses:
            resp_parts = []
            for resp in self.responses:
                preview_content = resp["content"][:500] + "..." if len(resp["content"]) > 500 else resp["content"]
                resp_parts.append(f"--- {resp['source']} ---\n{preview_content}")
            parts.append(f"=== RESPONSES ===\n" + '\n\n'.join(resp_parts))
        self.preview.insert('1.0', '\n\n'.join(parts))

    def open_all_llms(self):
        """Open all LLM chat windows."""
        for name, url in self.llm_urls:
            webbrowser.open(url)
        self.show_status(f"Opened {len(self.llm_urls)} LLM windows")

    def show_status(self, message):
        self.status.config(text=message)
        self.root.after(2000, lambda: self.status.config(text=""))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MCPClipboard()
    app.run()
