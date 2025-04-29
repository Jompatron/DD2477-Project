const NOTE_BASE = { C:0, D:2, E:4, F:5, G:7, A:9, B:11 };

function pitchToMidi(note) {
  const m = note.match(/^([A-G])([#b\-]{0,2})(-?\d+)$/);
  if (!m) throw new Error(`Unknown pitch: ${note}`);
  const [, letter, acc, octStr] = m;
  let semitone = NOTE_BASE[letter];
  for (const ch of acc) {
    if (ch === '#') semitone += 1;
    else if (ch === '-'|| ch === 'b') semitone -= 1;
  }
  const octave = parseInt(octStr, 10);
  return (octave + 1) * 12 + semitone;
}

/**
 * Compute a transposition-invariant interval-duration fingerprint for a list of tokens.
 */
function fingerprintMelody(tokens) {
  const mids = [];
  const durs = [];
  tokens.forEach(tok => {
    const [pitch, dur] = tok.split('_');
    durs.push(dur);
    if(pitch === 'REST'|| pitch === 'MEASURE_REST'){
      mids.push(null)
    }else{
      mids.push(pitchToMidi(pitch));
    }
  });
  const fp = [];
  let prev = null;
  mids.forEach((midi, idx) => {
    if (prev !== null && midi !== null) {
      const interval = midi - prev;
      const ivStr = interval >= 0 ? `+${interval}` : `${interval}`;
      fp.push(`${ivStr}_${durs[idx]}`);
    }
    prev = midi;
  });
  return fp.join(' ');
}

module.exports = { pitchToMidi, fingerprintMelody };
