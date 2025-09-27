from transformers import pipeline

# Use the same lightweight model
analyzer = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Example PR diff (pretend this came from GitHub)
diff_text = """
File: hello.py
+ print("Hello world")
- print("Bye world")
"""

labels = ["style issue", "bug risk", "optimization", "good code"]

analysis = analyzer(diff_text, candidate_labels=labels)
print("AI Review:", analysis)
