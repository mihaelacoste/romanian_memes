import pandas as pd
from collections import Counter
from itertools import combinations
import re
import numpy as np
import string

# --- Configuration ---
FILE_NAME = 'romanian_meme_analysis_results_local.csv'
PEOPLE_COLUMN = 'who_is_in_images'
VISUAL_CHAR_COLUMN = 'visual_characteristics'
SENTIMENT_COLUMN = 'visual_sentiment'
OUTPUT_EXCEL_PATH = 'meme_analysis_results_FINAL.xlsx' # Changed filename to prevent clash with potentially corrupt file

# --- 1. Data Cleaning and Counting Function ---
def clean_and_count(df, column_name, ignore_terms=['unknown', 'no text', 'none', 'error', ''], n_top=50):
    df[column_name] = df[column_name].fillna('').astype(str)
    all_terms = []
    chars_to_remove = re.escape(string.punctuation.replace('-', '').replace(',', ''))
    
    for entry in df[column_name]:
        terms = [re.sub(f'[{chars_to_remove}]', '', t).strip() for t in entry.split(',')]
        terms = [term.lower() for term in terms]
        terms = [term for term in terms if term and term not in ignore_terms]
        all_terms.extend(terms)
        
    term_counts = Counter(all_terms)
    print(f"\n--- Analysis for '{column_name}' ---")
    print(f"Total unique terms found (excluding ignored terms): {len(term_counts)}")
    
    return term_counts.most_common(n_top)

# --- 2. Co-occurrence Function (for People-People) ---
def calculate_co_occurrence(df, column_name, top_people_list, n_pairs=100):
    co_occurrence_counts = Counter()
    target_people = {name for name, count in top_people_list}
    chars_to_remove = re.escape(string.punctuation.replace('-', '').replace(',', ''))
    
    for entry in df[column_name]:
        names_in_image = [re.sub(f'[{chars_to_remove}]', '', name).strip().lower() 
                          for name in entry.split(',')]
        names_to_analyze = sorted([name for name in names_in_image if name in target_people])
        
        for pair in combinations(names_to_analyze, 2):
            co_occurrence_counts[pair] += 1
            
    co_occurrence_data = [
        {'Person_A': p1.title(), 'Person_B': p2.title(), 'Co_occurrence_Count': count}
        for (p1, p2), count in co_occurrence_counts.most_common(n_pairs)
    ]
    
    return pd.DataFrame(co_occurrence_data)

# --- 3. People-Sentiment Relationship Function ---
def calculate_people_sentiment_relationship(df, people_col, sentiment_col, ignore_terms=['unknown', 'error', 'no text', 'none', '']):
    
    chars_to_remove = re.escape(string.punctuation.replace('-', '').replace(',', ''))
    
    # 1. Explode both columns
    people_exploded = df[[people_col]].copy()
    people_exploded[people_col] = people_exploded[people_col].fillna('').astype(str).apply(
        lambda x: [re.sub(f'[{chars_to_remove}]', '', t).strip().lower() for t in x.split(',')]
    ).explode(people_col)
    
    sentiment_exploded = df[[sentiment_col]].copy()
    sentiment_exploded[sentiment_col] = sentiment_exploded[sentiment_col].fillna('').astype(str).apply(
        lambda x: [re.sub(f'[{chars_to_remove}]', '', t).strip().lower() for t in x.split(',')]
    ).explode(sentiment_col)
    
    # 2. Combine and Filter
    combined_df = people_exploded.join(sentiment_exploded)
    for col in [people_col, sentiment_col]:
        combined_df = combined_df[~combined_df[col].isin(ignore_terms)]
    
    # 3. Count the unique pairs
    relationship_counts = combined_df.groupby([people_col, sentiment_col]).size().reset_index(name='Co_occurrence_Count')
    
    # 4. Apply Title Case
    relationship_counts[people_col] = relationship_counts[people_col].apply(lambda x: str(x).title())
    relationship_counts[sentiment_col] = relationship_counts[sentiment_col].apply(lambda x: str(x).title())
    
    relationship_counts = relationship_counts.sort_values(by='Co_occurrence_Count', ascending=False)
    
    return relationship_counts

# --- 4. Main Execution and Excel Saving ---

try:
    df = pd.read_csv(FILE_NAME) 
    print(f"Data loaded successfully. Total records: {len(df)}")
    print("-" * 50)
    
    # --- CALCULATIONS ---
    
    # 1. People Frequency (Top 50)
    top_people_list = clean_and_count(df, PEOPLE_COLUMN, n_top=50)
    df_people = pd.DataFrame(top_people_list, columns=['Person', 'Count']).reset_index(drop=True)
    df_people['Person'] = df_people['Person'].apply(lambda x: str(x).title())

    # 2. Co-occurrence (People-People)
    top_20_people = top_people_list[:20] 
    df_co_occurrence = calculate_co_occurrence(df, PEOPLE_COLUMN, top_20_people).reset_index(drop=True)

    # 3. Visual Characteristics Frequency (Top 50)
    top_visual_chars = clean_and_count(df, VISUAL_CHAR_COLUMN, n_top=50)
    df_chars = pd.DataFrame(top_visual_chars, columns=['Characteristic', 'Count']).reset_index(drop=True)
    df_chars['Characteristic'] = df_chars['Characteristic'].apply(lambda x: str(x).title())

    # 4. Visual Sentiment Frequency (Top 5)
    top_sentiment = clean_and_count(df, SENTIMENT_COLUMN, n_top=5)
    df_sentiment = pd.DataFrame(top_sentiment, columns=['Sentiment', 'Count']).reset_index(drop=True)
    df_sentiment['Sentiment'] = df_sentiment['Sentiment'].apply(lambda x: str(x).title())

    # 5. People-Sentiment Relationship
    df_relationship = calculate_people_sentiment_relationship(df, PEOPLE_COLUMN, SENTIMENT_COLUMN).reset_index(drop=True)
    
    print("-" * 50)
    print("NEW ANALYSIS: Top 20 People-Sentiment Relationships:")
    print(df_relationship.head(20))
    print("-" * 50)


    # --- EXCEL EXPORT ---

    # We use openpyxl as the engine for robustness.
    with pd.ExcelWriter(OUTPUT_EXCEL_PATH, engine='openpyxl') as writer:
        df_people.to_excel(writer, sheet_name='1_Top_People_Frequency', index=False)
        df_co_occurrence.to_excel(writer, sheet_name='2_People_Co-occurrence', index=False)
        df_chars.to_excel(writer, sheet_name='3_Visual_Characteristics', index=False)
        df_sentiment.to_excel(writer, sheet_name='4_Visual_Sentiment', index=False)
        df_relationship.to_excel(writer, sheet_name='5_People_Sentiment_Relationship', index=False)
    
    print(f"✅ Success! All analysis results saved to a single Excel file: {OUTPUT_EXCEL_PATH}")
    
except FileNotFoundError:
    print(f"❌ Error: The file '{FILE_NAME}' was not found. Please ensure it is in the same directory as the script.")
except Exception as e:
    # Print a more informative error message if the Excel save failed for some other reason
    print(f"❌ An unexpected critical error occurred during analysis or saving: {e}")
    print("   Please check for data inconsistencies in your CSV or ensure 'openpyxl' is installed.")