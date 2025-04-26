import os
import json
import re
from pathlib import Path
from music21 import converter, note, chord

doc_id = 1
title_id_map = {}

def quantize_duration(ql):
    # Convert quarterLength into readable labels
    duration_mapping = {
        1.0/3: "triplet_eighth",
        2.0/3: "triplet_quarter",
        0.25: "sixteenth",
        0.5: "eighth",
        0.75: "dotted_eighth",
        1.0: "quarter",
        1.5: "dotted_quarter",
        2.0: "half",
        3.0: "dotted_half",
        4.0: "whole",
        6.0: "dotted_whole",
        8.0: "double_whole", 
        12.0: "dotted_double_whole",
    }

    tolerance = 0.1

    for base_duration, label in duration_mapping.items():
        if abs(ql - base_duration) < tolerance:
            return label
        
    #long holds 
    if ql > 12.0:  # anything longer than triple whole
        return "long_note"
    
    return f"{ql:.2f}"


def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text).strip().lower()

def clean_title(file_path):
    filename = Path(file_path).stem  # gets filename without extension
    filename = filename.replace("_", " ")  # replace underscores with spaces
    return filename.title()  # capitalize nicely

def extract_musicxml_features(file_path):
    try:
        score = converter.parse(file_path)
        try:
            expanded_score = score.expandRepeats()  # Expands repeat structures if present
            if expanded_score is not None:
                score = expanded_score
        except Exception as e:
            print(f"Could not expand repeats for {file_path}: {e}")

        data = {}

        # Metadata
        title = score.metadata.title if score.metadata and score.metadata.title else os.path.basename(file_path)
        composer = score.metadata.composer if score.metadata and score.metadata.composer else "Unknown"

        data['title'] = clean_title(title)
        data['composer'] = clean_text(composer)

        # Key signature
        key = score.analyze('key')
        #music21 uses - for flat 
        key_name = key.name.replace('-', 'b')
        data['key'] = key_name

        # Time signature
        ts = score.recurse().getElementsByClass('TimeSignature').first()
        data['time_signature'] = ts.ratioString if ts else "Unknown"

        # Tokens
        tokens = []
        for element in score.recurse().notesAndRests:
            # Remove ornaments if any (cleanup expressions)
            if hasattr(element, 'expressions'):
                element.expressions.clear()

            if isinstance(element, note.Note):
                if element.duration.isGrace:
                    continue  # Skip grace notes
                #double sharps or flats and fix the - substituion with flat
                pitch = element.pitch.simplifyEnharmonic().nameWithOctave.replace('-', 'b')
                dur_label = quantize_duration(element.quarterLength)
                tokens.append(f"{pitch}_{dur_label}")
            elif isinstance(element, note.Rest):
                if element.quarterLength >= 4.0:
                    tokens.append("MEASURE_REST")
                elif element.quarterLength <= .25:
                    tokens.append(f"REST_sixteenth")
                else:
                    dur_label = quantize_duration(element.quarterLength)
                    tokens.append(f"REST_{dur_label}")
            elif isinstance(element, chord.Chord):
                dur_label = quantize_duration(element.quarterLength)
                for p in element.pitches:
                    pitch = p.simplifyEnharmonic().nameWithOctave.replace('-', 'b')
                    tokens.append(f"{pitch}_{dur_label}")

        data['tokens'] = " ".join(tokens)
        return data
    except Exception as e:
        print(f"\u274c Failed to process {file_path}: {e}")
        return None

# === Main Script ===
music_dir = "corpus"
bulk_file = "data/corpus_bulk_music.json"
all_lines = []

for root, _, files in os.walk(music_dir):
    for filename in files:
        #changed this to .xml instead of .musicxml with corpus batch loading instead of samples
        if filename.lower().endswith(".xml"):
            full_path = os.path.join(root, filename)
            print(f"Processing {full_path}...")
            doc = extract_musicxml_features(full_path)
            if doc:
                # Add Elasticsearch bulk action + doc
                title = doc['title']
                title_id_map[title] = doc_id

                all_lines.append(json.dumps({ "index": { "_index": "musicxml", "_id": doc_id } }))
                all_lines.append(json.dumps(doc))

                doc_id += 1
                if doc_id == 500:
                    break


# Write to file
with open(bulk_file, "w") as f:
    f.write("\n".join(all_lines) + "\n")

print(f"\n Bulk JSON written to {bulk_file} with {len(all_lines)//2} documents.")

# Save title-id mapping
with open("data/corpus_title_id_map.json", "w") as f:
    json.dump(title_id_map, f, indent=2)

print(f"✅ Title-ID mapping saved to data/corpus_title_id_map.json.")
