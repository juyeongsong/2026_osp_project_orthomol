import pyrebase
import json

class DBhandler:
    def __init__(self):
        with open('./authentication/firebase_auth.json') as f:
            config = json.load(f)
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

    def insert_item(self, name, data, img_path):
        item_info = {
            "seller": data['seller'],
            "addr": data['addr'],
            "price": data['price'],
            "status": data['status'],
            "email": data['email'],
            "img_path": img_path
        }
        self.db.child("item").child(name).set(item_info)
        return True
    
    def insert_user(self, data, pw):
        user_info = {
            "id": data['id'],
            "pw": pw,
            "nickname": data['nickname']
        }
        if self.user_duplicate_check(str(data['id'])):
            self.db.child("user").push(user_info)
            return True
        else:
            return False
        
    def user_duplicate_check(self, id_string):
        users=self.db.child("user").get()

        if str(users.val()) == "None":
            return True
        else: 
            for res in users.each():
                value = res.val()
                    
                if value['id'] == id_string:
                    return False
                
            return True
        
    def get_user_by_id(self, id_string):
        users = self.db.child("user").get()

        if str(users.val()) == "None":
            return None
        
        for res in users.each():
            value = res.val()

            if value["id"] == id_string:
                return value
            
        return None
    
    def get_items(self):
        return self.db.child("item").get().val()
    
    def get_item_byname(self, name):
        return self.db.child("item").child(name).get().val()

    # ---------- 후기 (Team Practice 1) ----------
    def insert_review(self, data, img_path):
        review_info = {
            "title": data["title"],
            "product": data["product"],
            "rating": data["rating"],
            "content": data["content"],
            "user_id": data["id"],
            "img_path": img_path
        }
        self.db.child("review").push(review_info)  # "review" 노드에 push()로 저장
        return True

    # ---------- 후기 목록 / 상세 / 좋아요 (Team Practice 2, 3) ----------
    def get_reviews(self):
        return self.db.child("review").get().val()

    def get_review_by_id(self, review_id):
        return self.db.child("review").child(review_id).get().val()

    def get_heart(self, user_id, review_id):
        liked = self.db.child("review_like").child(user_id).child(review_id).get().val()
        return liked == True

    def set_heart(self, user_id, review_id, liked):
        self.db.child("review_like").child(user_id).child(review_id).set(liked)
        return liked