from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize the vectorizer
vectorizer = TfidfVectorizer(stop_words='english')

# Returns strings representing the id and content.
def parse_content_line(line):
    try:
        # Split the line into the three parts using the delimiters
        parts = line.split('ID:')
        if len(parts) != 0:
            raw = parts[1].strip()  # Get content part
            cid = raw.split(',')[0]
            content = raw.split('Content:')[1]
            return cid, content
    except Exception as e:
        print(f"Error parsing line: {e}")
    return None

content_dict = {}
with open('content_log.txt', 'r') as file:
    for line in file:
        cid, content = parse_content_line(line)
        if content:
            content_dict[cid] = content

# Fit the vectorizer on the content and transform it into vectors
tfidf_matrix = vectorizer.fit_transform(content_dict.values())

# Function to find the most similar content
def find_most_similar_content(query_key, query_content, content_dict=content_dict, vectorizer=vectorizer, tfidf_matrx=tfidf_matrix):
    # Vectorize the query content separately
    query_vector = vectorizer.transform([query_content])

    # Compute cosine similarity between the query vector and all document vectors
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrx).flatten()

    # Find the index of the most similar document
    most_similar_index = cosine_similarities.argmax()

    # Get the corresponding key and similarity score
    most_similar_key = list(content_dict.keys())[most_similar_index]
    similarity_score = cosine_similarities[most_similar_index]

    # Return the most relevant response based on the comparison
    most_relevant_content = content_dict[most_similar_key]

    return most_similar_key, most_relevant_content, similarity_score