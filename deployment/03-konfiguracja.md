# Konfiguracja programu

## Plik config.toml

Program wymaga pliku `config.toml` w głównym katalogu projektu.

### Utworzenie pliku

1. Skopiuj plik przykładowy:
   ```powershell
   copy config.toml.example config.toml
   ```

2. Otwórz `config.toml` w Notatniku:
   ```powershell
   notepad config.toml
   ```

3. Uzupełnij dane:

```toml
[credentials]
username = "TWÓJ_LOGIN"
password = "TWOJE_HASŁO"
pin = "TWÓJ_PIN"

[output]
directory = "C:\\Users\\TWOJA_NAZWA\\Documents\\metin_logs"

[scraper]
timeout_ms = 30000
page_load_delay_ms = 1000
```

### Opis pól

| Pole | Opis | Przykład |
|------|------|---------|
| username | Login do panelu UCP | "hubiklewyJinoo" |
| password | Hasło do panelu UCP | "mojeHaslo123" |
| pin | 5-cyfrowy PIN | "12345" |
| directory | Folder na pliki wynikowe (musi istnieć!) | "C:\\Users\\Hubert\\Documents\\metin_logs" |
| timeout_ms | Timeout połączenia (ms) | 30000 |
| page_load_delay_ms | Opóźnienie między stronami (ms) | 1000 |

### WAŻNE

- Folder w polu `directory` musi istnieć przed uruchomieniem programu!
- Utwórz go ręcznie jeśli nie istnieje.
- Plik `config.toml` zawiera hasło — nie udostępniaj go nikomu.
- Program zapisuje pliki XLSX i CSV w tym folderze.
