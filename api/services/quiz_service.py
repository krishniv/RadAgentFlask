import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database import db_session, MedicalImage, QuizQuestion, QuizOption
from .image_service import ImageService

class QuizService:
    def __init__(self):
        # Load all descriptions for similarity comparison
        descriptions = db_session.query(MedicalImage.description).all()
        self.corpus = [desc[0] for desc in descriptions if desc[0]]  # Filter out None values
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(stop_words='english')
        if self.corpus:  # Only create matrix if we have descriptions
            self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)
    
    def get_similar_options(self, target_desc, num_options=3):
        """Get similar descriptions using TF-IDF and cosine similarity."""
        if not self.corpus or target_desc not in self.corpus:
            # If target isn't in corpus, add it temporarily
            temp_corpus = self.corpus + [target_desc]
            temp_vectorizer = TfidfVectorizer(stop_words='english')
            temp_tfidf_matrix = temp_vectorizer.fit_transform(temp_corpus)
            target_index = len(temp_corpus) - 1
            # Get similarities to all other descriptions
            similarities = cosine_similarity(
                temp_tfidf_matrix[target_index:target_index+1], 
                temp_tfidf_matrix
            ).flatten()
        else:
            # If target is in corpus, use pre-computed matrix
            target_index = self.corpus.index(target_desc)
            target_vec = self.tfidf_matrix[target_index:target_index+1]
            similarities = cosine_similarity(target_vec, self.tfidf_matrix).flatten()
        
        # Get indices of most similar descriptions (excluding exact match)
        similar_indices = similarities.argsort()[-(num_options + 1):][::-1]
        similar_descs = []
        
        for idx in similar_indices:
            if idx < len(self.corpus) and self.corpus[idx] != target_desc:
                similar_descs.append(self.corpus[idx])
                if len(similar_descs) >= num_options:
                    break
        
        # If we don't have enough similar descriptions, add random ones
        while len(similar_descs) < num_options:
            random_desc = random.choice(self.corpus)
            if random_desc != target_desc and random_desc not in similar_descs:
                similar_descs.append(random_desc)
        
        return similar_descs
    
    def generate_question(self):
        """Generate a single question with options."""
        # Get a random image
        image_data = ImageService.get_random_image()
        
        if not image_data:
            return None
        
        correct_desc = image_data["description"]
        similar_options = self.get_similar_options(correct_desc)
        
        all_options = [correct_desc] + similar_options
        random.shuffle(all_options)
        
        # Create a question in the database
        quiz_question = QuizQuestion(
            image_id=image_data["id"],
            correct_answer=correct_desc
        )
        db_session.add(quiz_question)
        db_session.flush()  # Get the ID without committing
        
        # Add the options
        for option_text in all_options:
            option = QuizOption(
                question_id=quiz_question.id,
                option_text=option_text,
                is_correct=1 if option_text == correct_desc else 0
            )
            db_session.add(option)
        
        db_session.commit()
        
        return {
            "image": image_data["url_path"],
            "correct": correct_desc,
            "options": all_options
        }
    
    def generate_multiple_questions(self, amount):
        """Generate multiple quiz questions."""
        return [self.generate_question() for _ in range(amount)] 