import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import os
import sys
import tempfile
import traceback
from datetime import datetime
from pathlib import Path
import concurrent.futures


def log_error(message):
    """Schrijf een foutmelding (met volledige traceback) naar een logbestand.

    Nodig omdat de gebouwde .exe zonder console draait: print()-uitvoer is
    dan onzichtbaar en gaat verloren, waardoor conversiefouten voorheen
    spoorloos verdwenen."""
    try:
        log_dir = Path(os.environ.get('LOCALAPPDATA', tempfile.gettempdir())) / 'QuickImageConverter'
        log_dir.mkdir(parents=True, exist_ok=True)
        with open(log_dir / 'errors.log', 'a', encoding='utf-8') as f:
            f.write(f"\n[{datetime.now().isoformat(timespec='seconds')}] {message}\n")
    except Exception:
        pass  # Loggen mag nooit de conversie zelf laten crashen


def resource_path(relative_path):
    """Bepaal het absolute pad naar een resource, zowel bij het draaien als script
    als vanuit de gebundelde .exe (waar converter.ico naast het exe-bestand staat)."""
    candidates = []
    if getattr(sys, 'frozen', False):
        candidates.append(os.path.dirname(sys.executable))
        if hasattr(sys, '_MEIPASS'):
            candidates.append(sys._MEIPASS)
    candidates.append(os.path.dirname(os.path.abspath(__file__)))

    for base in candidates:
        path = os.path.join(base, relative_path)
        if os.path.exists(path):
            return path
    return os.path.join(candidates[0], relative_path)


class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quick Image Converter")
        self.root.geometry("500x600")

        try:
            self.root.iconbitmap(resource_path("converter.ico"))
        except tk.TclError:
            pass  # Icoon niet gevonden/ongeldig; ga verder zonder icoon

        # Cache voor de rembg AI-sessie (lazy geladen, één keer per programma-run)
        self._rembg_session = None

        # Beschikbare output formaten
        self.output_formats = {
            "WebP - Website optimalisatie": "webp",
            "JPG - Foto's": "jpeg",
            "PNG - Met transparantie": "png",
            "TIFF - Hoge kwaliteit": "tiff",
            "BMP - Windows bitmap": "bmp",
            "GIF - Animatie mogelijk": "gif",
            "ICO - Icoon bestand": "ico",
            "SVG - Vector (web, Tinkercad, ...)": "svg"
        }
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Output format selector
        ttk.Label(main_frame, text="Converteer naar:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.format_var = tk.StringVar()
        self.format_combo = ttk.Combobox(main_frame, 
                                       textvariable=self.format_var,
                                       values=list(self.output_formats.keys()),
                                       width=30)
        self.format_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.format_combo.set("WebP - Website optimalisatie")
        
        # Quality slider
        ttk.Label(main_frame, text="Kwaliteit:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.IntVar(value=90)
        self.quality_slider = ttk.Scale(main_frame, 
                                      from_=1, to=100,
                                      orient=tk.HORIZONTAL,
                                      variable=self.quality_var)
        self.quality_slider.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Size options
        size_frame = ttk.LabelFrame(main_frame, text="Afmetingen", padding="5")
        size_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Maintain original size checkbox
        self.maintain_size = tk.BooleanVar(value=True)
        ttk.Checkbutton(size_frame, 
                       text="Behoud originele afmetingen",
                       variable=self.maintain_size,
                       command=self.toggle_size_inputs).grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        # Width and height entries
        size_controls = ttk.Frame(size_frame)
        size_controls.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(size_controls, text="Breedte:").pack(side=tk.LEFT, padx=5)
        self.width_var = tk.StringVar()
        self.width_entry = ttk.Entry(size_controls, textvariable=self.width_var, width=8)
        self.width_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(size_controls, text="Hoogte:").pack(side=tk.LEFT, padx=5)
        self.height_var = tk.StringVar()
        self.height_entry = ttk.Entry(size_controls, textvariable=self.height_var, width=8)
        self.height_entry.pack(side=tk.LEFT, padx=5)
        
        self.maintain_aspect = tk.BooleanVar(value=True)
        self.aspect_check = ttk.Checkbutton(size_controls, 
                                          text="Behoud beeldverhouding",
                                          variable=self.maintain_aspect)
        self.aspect_check.pack(side=tk.LEFT, padx=5)
        
        # Initial size inputs state
        self.toggle_size_inputs()

        # Achtergrond verwijderen (AI)
        bg_frame = ttk.LabelFrame(main_frame, text="Achtergrond", padding="5")
        bg_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.remove_bg_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(bg_frame,
                       text="Achtergrond verwijderen (AI)",
                       variable=self.remove_bg_var).grid(row=0, column=0, sticky=tk.W)

        ttk.Label(bg_frame,
                 text="Kies PNG/WebP/GIF/TIFF/ICO als output om de\ntransparantie te behouden. Kost een paar\nseconden per afbeelding (eerste keer trager,\ndownloadt eenmalig een AI-model).",
                 justify=tk.LEFT, foreground="gray30").grid(row=1, column=0, sticky=tk.W, pady=(2, 0))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame,
                  text="Selecteer Bestanden",
                  command=self.convert_files).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame,
                  text="Selecteer Map",
                  command=self.convert_folder).pack(side=tk.LEFT, padx=5)

        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame,
                                      variable=self.progress_var,
                                      maximum=100)
        self.progress.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # Status label
        self.status_var = tk.StringVar(value="Gereed voor conversie")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=6, column=0, columnspan=2, sticky=tk.W)

        # Info text
        info_text = ("Ondersteunde formaten:\n"
                    "• Input: PNG, JPG/JPEG, TIFF, WebP, HEIC, BMP, GIF\n"
                    "• Output: WebP, JPG, PNG, TIFF, BMP, GIF, ICO, SVG\n\n"
                    "Tips:\n"
                    "• WebP voor websites (beste compressie)\n"
                    "• JPG voor foto's\n"
                    "• TIFF voor hoogste kwaliteit\n"
                    "• Gebruik 90% kwaliteit voor beste balans\n"
                    "• SVG = echte vector (lijnen/vormen), geen foto-\n"
                    "  detail. Werkt het best bij logo's/eenvoudige\n"
                    "  vormen, eventueel na achtergrond verwijderen")

        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT)
        info_label.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=20)

    def toggle_size_inputs(self):
        """Schakel grootte inputs in/uit gebaseerd op checkbox"""
        state = 'disabled' if self.maintain_size.get() else 'normal'
        self.width_entry.config(state=state)
        self.height_entry.config(state=state)
        self.aspect_check.config(state=state)

    # Formaten die een alfakanaal (transparantie/geen achtergrond) ondersteunen
    ALPHA_SUPPORTED_FORMATS = {'png', 'webp', 'gif', 'tiff', 'ico', 'svg'}

    def _get_rembg_session(self):
        """Laad de AI-sessie voor achtergrondverwijdering lui in en hergebruik
        deze voor alle bestanden in de batch (voorkomt herhaaldelijk laden)."""
        if self._rembg_session is None:
            from rembg import new_session
            self._rembg_session = new_session("u2net")
        return self._rembg_session

    def convert_image(self, input_path, output_format, quality, remove_background=False):
        """Converteer een enkele afbeelding"""
        try:
            input_path = Path(input_path)
            output_path = input_path.with_suffix(f'.{output_format}')
            if output_path.resolve() == input_path.resolve():
                # Zelfde bestandsnaam én extensie (bv. png -> png): nooit het
                # bronbestand overschrijven, ook niet stilzwijgend.
                output_path = input_path.with_name(
                    f"{input_path.stem}_geconverteerd.{output_format}")

            with Image.open(input_path) as img:
                img.load()

                if remove_background:
                    from rembg import remove
                    img = remove(img, session=self._get_rembg_session())

                # Pas grootte aan indien nodig
                if not self.maintain_size.get():
                    try:
                        width = int(self.width_var.get() or img.width)
                        height = int(self.height_var.get() or img.height)

                        if self.maintain_aspect.get():
                            # Bereken nieuwe afmetingen met behoud van ratio
                            ratio = min(width/img.width, height/img.height)
                            width = int(img.width * ratio)
                            height = int(img.height * ratio)

                        img = img.resize((width, height), Image.Resampling.LANCZOS)
                    except ValueError:
                        # Als er ongeldige waardes zijn, behoud originele grootte
                        pass

                # Heeft de bron een alfakanaal (dus geen/transparante achtergrond)?
                has_alpha = img.mode in ('RGBA', 'LA') or (
                    img.mode == 'P' and 'transparency' in img.info)

                if has_alpha and output_format not in self.ALPHA_SUPPORTED_FORMATS:
                    # Doelformaat ondersteunt geen transparantie (bv. JPG/BMP):
                    # vul de achtergrond wit op zodat er geen rommel ontstaat.
                    img = img.convert('RGBA')
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                elif has_alpha:
                    # Doelformaat ondersteunt transparantie: behoud het alfakanaal
                    img = img.convert('RGBA')
                else:
                    img = img.convert('RGB')

                # Voor ICO output, maak meerdere formaten
                if output_format == 'ico':
                    sizes = [16, 32, 48, 64, 128, 256]
                    images = [img.resize((size, size), Image.Resampling.LANCZOS) for size in sizes]

                    images[0].save(output_path, format='ICO',
                                 sizes=[(im.width, im.height) for im in images],
                                 append_images=images[1:])

                # SVG: echte vectorisatie (lijnen/vormen), geen pixelplaatje
                elif output_format == 'svg':
                    import vtracer
                    img = img.convert('RGBA')
                    # Zachte/gedeeltelijke transparantie (bv. anti-aliasing of
                    # AI-achtergrondverwijdering) levert per gradatie een apart
                    # "ringetje" op in de vector-tracing, wat tientallen extra
                    # paden veroorzaakt. Transparantie hard maken (aan/uit)
                    # geeft één schone, bruikbare vorm.
                    r, g, b, a = img.split()
                    a = a.point(lambda p: 255 if p >= 128 else 0)
                    img = Image.merge('RGBA', (r, g, b, a))
                    svg_content = vtracer.convert_pixels_to_svg(
                        list(img.getdata()), size=img.size, colormode='color',
                        filter_speckle=8)
                    output_path.write_text(svg_content, encoding='utf-8')

                # Standaard conversie voor andere formaten
                else:
                    img.save(output_path, output_format.upper(), quality=quality)
                return True

        except Exception:
            log_error(f"Fout bij conversie van {input_path.name}:\n{traceback.format_exc()}")
            return False

    def process_files(self, files):
        """Verwerk een lijst van bestanden"""
        total_files = len(files)
        successful = 0
        quality = self.quality_var.get()
        output_format = self.output_formats[self.format_var.get()]
        remove_background = self.remove_bg_var.get()

        if remove_background:
            try:
                import rembg  # noqa: F401  (alleen om vroeg een duidelijke fout te geven)
            except ImportError:
                messagebox.showerror("Achtergrond verwijderen niet beschikbaar",
                                    "De module 'rembg' (en 'onnxruntime') is niet geïnstalleerd.\n\n"
                                    "Installeer met:\n"
                                    "pip install rembg onnxruntime")
                return
            self.status_var.set("AI-model laden (kan bij eerste gebruik even duren)...")
            self.root.update()

        for idx, file_path in enumerate(files, 1):
            if self.convert_image(file_path, output_format, quality, remove_background):
                successful += 1

            # Update progress
            progress = (idx / total_files) * 100
            self.progress_var.set(progress)
            self.status_var.set(f"Verwerkt: {idx}/{total_files}")
            self.root.update()

        self.progress_var.set(0)
        mislukt = total_files - successful
        self.status_var.set(f"Voltooid: {successful}/{total_files} succesvol geconverteerd")
        detail = f"Conversie voltooid!\n\nSuccesvol: {successful}\nMislukt: {mislukt}"
        if mislukt > 0:
            log_dir = Path(os.environ.get('LOCALAPPDATA', tempfile.gettempdir())) / 'QuickImageConverter'
            detail += f"\n\nDetails over mislukte conversies staan in:\n{log_dir / 'errors.log'}"
        messagebox.showinfo("Voltooid", detail)

    def convert_files(self):
        """Handler voor bestand selectie"""
        files = filedialog.askopenfilenames(
            title="Selecteer bestanden voor conversie",
            filetypes=[
                ("Alle ondersteunde", "*.png;*.jpg;*.jpeg;*.tiff;*.tif;*.webp;*.heic;*.bmp;*.gif"),
                ("PNG bestanden", "*.png"),
                ("JPEG bestanden", "*.jpg;*.jpeg"),
                ("TIFF bestanden", "*.tiff;*.tif"),
                ("WebP bestanden", "*.webp"),
                ("HEIC bestanden", "*.heic"),
                ("BMP bestanden", "*.bmp"),
                ("GIF bestanden", "*.gif")
            ]
        )
        
        if files:
            self.process_files(files)

    def convert_folder(self):
        """Handler voor map selectie"""
        folder = filedialog.askdirectory(title="Selecteer map met afbeeldingen")
        if folder:
            supported_extensions = ['.png', '.jpg', '.jpeg', '.tiff', '.tif', '.webp', '.heic', '.bmp', '.gif']
            
            # Verzamel alle bestanden
            files = []
            for ext in supported_extensions:
                files.extend(Path(folder).glob(f'*{ext}'))
                files.extend(Path(folder).glob(f'*{ext.upper()}'))
            
            if files:
                self.process_files(files)
            else:
                messagebox.showwarning("Geen bestanden",
                                     "Geen ondersteunde afbeeldingsbestanden gevonden in deze map.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()