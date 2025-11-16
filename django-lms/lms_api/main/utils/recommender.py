# main/utils/recommender.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from main.models import Course, CourseRating, StudentCourseEnrollment
from django.db.models import Avg, Count

def build_course_text(course):
    """
    Creates ML text for the TF-IDF model.
    Combines: title + description + techs + category
    """
    category = course.category.title if course.category else ""
    techs = course.techs or ""
    desc = course.description or ""
    title = course.title or ""
    return f"{title} {desc} {techs} {category}"


def get_popularity_score(course):
    """
    Uses #ratings + avg rating + enrollments as a simple popularity signal.
    """
    rating = CourseRating.objects.filter(course=course).aggregate(avg=Avg("rating"))["avg"] or 0
    enroll_count = StudentCourseEnrollment.objects.filter(course=course).count()
    
    popularity = (rating * 2) + (enroll_count * 0.5)
    return popularity


def recommend_courses_for_student(student):
    """
    ML-based recommendation pipeline:
    1. Build TF-IDF vectors
    2. Compute cosine similarity
    3. Use student's enrolled courses to find similar ones
    4. Boost using category & tech overlap
    5. Boost using popularity
    """

    # 1. Get all courses
    courses = list(Course.objects.all())
    if not courses:
        return []

    # 2. Build training text
    corpus = [build_course_text(c) for c in courses]

    # 3. TF-IDF vectorization (ML)
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # 4. ML Similarity: cosine similarity across courses
    similarity_matrix = cosine_similarity(tfidf_matrix)

    # 5. Get student's enrolled courses
    enrolled_ids = StudentCourseEnrollment.objects.filter(student=student).values_list("course_id", flat=True)
    enrolled_courses = [c for c in courses if c.id in enrolled_ids]

    if not enrolled_courses:
        # If student is new → recommend popular courses
        popular_sorted = sorted(
            courses, key=lambda c: get_popularity_score(c), reverse=True
        )
        return popular_sorted[:10]

    # 6. Compute ML similarities for each enrolled course
    course_index = {course.id: idx for idx, course in enumerate(courses)}

    scores = {}

    for enrolled in enrolled_courses:
        idx = course_index[enrolled.id]
        similar_scores = list(enumerate(similarity_matrix[idx]))

        for i, sim_score in similar_scores:
            if courses[i].id in enrolled_ids:
                continue  # skip already enrolled

            if courses[i].id not in scores:
                scores[courses[i].id] = 0

            scores[courses[i].id] += sim_score  # ML score

            # Boost: category match
            if courses[i].category_id == enrolled.category_id:
                scores[courses[i].id] += 0.5

            # Boost: tech overlap
            if courses[i].techs and enrolled.techs:
                overlap = len(set(courses[i].tech_list()) & set(enrolled.tech_list()))
                scores[courses[i].id] += overlap * 0.3

            # Boost: popularity
            scores[courses[i].id] += get_popularity_score(courses[i]) * 0.1

    # 7. Sort by score (descending)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # 8. Return top 10 recommended course objects
    top_course_ids = [course_id for course_id, score in sorted_scores][:10]

    recommended = [c for c in courses if c.id in top_course_ids]
    return recommended
