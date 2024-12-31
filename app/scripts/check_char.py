import os
import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        return result['encoding']

def convert_to_utf8(file_path, original_encoding):
    try:
        with open(file_path, 'r', encoding=original_encoding) as f:
            content = f.read()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Converted {file_path} from {original_encoding} to UTF-8.")
    except Exception as e:
        print(f"Failed to convert {file_path}: {e}")

def process_files(root_directory):
    for subdir, _, files in os.walk(root_directory):
        for file in files:
            file_path = os.path.join(subdir, file)
            if file_path.endswith('.py'):  # Cible uniquement les fichiers Python
                encoding = detect_encoding(file_path)
                if encoding and encoding.lower() != 'utf-8':
                    convert_to_utf8(file_path, encoding)
                else:
                    print(f"{file_path} is already in UTF-8 or encoding could not be detected.")

if __name__ == "__main__":
    project_directory = 'C:\\Users\\Utilisateur\\Documents\\Projet_Ai\\app'  # Remplacez par le chemin de votre projet
    process_files(project_directory)