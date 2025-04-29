function fingerprintRhythm(tokens) {
    const durationMapping = {
        tripletEighth: 1.0 / 3,
        tripletQuarter: 2.0 / 3,
        sixteenth: 0.25,
        eighth: 0.5,
        dottedEighth: 0.75,
        quarter: 1.0,
        dottedQuarter: 1.5,
        half: 2.0,
        dottedHalf: 3.0,
        whole: 4.0,
        dottedWhole: 6.0,
        doubleWhole: 8.0,
        dottedDoubleWhole: 12.0
    };

    const durs = [];

    for (const tok of tokens) {
        const parts = tok.split("_");
        if (parts.length === 2) {
            const dur = parts[1];
            if (durationMapping.hasOwnProperty(dur)) {
                durs.push(dur);
            }
        }else if (parts.length === 1) {
            const dur = parts[0];
            if (durationMapping.hasOwnProperty(dur)) {
                durs.push(dur);
            }
        } else {
            throw new Error(`Unknown token format: ${tok}`);
        }
    }

    const fp = [];
    let prev = null;

    for (const dur of durs) {
        const current = durationMapping[dur];
        if (prev !== null) {
            const ratio = current / prev;
            const ratioStr = ratio.toFixed(2);  // keep 2 decimal places
            fp.push(ratioStr);
        }
        prev = current;
    }

    return fp.join(" ");
}

module.exports = { fingerprintRhythm };