# Kanoheda

Make language learning tapes with interwoven Cherokee and English.

## How to add a new story

1. Create a "terms" csv for the story
   a. Make a plaintext file for both the Cherokee and English story
   b. Use `python scripts/split_article_text.py "relative_path_to_file"` to split up sentences.
   c. Copy and paste these rows into GoogleSheets, using a template for another `terms.csv` file, in the "English" and "Syllabary" columns, respectively.
2. Download Cherokee and English audio files  
   a. Annotate each file with ELAN, so that sentence is in an annotation.
