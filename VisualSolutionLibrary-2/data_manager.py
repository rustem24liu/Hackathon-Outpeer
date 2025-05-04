import json
import os
from utils import generate_id, get_timestamp, ensure_directories, save_uploaded_file

# Ensure necessary directories and files exist
ensure_directories()

# Load data from JSON file
def load_data(file_name):
    """Load data from JSON file"""
    try:
        with open(f"data/{file_name}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# Save data to JSON file
def save_data(data, file_name):
    """Save data to JSON file"""
    with open(f"data/{file_name}.json", "w") as f:
        json.dump(data, f, indent=4)

# Solution Management
def get_all_solutions():
    """Get all solutions"""
    return load_data("solutions")

def get_solution_by_id(solution_id):
    """Get solution by ID"""
    solutions = get_all_solutions()
    for solution in solutions:
        if solution["id"] == solution_id:
            return solution
    return None

def add_solution(title, description, uploaded_file, user_id, tags=None):
    """Add a new solution"""
    solutions = get_all_solutions()
    
    solution_id = generate_id()
    file_path = save_uploaded_file(uploaded_file, solution_id)
    
    solution = {
        "id": solution_id,
        "title": title,
        "description": description,
        "file_path": file_path,
        "user_id": user_id,
        "tags": tags or [],
        "created_at": get_timestamp(),
        "views": 0
    }
    
    solutions.append(solution)
    save_data(solutions, "solutions")
    return solution_id

def update_solution(solution_id, title=None, description=None, tags=None):
    """Update an existing solution"""
    solutions = get_all_solutions()
    
    for i, solution in enumerate(solutions):
        if solution["id"] == solution_id:
            if title is not None:
                solutions[i]["title"] = title
            if description is not None:
                solutions[i]["description"] = description
            if tags is not None:
                solutions[i]["tags"] = tags
            solutions[i]["updated_at"] = get_timestamp()
            
            save_data(solutions, "solutions")
            return True
    
    return False

def delete_solution(solution_id):
    """Delete a solution"""
    solutions = get_all_solutions()
    
    for i, solution in enumerate(solutions):
        if solution["id"] == solution_id:
            file_path = solution.get("file_path")
            
            # Delete the file if it exists
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            
            # Remove the solution from the list
            solutions.pop(i)
            save_data(solutions, "solutions")
            
            # Delete associated comments and ratings
            delete_comments_for_solution(solution_id)
            delete_ratings_for_solution(solution_id)
            
            return True
    
    return False

def increment_solution_views(solution_id):
    """Increment view count for a solution"""
    solutions = get_all_solutions()
    
    for i, solution in enumerate(solutions):
        if solution["id"] == solution_id:
            solutions[i]["views"] = solutions[i].get("views", 0) + 1
            save_data(solutions, "solutions")
            return True
    
    return False

# User Management
def get_all_users():
    """Get all users"""
    return load_data("users")

def get_user_by_id(user_id):
    """Get user by ID"""
    users = get_all_users()
    for user in users:
        if user["id"] == user_id:
            return user
    return None

def get_user_by_username(username):
    """Get user by username"""
    users = get_all_users()
    for user in users:
        if user["username"].lower() == username.lower():
            return user
    return None

def add_user(username, password_hash):
    """Add a new user"""
    users = get_all_users()
    
    # Check if username already exists
    if get_user_by_username(username):
        return None
    
    user_id = generate_id()
    user = {
        "id": user_id,
        "username": username,
        "password_hash": password_hash,
        "created_at": get_timestamp()
    }
    
    users.append(user)
    save_data(users, "users")
    return user_id

# Comment Management
def get_all_comments():
    """Get all comments"""
    return load_data("comments")

def get_comments_for_solution(solution_id):
    """Get comments for a specific solution"""
    comments = get_all_comments()
    return [comment for comment in comments if comment["solution_id"] == solution_id]

def add_comment(solution_id, user_id, content):
    """Add a new comment"""
    comments = get_all_comments()
    
    comment = {
        "id": generate_id(),
        "solution_id": solution_id,
        "user_id": user_id,
        "content": content,
        "created_at": get_timestamp()
    }
    
    comments.append(comment)
    save_data(comments, "comments")
    return comment["id"]

def delete_comment(comment_id):
    """Delete a comment"""
    comments = get_all_comments()
    
    for i, comment in enumerate(comments):
        if comment["id"] == comment_id:
            comments.pop(i)
            save_data(comments, "comments")
            return True
    
    return False

def delete_comments_for_solution(solution_id):
    """Delete all comments for a solution"""
    comments = get_all_comments()
    new_comments = [comment for comment in comments if comment["solution_id"] != solution_id]
    
    if len(new_comments) != len(comments):
        save_data(new_comments, "comments")
        return True
    
    return False

# Rating Management
def get_all_ratings():
    """Get all ratings"""
    return load_data("ratings")

def get_rating_by_user_and_solution(user_id, solution_id):
    """Get rating by user and solution"""
    ratings = get_all_ratings()
    for rating in ratings:
        if rating["user_id"] == user_id and rating["solution_id"] == solution_id:
            return rating
    return None

def add_or_update_rating(solution_id, user_id, rating_value):
    """Add or update a rating"""
    ratings = get_all_ratings()
    
    # Check if user has already rated this solution
    existing_rating = None
    for i, r in enumerate(ratings):
        if r["user_id"] == user_id and r["solution_id"] == solution_id:
            existing_rating = i
            break
    
    if existing_rating is not None:
        # Update existing rating
        ratings[existing_rating]["rating"] = rating_value
        ratings[existing_rating]["updated_at"] = get_timestamp()
    else:
        # Add new rating
        new_rating = {
            "id": generate_id(),
            "solution_id": solution_id,
            "user_id": user_id,
            "rating": rating_value,
            "created_at": get_timestamp()
        }
        ratings.append(new_rating)
    
    save_data(ratings, "ratings")
    return True

def delete_ratings_for_solution(solution_id):
    """Delete all ratings for a solution"""
    ratings = get_all_ratings()
    new_ratings = [rating for rating in ratings if rating["solution_id"] != solution_id]
    
    if len(new_ratings) != len(ratings):
        save_data(new_ratings, "ratings")
        return True
    
    return False

def get_solution_average_rating(solution_id):
    """Get average rating for a solution"""
    ratings = get_all_ratings()
    solution_ratings = [r["rating"] for r in ratings if r["solution_id"] == solution_id]
    
    if solution_ratings:
        return sum(solution_ratings) / len(solution_ratings)
    
    return 0

def get_solution_rating_count(solution_id):
    """Get count of ratings for a solution"""
    ratings = get_all_ratings()
    return len([r for r in ratings if r["solution_id"] == solution_id])

# Tag Management
def get_all_tags():
    """Get all unique tags from solutions"""
    solutions = get_all_solutions()
    all_tags = []
    
    for solution in solutions:
        tags = solution.get("tags", [])
        all_tags.extend(tags)
    
    # Return unique tags
    return list(set(all_tags))

def get_solutions_by_tag(tag):
    """Get solutions by tag"""
    solutions = get_all_solutions()
    return [solution for solution in solutions if tag in solution.get("tags", [])]

def get_solutions_by_user(user_id):
    """Get solutions by user"""
    solutions = get_all_solutions()
    return [solution for solution in solutions if solution["user_id"] == user_id]

def search_solutions(query):
    """Search solutions by title, description, or tags"""
    solutions = get_all_solutions()
    results = []
    
    query = query.lower()
    for solution in solutions:
        if (query in solution["title"].lower() or
            query in solution["description"].lower() or
            any(query in tag.lower() for tag in solution.get("tags", []))):
            results.append(solution)
    
    return results
