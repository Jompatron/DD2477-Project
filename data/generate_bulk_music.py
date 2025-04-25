import os
import json
from music21 import converter, note, chord

def quantize_duration(ql):
    # Convert quarterLength into readable labels
    if ql == 1.0:
        return "quarter"
    elif ql == 0.5:
        return "eighth"
    elif ql == 2.0:
        return "half"
    elif ql == 0.25:
        return "sixteenth"
    elif ql == 4.0:
        return "whole"
    else:
        return f"{ql:.2f}"

def extract_musicxml_features(file_path):
    try:
        score = converter.parse(file_path)
        try:
            score = score.expandRepeats()  # Try expanding repeats
        except Exception as e:
            print(f"Warning: could not expand repeats in {file_path}: {e}. Continuing with original score.")
        # ... continue processing
        data = {}
        data['title'] = score.metadata.title if score.metadata and score.metadata.title else os.path.basename(file_path)
        data['composer'] = score.metadata.composer if score.metadata and score.metadata.composer else "Unknown"

        key = score.analyze('key')
        data['key'] = key.name

        ts = score.recurse().getElementsByClass('TimeSignature').first()
        data['time_signature'] = ts.ratioString if ts else "Unknown"

        tokens = []
        for element in score.recurse().notesAndRests:
            if isinstance(element, note.Note):
                pitch = element.nameWithOctave
                dur_label = quantize_duration(element.quarterLength)
                tokens.append(f"{pitch}_{dur_label}")
            elif isinstance(element, note.Rest):
                dur_label = quantize_duration(element.quarterLength)
                tokens.append(f"REST_{dur_label}")
            elif isinstance(element, chord.Chord):
                dur_label = quantize_duration(element.quarterLength)
                for p in element.pitches:
                    tokens.append(f"{p.nameWithOctave}_{dur_label}")
        data['tokens'] = " ".join(tokens)
        return data
    except Exception as e:
        print(f"❌ Failed to process {file_path}: {e}")
        return None

# === Main Script ===
music_dir = "data/xmlsamples"
bulk_file = "data/bulk_music.json"
all_lines = []

for root, _, files in os.walk(music_dir):
    for filename in files:
        if filename.lower().endswith(".musicxml"):
            full_path = os.path.join(root, filename)
            print(f"🎵 Processing {full_path}...")
            doc = extract_musicxml_features(full_path)
            if doc:
                # Add Elasticsearch bulk action + doc
                all_lines.append(json.dumps({ "index": { "_index": "musicxml" } }))
                all_lines.append(json.dumps(doc))

# Write to file
with open(bulk_file, "w") as f:
    f.write("\n".join(all_lines) + "\n")

print(f"\n✅ Bulk JSON written to {bulk_file} with {len(all_lines)//2} documents.")
