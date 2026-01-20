from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDBManager:

    
    def __init__(self):
        mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
        mongodb_db = os.getenv('MONGODB_DB', 'ProjetoBD2')
        mongodb_collection = os.getenv('MONGODB_COLLECTION', 'evaluations')
        self.client = MongoClient(mongodb_url)
        self.db = self.client[mongodb_db]

        self.evaluations = self.db[mongodb_collection]
        
        self.create_indexes()
    
    def create_indexes(self):
        try:
            self.evaluations.create_index("user_id")
            self.evaluations.create_index("class_schedule_id")
            self.evaluations.create_index("member_id")
            self.evaluations.create_index("instructor_id")
            # Evita duplicatas por utilizador + agendamento
            self.evaluations.create_index([("user_id", 1), ("class_schedule_id", 1)], unique=True)
            # Compatibilidade: algumas instâncias antigas usavam `class_id` + `member_id` como índice único
            try:
                self.evaluations.create_index([("class_id", 1), ("member_id", 1)], unique=True)
            except Exception:
                # ignore if index can't be created (existing conflicting index)
                pass
        except:
            pass  
    
    
    def add_class_evaluation(self, user_id, class_schedule_id, rating, comment="", member_id=None, instructor_id=None, member_name=None, class_name=None):

        if rating < 1 or rating > 5:
            raise ValueError("Rating deve estar entre 1 e 5")
        
        evaluation = {
            "user_id": user_id,
            "class_schedule_id": class_schedule_id,
            # Persist also as `class_id` for backward compatibility with older indexes
            "class_id": class_schedule_id,
            "member_id": member_id,
            "member_name": member_name,
            "instructor_id": instructor_id,
            "class_name": class_name,
            "rating": rating,
            "comment": comment,
            "date": datetime.now()
        }
        
        return self.evaluations.insert_one(evaluation).inserted_id
    
    def get_class_evaluation(self, user_id, class_schedule_id, member_id=None):
        # Try to find by user + class_schedule_id first
        qry = {"user_id": user_id, "class_schedule_id": class_schedule_id}
        found = self.evaluations.find_one(qry)
        if found:
            return found

        # Fallback: check by member_id + class_id (compatibility with older schema/index)
        if member_id is not None:
            try:
                found = self.evaluations.find_one({"member_id": member_id, "class_id": class_schedule_id})
                if found:
                    return found
            except Exception:
                pass

        return None
    
    def get_class_evaluations(self, class_schedule_id):

        return list(self.evaluations.find({"class_schedule_id": class_schedule_id}))
    
    def get_member_evaluations(self, user_id):

        return list(self.evaluations.find({"user_id": user_id}))
    
    def get_instructor_evaluations(self, instructor_id):
 
        return list(self.evaluations.find({"instructor_id": instructor_id}))
    
    def get_instructor_recent_evaluations(self, instructor_id, limit=4):

        return list(self.evaluations.find(
            {"instructor_id": instructor_id}
        ).sort("date", -1).limit(limit))
    
    def get_instructor_average_rating(self, instructor_id):

        evaluations = list(self.evaluations.find({"instructor_id": instructor_id}))
        
        if not evaluations:
            return 0
        
        total = sum(eval.get("rating", 0) for eval in evaluations)
        return round(total / len(evaluations), 2)

    def close(self):

        self.client.close()

