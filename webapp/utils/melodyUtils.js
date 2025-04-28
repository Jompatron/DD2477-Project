// /**
//  * Given a note (e.g. "C4") and an offset (number of scale steps),
//  * returns the transposed note. For simplicity, we assume natural notes.
//  */
// function transposeNote(note, offset) {
//     const scale = ['C', 'D', 'E', 'F', 'G', 'A', 'B'];
//     // Extract the note letter and octave from something like "C4_quarter"
//     const match = note.match(/^([A-G])(\d)$/);
//     if (!match) return note; 
//     let [ , letter, octaveStr ] = match;
//     let octave = parseInt(octaveStr, 10);
//     let idx = scale.indexOf(letter);
    
//     let newIdx = idx + offset;
//     while (newIdx < 0) {
//       newIdx += scale.length;
//       octave -= 1;
//     }
//     while (newIdx >= scale.length) {
//       newIdx -= scale.length;
//       octave += 1;
//     }
//     return scale[newIdx] + octave;
//   }
  
//   /**
//    * Transposes an entire melody string by an offset (in scale degrees).
//    * Each token is expected to be in the format "Note_Duration" (e.g. "C4_quarter").
//    */
//   function transposeMelody(melodyStr, offset) {
//     return melodyStr.split(/\s+/)
//       .map(token => {
//         const parts = token.split('_');
//         if (parts.length < 2) return token;
//         const [note, duration] = parts;
//         const transposedNote = transposeNote(note, offset);
//         return `${transposedNote}_${duration}`;
//       })
//       .join(' ');
//   }
  
//   /**
//    * Generate an array of transposed melody queries.
//    * Here we'll produce 7 queries for offsets 0 through 6.
//    */
//   function generateTransposedQueries(originalMelody) {
//     const transposedQueries = [];
//     for (let i = 0; i < 7; i++) {
//         transposedQueries.push(transposeMelody(originalMelody, i));
//     }
//     console.log(transposedQueries);
//     return transposedQueries;
//   }
  


// module.exports = {
//     transposeNote,
//     transposeMelody,
//     generateTransposedQueries
//   }; 
// /*   // Example usage:
//   const inputMelody = "C4_quarter D4_quarter C4_quarter F4_quarter F4_quarter";
//   "D4_quarter E4_quarter D4_quarter G4_quarter G4_quarter"
//   const transposedQueries = generateTransposedQueries(inputMelody);
//   console.log(transposedQueries);
//    */
const NOTE_BASE = { C:0, D:2, E:4, F:5, G:7, A:9, B:11 };

function pitchToMidi(note) {
  const m = note.match(/^([A-G])([#\-]{0,2})(-?\d+)$/);
  if (!m) throw new Error(`Unknown pitch: ${note}`);
  const [, letter, acc, octStr] = m;
  let semitone = NOTE_BASE[letter];
  for (const ch of acc) {
    if (ch === '#') semitone += 1;
    else if (ch === '-') semitone -= 1;
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
    mids.push(pitch === 'REST' ? null : pitchToMidi(pitch));
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
