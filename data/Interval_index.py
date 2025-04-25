import os
import re
import json
from music21 import converter, note, chord

# Base semitone indices for natural notes
NOTE_BASE = {
    'C': 0, 'D': 2, 'E': 4,
    'F': 5, 'G': 7, 'A': 9, 'B': 11
}

EQ_RE = re.compile(r'^([A-G])([#\-]{0,2})(-?\d+)$')

def quantize_duration(ql):
    """Convert a quarterLength to a duration label."""
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
        if pitch == 'REST':
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


def extract_musicxml_features(file_path):
    try:
        score = converter.parse(file_path)
        try:
            score = score.expandRepeats()
        except Exception:
            pass

        data = {}
        # Title
        data['title'] = (score.metadata.title
                         if score.metadata and score.metadata.title
                         else os.path.basename(file_path))
        # Composer: try composer field, then creators list
        composer = 'Unknown'
        if score.metadata:
            if score.metadata.composer:
                composer = score.metadata.composer
            elif getattr(score.metadata, 'creators', None):
                composer = ', '.join(score.metadata.creators)
        data['composer'] = composer

        # Key and time signature
        key = score.analyze('key')
        data['key'] = key.name
        ts = score.recurse().getElementsByClass('TimeSignature').first()
        data['time_signature'] = ts.ratioString if ts else 'Unknown'

        # Tokenize
        tokens = []
        for el in score.recurse().notesAndRests:
            dur_label = quantize_duration(el.quarterLength)
            if isinstance(el, note.Note):
                tokens.append(f"{el.nameWithOctave}_{dur_label}")
            elif isinstance(el, note.Rest):
                tokens.append(f"REST_{dur_label}")
            elif isinstance(el, chord.Chord):
                for p in el.pitches:
                    tokens.append(f"{p.nameWithOctave}_{dur_label}")

        data['tokens'] = tokens
        data['tokens_str'] = " ".join(tokens)
        data['interval_fp'] = fingerprint_melody(tokens)
        return data
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None


if __name__ == '__main__':
    music_dir = 'data/xmlsamples'
    bulk_file = 'data/bulk_music_with_intervals.json'
    all_lines = []
    for root, _, files in os.walk(music_dir):
        for fname in files:
            if not fname.lower().endswith('.musicxml'):
                continue
            path = os.path.join(root, fname)
            doc = extract_musicxml_features(path)
            if doc:
                all_lines.append(json.dumps({ 'index': { '_index': 'musicxml_intervals' } }))
                all_lines.append(json.dumps(doc))
    with open(bulk_file, 'w') as out:
        out.write("\n".join(all_lines) + "\n")
    print(f"Bulk JSON with intervals written to {bulk_file} ({len(all_lines)//2} docs)")

# ES mapping recommendation:
# PUT /musicxml_intervals
# { "mappings": { "properties": { ... } } }
