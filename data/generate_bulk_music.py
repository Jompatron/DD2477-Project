import os
import json
import re
from pathlib import Path
from music21 import converter, note, chord

doc_id = 1
title_id_map = {}

# Base semitone indices for natural notes
NOTE_BASE = {
    'C': 0, 'D': 2, 'E': 4,
    'F': 5, 'G': 7, 'A': 9, 'B': 11
}

EQ_RE = re.compile(r'^([A-G])([#b\-]{0,2})(-?\d+)$')

def quantize_duration(ql):
    # Convert quarterLength into readable labels
    duration_mapping = {
        12.0: "dottedDoubleWhole",
        8.0: "doubleWhole", 
        6.0: "dottedWhole",
        4.0: "whole",
        3.0: "dottedHalf",
        2.0: "half",
        1.5: "dottedQuarter",
        1.0: "quarter",
        0.75: "dottedEighth",
        0.5: "eighth",
        0.25: "sixteenth",
        2.0/3: "tripletQuarter",
        1.0/3: "tripletEighth", 
    }

    tolerance = 0.05

    for base_duration, label in duration_mapping.items():
        if abs(ql - base_duration) < tolerance:
            return label
        
    #long holds 
    if ql > 12.0:  # anything longer than triple whole
        return "long_note"
    
    return f"{ql:.2f}"

def pitch_to_midi(note_name):
    """Convert a note name (e.g. 'C#4', 'E-6', 'F##5') to a MIDI number."""
    match = EQ_RE.match(note_name)
    if not match:
        raise ValueError(f"Unknown pitch: {note_name}")
    letter, acc, oct_str = match.groups()
    octave = int(oct_str)
    semitone = NOTE_BASE[letter]
    # apply accidentals
    for sym in acc:
        if sym == '#':
            semitone += 1
        elif sym in ('-', 'b'):
            semitone -= 1
    # MIDI number formula: (octave + 1) * 12 + semitone
    return (octave + 1) * 12 + semitone

def fingerprint_melody(tokens):
    """
    Given tokens like ['B-4_quarter', 'C5_eighth', ...],
    compute an interval-duration fingerprint.
    """
    mids, durs = [], []
    for tok in tokens:
        try:
            pitch, dur = tok.split('_', 1)
        except ValueError:
            continue
        if pitch == 'REST'or pitch == ('MEASURE'): #split on underscore so this covers MEASURE_REST
            mids.append(None)
        else:
            mids.append(pitch_to_midi(pitch))
        durs.append(dur)

    fp = []
    prev = None
    for midi, dur in zip(mids, durs):
        if prev is not None and midi is not None:
            interval = midi - prev
            iv_str = f"{interval:+d}"
            fp.append(f"{iv_str}_{dur}")
        prev = midi
    return " ".join(fp)


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

        cleaned_title = clean_title(title)
        if cleaned_title.lower().startswith("qm"):
            print(f"Skipping {file_path} as the cleaned title starts with 'Qm'.")
            return None  # Skip processing this file for the sake of a pretty demo
        data['title'] = cleaned_title
        data['composer'] = clean_text(composer)

        # Key signature
        key_sig = score.recurse().getElementsByClass('KeySignature').first()
        if key_sig:
            key = key_sig.asKey()
        #music21 uses - for flat 
        else:
            key = score.analyze('key')
        data['key'] = key.name.replace('-', 'b')

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

        data['tokens'] = tokens
        data['tokens'] = " ".join(tokens)
        data['interval_fp'] = fingerprint_melody(tokens)
        return data
    except Exception as e:
        print(f"\u274c Failed to process {file_path}: {e}")
        return None

# === Main Script ===
music_dir = "../corpus"
test_music_dir = "../melodyTests"
bulk_file = "corpus_interval_bulk_music.json"
all_lines = []

#big corpus
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

                all_lines.append(json.dumps({ "index": { "_index": "musicxml_intervals", "_id": doc_id } }))
                all_lines.append(json.dumps(doc))

                doc_id += 1
                if doc_id == 500:
                    break

#self-written musicxml tests
for root, _, files in os.walk(test_music_dir):
    for filename in files:
        #changed this to .xml instead of .musicxml with corpus batch loading instead of samples
        if filename.lower().endswith(".musicxml"):
            full_path = os.path.join(root, filename)
            print(f"Processing {full_path}...")
            doc = extract_musicxml_features(full_path)
            if doc:
                # Add Elasticsearch bulk action + doc
                title = doc['title']
                title_id_map[title] = doc_id

                all_lines.append(json.dumps({ "index": { "_index": "musicxml_intervals", "_id": doc_id } }))
                all_lines.append(json.dumps(doc))

                doc_id += 1


# Write to file
with open(bulk_file, "w") as f:
    f.write("\n".join(all_lines) + "\n")

print(f"\n Bulk JSON written to {bulk_file} with {len(all_lines)//2} documents.")

# # Save title-id mapping
#change r+ to w when writing from scratch
with open("corpus_title_id_map.json", "w") as f:
    json.dump(title_id_map, f, indent=2)

print(f"✅ Title-ID mapping saved to corpus_title_id_map.json.")
