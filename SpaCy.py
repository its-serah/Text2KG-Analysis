import spacy
import json
import os

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    print("Model not found. Please download the model using 'python -m spacy download en_core_web_sm'")

def find_subject(verb):
    for possible_subject in verb.children:
        if possible_subject.dep_ in ('nsubj', 'nsubjpass'):
            return possible_subject
    return None

def find_object(verb):
    for possible_object in verb.children:
        if possible_object.dep_ in ('dobj', 'dative', 'pobj'):
            if possible_object.dep_ == 'pobj' and possible_object.head.dep_ != 'prep':
                continue
            return possible_object
    return None

def extract_svo(text):
    doc = nlp(text)
    svos = []
    for sent in doc.sents:
        for possible_verb in sent:
            if possible_verb.pos_ == 'VERB':
                subj = find_subject(possible_verb)
                obj = find_object(possible_verb)
                if subj and obj:
                    svos.append({
                        "subject": subj.text,
                        "verb": possible_verb.text,
                        "stem": possible_verb.lemma_,
                        "object": obj.text
                    })
    return svos

def process_category(category_name, category_prefix, error_log_path):
    folder_path = f'C:/Users/hamzah/Desktop/sara/Dataset/{category_name}'  
    files = sorted(os.listdir(folder_path))[:50]  
    all_data = {}
    errors = []
    
    for idx, file_name in enumerate(files, start=1):
        file_path = os.path.join(folder_path, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                svos = extract_svo(text)
                if svos:
                    all_data[f"{category_prefix}-{idx}"] = {
                        "svo_relationships": svos,
                        "total_SVOs": len(svos)
                    }
                else:
                    errors.append(f"No SVOs found in file {file_name} ({category_prefix}-{idx})")
        except Exception as e:
            errors.append(f"Error processing file {file_name} ({category_prefix}-{idx}): {str(e)}")
    
    output_json_path = f'C:/Users/hamzah/Desktop/sara/Dataset/SpaCyResults/{category_prefix}_results.json'  
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(all_data, json_file, indent=4, ensure_ascii=False)
    print(f"SVOs for {category_name} saved to {output_json_path}")

    # Write errors to log file
    with open(error_log_path, 'a', encoding='utf-8') as log_file:
        for error in errors:
            log_file.write(error + '\n')
    print(f"Errors for {category_name} logged to {error_log_path}")

# Categories and their prefixes
categories = {
    "literature": "Lit",
    "medicalArticles": "Med",
    "movieScripts": "Mov",
    "newsandPressReleases": "NPR",
}

# Error log path
error_log_path = 'C:/Users/hamzah/Desktop/sara/Dataset/SpaCyResults/error_log.txt'
os.makedirs(os.path.dirname(error_log_path), exist_ok=True)

# Process each category
for category, prefix in categories.items():
    process_category(category, prefix, error_log_path)


