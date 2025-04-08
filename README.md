# DD2477-Project

## 🗓️ April 3rd Meeting Notes

Sources of musicxml docs for corpus:
- https://zenodo.org/records/14984509
- https://www.musicxml.com/music-in-musicxml/example-set/

Potential ideas:
- Each token is a concatenation of musical attributions (pitch, duration, sharp/flat, etc.)
- Use n-gram or phrase for melody matching
- Tolerance for differences in melodies
- Implement relevance feedback
- Normalization within the attributes (similar rhythms that may have different durations, normalize the key like Johan suggested)

Random tweaks to improve musical matching (not so important, but helpful):
- A natural sign in front of note should be same as notes with no natural sign of otherwise same characteristics
- Remove grace notes, trills, mordents, slides to increase match rate

## 🗓️ April 8th Meeting Notes

### 🎯 Tasks
- [ ] **Figure out how to add a front-end or search GUI using Kibana**  
  - Ideally use Kibana’s dev tools or something like that
  - **Fallback:** use GUI from course assignemnts

- [ ] **Clarify query differences:**
  - `match`: unordered token match (like keyword search)
  - `match_phrase`: ordered, exact match (hopefully useful for motifs/melodies). But do we need one long string for token? Or does elasticsearch have indices for each token order. And do we instead need to make an n-gram index?

---

### 🧠 Potential Project Goal: Motif / Melody Matching

Our goal is to build a flexible search engine for symbolic music queries, supporting different motif types:

#### 1. 🎼 Pitch-Based
- **Exact match** on tokens like `"C4_quarter D4_quarter E4_quarter"`

#### 2. 🥁 Rhythmic
- Match based **only on durations**
- Strip pitch and octave (e.g. `"quarter quarter half"`) on the search. This is the front-heavy processing approach, slower with real-time searching potentially
- Or make another query field instead of token, like rhythms, when indexings 

#### 3. 🔁 Transposition-Invariant
- Match motifs **regardless of key**
- Maybe use **interval representation** (e.g. `+2 +2 +3`)
- Options:
  - Transpose motif to 16 possible searches
  - Or use the numerical interval representation

 Maybe also use slop or fuzzy search somewhere for ornaments and rest 
