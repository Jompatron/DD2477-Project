import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the data
df = pd.read_csv('evaluation/dies.csv')

# 2. Ensure relevance column is numeric
df['relevance'] = pd.to_numeric(df['relevance'], errors='coerce').fillna(0).astype(int)

# 3. Count relevant docs per method
relevant_counts = df[df['relevance'] == 1] \
                    .groupby('method') \
                    .size() \
                    .reindex(['combination','melody','rhythm'], fill_value=0)

# 4. Plot
plt.figure(figsize=(8,5))
bars = plt.bar(relevant_counts.index, relevant_counts.values, edgecolor='black')
plt.xlabel('Method')
plt.ylabel('Number of Relevant Documents Retrieved')
plt.title('Comparison of Retrieval Methods')
plt.ylim(0, relevant_counts.values.max() + 1)

# Add labels on top of each bar
for bar in bars:
    h = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, h + 0.1, str(int(h)),
             ha='center', va='bottom')

plt.tight_layout()
plt.show()
