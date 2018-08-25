import uuid
import hashlib


class Hasher:

    def hash(self, to_hash):
        salt = self.get_id()
        # uuid is used to generate a random number
        salted = salt.encode() + to_hash.encode()

        digest = hashlib.sha256(salted).hexdigest()
        return digest, salt

    def check(self, hashed, salt, raw):

        return hashed == hashlib.sha256(
            salt.encode() + raw.encode()).hexdigest()

    def get_id(self):
        return uuid.uuid4().hex

    def secure_set(self):
        token = self.get_id()
        digest, salt = self.hash(token)
        return token, digest, salt

if __name__ == '__main__':

    hasher = Hasher()
    new_pass = hasher.get_id()
    print('The password is:', new_pass)
    hashed_password, salt = hasher.hash(new_pass)
    print('The string to store in the db is: ' + hashed_password)
    print('The salt is: ' + salt)
    old_pass = new_pass
    print('The password to check is :', old_pass)
    print("and the result is:", hasher.check(hashed_password, salt, old_pass))

