import os
import nltk
from nltk import pos_tag, word_tokenize, sent_tokenize, ne_chunk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import json

# Download necessary NLTK data packages
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('wordnet')

# Initialize the WordNet Lemmatizer
lemmatizer = WordNetLemmatizer()

def get_wordnet_pos(treebank_tag):
    """Convert treebank tags to wordnet tags."""
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None

def extract_svo(text):
    tokens = word_tokenize(text)
    pos_tags = pos_tag(tokens)
    named_entities = ne_chunk(pos_tags, binary=True)
    
    # Enhanced grammar for better chunking
    grammar = r"""
      NP: {<DT>?<JJ>*<NN.*>+}
          {<NNP>+}
          {<NE>+}
      VP: {<MD>?<VB.*>+<RB>?}
      PP: {<IN><NP>}
      CLAUSE: {<NP><VP><NP|PP>*}
    """
    
    cp = nltk.RegexpParser(grammar)
    tree = cp.parse(named_entities)
    
    svos = []
    for subtree in tree.subtrees():
        if subtree.label() == 'CLAUSE':
            subject = verb = obj = None
            for s in subtree:
                if s.label() == 'NP':
                    if not subject:
                        subject = ' '.join(token for token, pos in s.leaves())
                    else:
                        obj = ' '.join(token for token, pos in s.leaves())
                elif s.label() == 'VP':
                    verb_phrase = ' '.join(token for token, pos in s.leaves())
                    verb = next((token for token, pos in pos_tag(word_tokenize(verb_phrase)) if pos.startswith('V')), None)
                    if verb:
                        verb = lemmatizer.lemmatize(verb, get_wordnet_pos(pos_tag([verb])[0][1]))

            if subject and verb and obj:
                svos.append({
                    "subject": subject,
                    "verb": verb,
                    "stem": lemmatizer.lemmatize(verb, get_wordnet_pos(pos_tag([verb])[0][1])),
                    "object": obj
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
                        "SVO_relationships": svos,
                        "total_SVOs": len(svos)
                    }
                else:
                    errors.append(f"No SVOs found in file {file_name} ({category_prefix}-{idx})")
        except Exception as e:
            errors.append(f"Error processing file {file_name} ({category_prefix}-{idx}): {str(e)}")

    output_json_path = f'C:/Users/hamzah/Desktop/sara/Dataset/NLTKResults/{category_prefix}_results.json'
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
error_log_path = 'C:/Users/hamzah/Desktop/sara/Dataset/NLTKResults/error_log.txt'
os.makedirs(os.path.dirname(error_log_path), exist_ok=True)

# Process each category
for category, prefix in categories.items():
    process_category(category, prefix, error_log_path)

