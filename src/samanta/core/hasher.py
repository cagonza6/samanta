import uuid
import hashlib


class Hasher:
    """Simple warapper for the package 'hashlib' in order to generate
    cryptographic secure data that is used in confirmations that use links sent
    to the suers.

    The complete idea is based on 3 values:
    * raw: value desired to be secured
    * salt: used to add randomness to row
    * digest: value generated with raw and salt. For this idea to make sense,
      the server has to keep two values in any combination, but raw and salt at
      the same time. 

    In other words the server can keep:
    * salt and digest and send the raw to the user
    * raw an digest while sending the salt to the user

    But never keep raw and salt, since those two values are used to be sent to
    are used to generate the digest. In this way not the server ot the user are
    able to get the value of the counterpart. Just by working together they can
    check if the values match.

    >>> hasher = Hasher()
    >>> raw, digest, _salt = hasher.secure_set()
    >>> hasher.check(digest, _salt, raw)
    True
    >>> hasher.check(digest.upper(), _salt, raw)
    False
    >>> hasher.check(digest[:-1], _salt, raw)
    False
    >>> hasher.check(digest, _salt[:-1], raw)
    False
    >>> hasher.check(digest, _salt, raw[-1])
    False

    """

    def get_id(self):
        """ Wrapper for 'uuid.uuid4' it generates a cryptographic secure id
        with a decent Entropy

        :return: str
        """
        return uuid.uuid4().hex

    def hash(self, seed):
        """Takes the given input and generates a secure _salt and digested hash

        :param seed: str: string to encrypt
        :return: tuple
        """
        _salt = self.get_id()
        # uuid is used to generate a random number
        salted = _salt.encode() + seed.encode()

        digest = hashlib.sha256(salted).hexdigest()
        return digest, _salt

    def check(self, digested, _salt, raw):
        """Checks if the raw input and salt can be used to generate the digested

        :param digested: str: already processed value
        :param _salt: str: value used to add entropy to the raw value
        :param raw: str: original value

        :return: bool: True if the triad is valid, False if not
        """

        return digested == hashlib.sha256(
            _salt.encode() + raw.encode()).hexdigest()

    def secure_set(self):
        """Generates a set of three values to be used as keys.
        * token: corresponds to a secure id
        * salt: same as token, but different value
        * digest: is the result of the hashing process using the salt and token

        :return: tuple of strings
        """
        raw = self.get_id()
        digest, _salt = self.hash(raw)
        return raw, digest, _salt


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

