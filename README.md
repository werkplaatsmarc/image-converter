# Image Converter

Gratis Windows-tool om afbeeldingen te converteren, resizen, achtergronden te verwijderen (AI) en te vectoriseren naar SVG gemaakt door [Werkplaats Marc](https://werkplaatsmarc.be).

Ook beschikbaar als [online webversie](https://werkplaatsmarc.be/image-converter.html) geen installatie nodig, werkt direct in je browser, en is als PWA te installeren als app (icoon op je beginscherm, werkt offline na de eerste keer). Handig voor wie geen Windows draait of niets wil downloaden.

## Functies

- **Formaten converteren**: WebP, JPG, PNG, TIFF, BMP, GIF, ICO
- **Resizen** met behoud van beeldverhouding
- **Achtergrond verwijderen (AI)** volledig lokaal, geen internetverbinding nodig na installatie
- **SVG-vectorisatie** zet een afbeelding om in echte schaalbare vormen (handig voor logo's, Tinkercad, lasersnijden, ...)
- **Batchverwerking** meerdere bestanden of een hele map in één keer
- Kwaliteitsinstelling voor JPG/WebP
- Geen data verlaat je pc alles gebeurt lokaal

## Download

Ga naar de [Releases-pagina](../../releases/latest) en download `image_converter.exe`. Geen installatie nodig gewoon uitvoeren.

> Bij eerste gebruik van "Achtergrond verwijderen" wordt eenmalig een AI-model gedownload (±175MB). Daarna werkt alles offline.

## Gebruik

1. Kies het gewenste uitvoerformaat en eventueel de kwaliteit
2. Vink "Achtergrond verwijderen" of pas de afmetingen aan indien gewenst
3. Klik op **Selecteer Bestanden** (of **Selecteer Map** voor een hele map)
4. Klaar de geconverteerde bestanden staan naast de originelen

## Web-versie / PWA

Geen Windows, of liever niets downloaden? De [online versie](https://werkplaatsmarc.be/image-converter.html) heeft dezelfde functies (formaten converteren, resizen, achtergrond verwijderen met AI, SVG-vectorisatie) en draait volledig in de browser er wordt niets geüpload.

Via "📲 Installeer als app" (Chrome/Edge/Android) of "Zet op beginscherm" (iOS Safari) installeer je 'm als PWA: icoon op je beginscherm, en na een eenmalige download (ongeveer 15-25MB voor de AI-onderdelen) werkt alles ook zonder internet.

## Draaien vanuit broncode

Vereist Python 3.10+.

```bash
pip install pillow rembg onnxruntime vtracer
python image_converter.py
```

### Zelf bouwen tot .exe

```bash
pip install pyinstaller
pyinstaller image_converter.spec
```

Het resultaat staat in `dist/image_converter.exe`.

## Gebruikte bibliotheken

| Bibliotheek | Doel | Licentie |
|---|---|---|
| [Pillow](https://python-pillow.org/) | Beeldbewerking | MIT-CMU |
| [rembg](https://github.com/danielgatis/rembg) | AI-achtergrondverwijdering | MIT |
| [onnxruntime](https://onnxruntime.ai/) | AI-inferentie | MIT |
| [vtracer](https://github.com/visioncortex/vtracer) | SVG-vectorisatie | MIT |
| [U2Net](https://github.com/xuebinqin/U-2-Net) model | AI-model voor achtergrondverwijdering | Apache 2.0 |
| [PyInstaller](https://pyinstaller.org/) | Bouwen tot .exe | GPL (met uitzondering voor gebouwde programma's) |

## Licentie

[MIT](LICENSE) vrij te gebruiken, aan te passen en te herverspreiden, ook commercieel.

## Meer van Werkplaats Marc

- [YouTube](https://youtube.com/@werkplaatsmarc)
- [Website](https://werkplaatsmarc.be)

---

*Bedenk het, maak het.*
