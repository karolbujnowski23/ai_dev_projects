import os

def test_deduplication(file_path):
    print(f"Przeprowadzam test deduplikacji na pliku: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Błąd: Plik {file_path} nie istnieje.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        initial_raw_logs = f.read()

    lines = initial_raw_logs.split('\n')
    original_line_count = len(lines)
    print(f"Oryginalna liczba linii: {original_line_count}")

    unique_logs_set = set()
    processed_initial_raw_logs = []
    
    for line in lines:
        if len(line) > 21:  # Sprawdzamy, czy linia ma wystarczającą długość dla timestampu
            log_content = line[21:].strip()
            if log_content not in unique_logs_set:
                unique_logs_set.add(log_content)
                processed_initial_raw_logs.append(line)
        else:
            # Dodaj linie, które nie pasują do formatu, ale mogą być ważne
            processed_initial_raw_logs.append(line)
            
    deduplicated_line_count = len(processed_initial_raw_logs)
    print(f"Liczba linii po deduplikacji (ignorując timestamp): {deduplicated_line_count}")

    # Możesz również zapisać przetworzone logi do nowego pliku, aby je przejrzeć
    with open("temp_logs/deduplicated_test.log", "w", encoding="utf-8") as df:
        df.write("\n".join(processed_initial_raw_logs))
    print("Przetworzone logi zapisano do: temp_logs/deduplicated_test.log")


if __name__ == "__main__":
    # Upewnij się, że ten plik istnieje po uruchomieniu Twojego `app.py`
    base_filtered_path = "temp_logs/base_filtered.log" 
    test_deduplication(base_filtered_path)