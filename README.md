# DD2477-Project

Hello

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
