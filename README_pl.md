<div align="center">

<img src="icon.png" width="96" height="96" alt="Text List Tool logo" />

# 📋 Text List Tool

### Wklej. Podziel. Kopiuj. Gotowe.

Lekka, przenośna aplikacja do szybkiego zarządzania listą 15 tekstów — bez instalacji, bez zależności, jeden plik `.exe`.

[![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D4?style=flat-square&logo=windows)](#-wymagania)
[![Wersja](https://img.shields.io/badge/wersja-1.0.0-89b4fa?style=flat-square)](#-changelog)
[![Rozmiar](https://img.shields.io/badge/rozmiar-~10%20MB-a6e3a1?style=flat-square)](#-pobieranie)
[![Licencja](https://img.shields.io/badge/licencja-Freeware-f38ba8?style=flat-square)](#-licencja)
[![Język](https://img.shields.io/badge/j%C4%99zyk-PL%20%7C%20EN-cdd6f4?style=flat-square)](#-języki)
[![Edycje](https://img.shields.io/badge/edycje-Tkinter%20%7C%20PyQt6-89b4fa?style=flat-square)](#-dwie-edycje)

**[⬇️ Pobierz](#-pobieranie)** · **[✨ Funkcje](#-funkcje)** · **[🧩 Dwie edycje](#-dwie-edycje)** · **[🖥️ Zrzuty ekranu](#️-zrzuty-ekranu)** · **[❓ FAQ](#-faq)**

</div>

---

## O aplikacji

**Text List Tool** to proste, szybkie narzędzie dla każdego, kto regularnie kopiuje i wkleja powtarzalne fragmenty tekstu — kody, linki, komentarze, dane testowe, odpowiedzi, cokolwiek. Wklejasz blok tekstu, aplikacja dzieli go na 15 gotowych do edycji pozycji, a Ty kopiujesz każdą jednym kliknięciem.

Zero instalacji. Zero konta. Zero połączenia z internetem. Uruchamiasz `.exe` i działa.

<div align="center">
<img src="https://img.shields.io/badge/-Bez%20instalatora-1e1e2e?style=for-the-badge" />
<img src="https://img.shields.io/badge/-Bez%20zależności-1e1e2e?style=for-the-badge" />
<img src="https://img.shields.io/badge/-Dane%20tylko%20lokalnie-1e1e2e?style=for-the-badge" />
</div>

---

## ✨ Funkcje

| | |
|---|---|
| 📋 **Podziel na listę** | Wklej dowolny tekst i podziel go jednym kliknięciem (lub `Ctrl+Enter`) na 15 osobnych, edytowalnych pozycji |
| 🖱️ **Kopiowanie 1 klikiem** | Każda pozycja ma własny przycisk **Kopiuj** — z wizualnym potwierdzeniem |
| 📑 **Kopiuj wszystko** | Skopiuj wszystkie niepuste pozycje naraz, jako listę linii |
| ✕ **Czyszczenie pojedyncze** | Usuń jedną pozycję bez kasowania całej listy |
| 🌗 **Jasny / ciemny motyw** | Domyślnie ciemny motyw **Catppuccin Mocha**, przełączany jednym przyciskiem |
| 🌍 **PL / EN** | Pełne tłumaczenie interfejsu, przełączane w locie |
| 📌 **Zawsze na wierzchu** | Przypnij okno nad innymi aplikacjami |
| 🗕 **Tryb kompaktowy** | Zwiń aplikację do małej, przeciąganej ikonki na pulpicie |
| 💾 **Autozapis** | Treść listy, język, motyw i ustawienia zapamiętywane automatycznie między uruchomieniami |
| 🖱️ **Menu kontekstowe** | Wytnij / Kopiuj / Wklej / Zaznacz wszystko pod prawym przyciskiem myszy |

---

## 🧩 Dwie edycje

Text List Tool jest dostępny w **dwóch niezależnych wydaniach** — ta sama funkcjonalność, inny silnik graficzny. Wybierz to, które lepiej wygląda/działa na Twoim systemie.

| | 🔵 Edycja **Tkinter** | 🟣 Edycja **PyQt6** |
|---|:---:|:---:|
| Plik | `lista_tekstow_tk.exe` | `lista_tekstow_qt.exe` |
| Silnik GUI | Python Tkinter (natywny) | PyQt6 |
| Wygląd | Płaski, lekki | Bardziej dopracowane, natywne menu kontekstowe systemu |
| Rozmiar pliku | ~8–10 MB | ~25–35 MB (Qt jest bundlowane w środku) |
| Czas startu | Błyskawiczny | Odrobinę dłuższy (inicjalizacja Qt) |
| Funkcje | Identyczne w obu edycjach | Identyczne w obu edycjach |
| Motyw / języki | Jasny/ciemny (Catppuccin Mocha), PL/EN | Jasny/ciemny (Catppuccin Mocha), PL/EN |

> 💡 Obie edycje zapisują dane do tego samego formatu `text_list_data.json` — możesz swobodnie przełączać się między nimi, Twoja lista pozostanie nienaruszona.

Nie masz preferencji? Zacznij od edycji **Tkinter** — jest mniejsza i uruchamia się szybciej.

---

## 🖥️ Zrzuty ekranu

> _Miejsce na zrzuty ekranu — dodaj pliki `screenshot-dark.png` / `screenshot-light.png` do repozytorium i podmień poniższe odnośniki._

<div align="center">

| Motyw ciemny (domyślny) | Motyw jasny |
|:---:|:---:|
| ![Ciemny motyw](screenshot-dark.png) | ![Jasny motyw](screenshot-light.png) |

</div>

---

## ⬇️ Pobieranie

| Plik | Opis |
|---|---|
| [`lista_tekstow_tk.exe`](../../releases/latest) | Edycja **Tkinter** — mniejsza, szybszy start |
| [`lista_tekstow_qt.exe`](../../releases/latest) | Edycja **PyQt6** — natywne menu kontekstowe systemu |

Aplikacja **nie wymaga instalacji**. Pobierz wybrany plik `.exe`, uruchom go z dowolnego folderu (albo z pendrive'a) — to wszystko. Możesz mieć obie edycje na dysku jednocześnie.

> 🛡️ Windows SmartScreen może przy pierwszym uruchomieniu pokazać ostrzeżenie o nieznanym wydawcy (aplikacja nie jest podpisana certyfikatem code-signing). Kliknij **„Więcej informacji” → „Uruchom mimo to”**.

---

## 🚀 Szybki start

1. Uruchom `lista_tekstow_tk.exe`
2. Wklej tekst do górnego pola (każda linijka = jedna pozycja)
3. Kliknij **„Podziel na listę ⬇”** (lub `Ctrl+Enter`)
4. Kliknij **„Kopiuj”** przy dowolnej pozycji — trafia od razu do schowka

---

## ⌨️ Skróty klawiszowe

| Skrót | Akcja |
|---|---|
| `Ctrl + Enter` | Podziel wklejony tekst na listę |
| `Enter` (w polu pozycji) | Przejdź do kolejnego pola |
| Prawy przycisk myszy | Menu: Wytnij / Kopiuj / Wklej / Zaznacz wszystko |
| Podwójne kliknięcie ikonki (tryb kompaktowy) | Przywróć główne okno |

---

## 💻 Wymagania

- **System:** Windows 10 lub 11 (64-bit)
- **Dodatkowe oprogramowanie:** brak w obu edycjach — Python, biblioteki i wszystkie zależności (w tym Qt dla edycji PyQt6) są wbudowane w plik `.exe`
- **Miejsce na dysku:** ~10 MB (Tkinter) / ~25–35 MB (PyQt6)
- **Uprawnienia:** nie wymaga uprawnień administratora

---

## 🔒 Prywatność

Text List Tool działa **w 100% lokalnie**. Nie łączy się z internetem, nie wysyła żadnych danych, nie zawiera telemetrii ani reklam. Wpisana lista jest zapisywana wyłącznie na Twoim dysku, w pliku `text_list_data.json` obok `.exe`.

---

## 🌍 Języki

- 🇬🇧 English
- 🇵🇱 Polski

Przełącznik języka w prawym górnym rogu aplikacji — zmiana następuje natychmiastowo, bez restartu.

---

## ❓ FAQ

<details>
<summary><b>Którą edycję wybrać — Tkinter czy PyQt6?</b></summary><br>

Funkcjonalnie są identyczne. Edycja **Tkinter** jest mniejsza i startuje szybciej — dobry domyślny wybór. Edycja **PyQt6** ma natywne menu kontekstowe systemu (prawy przycisk myszy) i odrobinę bardziej dopracowaną stylistykę kosztem większego rozmiaru pliku. Obie korzystają z tego samego pliku danych, więc możesz swobodnie przetestować obie.
</details>

<details>
<summary><b>Czy muszę mieć zainstalowanego Pythona?</b></summary><br>

Nie. Aplikacja jest spakowana jako samodzielny plik `.exe` — wszystko czego potrzebuje jest już w środku.
</details>

<details>
<summary><b>Gdzie zapisują się moje dane?</b></summary><br>

W pliku `text_list_data.json`, w tym samym folderze co `.exe`. Możesz go skopiować razem z aplikacją, żeby przenieść swoją listę na inny komputer.
</details>

<details>
<summary><b>Dlaczego Windows pokazuje ostrzeżenie SmartScreen?</b></summary><br>

Plik nie jest podpisany certyfikatem code-signing (koszt certyfikatu nie jest uzasadniony dla darmowego, niekomercyjnego narzędzia). Aplikacja jest bezpieczna — możesz zweryfikować kod źródłowy.
</details>

<details>
<summary><b>Czy mogę używać aplikacji na dwóch komputerach jednocześnie z tą samą listą?</b></summary><br>

Skopiuj plik `.exe` razem z `text_list_data.json` na pendrive lub dysk sieciowy — lista pozostanie zsynchronizowana ręcznie (brak automatycznej synchronizacji w chmurze).
</details>

---

## 📝 Changelog

### 1.0.0
- Pierwsze wydanie
- Dwie edycje: **Tkinter** (`lista_tekstow_tk.exe`) i **PyQt6** (`lista_tekstow_qt.exe`), funkcjonalnie identyczne
- Podział wklejonego tekstu na 15 edytowalnych pozycji
- Kopiowanie pojedyncze i zbiorcze
- Motyw jasny / ciemny (Catppuccin Mocha)
- Pełna lokalizacja PL/EN
- Tryb kompaktowy i „zawsze na wierzchu”
- Autozapis treści i ustawień

---

## 📄 Licencja

**Freeware** — darmowe do użytku osobistego i komercyjnego. Bez gwarancji.

---

## 👤 Autor

**Sebastian Januchowski** — polsoft.ITS™ Group

[![GitHub](https://img.shields.io/badge/GitHub-polsoft--seb07uk-181825?style=flat-square&logo=github)](https://github.com/polsoft-seb07uk)
[![Email](https://img.shields.io/badge/Email-polsoft.its%40mail.com-1e1e2e?style=flat-square&logo=gmail)](mailto:polsoft.its@mail.com)

<div align="center">

---

Made with 🖤 by **polsoft.ITS™ Group**

</div>
