import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1) Load CSV
df = pd.read_csv('evaluation/fuzzy_results.csv')

# 2) Ensure correct types
df['slop']      = df['slop'].astype(int)
df['relevance'] = df['relevance'].astype(int)
df['score']     = pd.to_numeric(df['score'], errors='coerce')

# 3) Compute per-slop metrics
slops          = sorted(df['slop'].unique())
total_rel      = [df[df['slop']==s]['relevance'].sum() for s in slops]
top5_rel       = [df[df['slop']==s].head(5)['relevance'].sum() for s in slops]
average_scores = [df[df['slop']==s]['score'].mean() for s in slops]

# 4) Plot two panels side-by-side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14,5))

# — Left: grouped bars for relevance counts —
x     = np.arange(len(slops))
width = 0.35
ax1.bar(x - width/2, total_rel, width, label='Top 10 Relevant')
ax1.bar(x + width/2, top5_rel,  width, label='Top 5 Relevant')
ax1.set_xticks(x)
ax1.set_xticklabels(slops)
ax1.set_ylim(0, 10)
ax1.set_xlabel('Slop value')
ax1.set_ylabel('Number of Relevant Documents')
ax1.set_title('Relevant Docs Retrieved by Slop')
ax1.legend()
ax1.grid(True)

# — Right: line chart for average scores —
ax2.plot(slops, average_scores, marker='o')
ax2.set_xticks(slops)
ax2.set_xlabel('Slop value')
ax2.set_ylabel('Average Score')
ax2.set_title('Average Score vs Slop')
ax2.grid(True)

plt.tight_layout()
plt.show()
