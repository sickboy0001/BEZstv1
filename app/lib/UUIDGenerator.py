import uuid
import hashlib
from cryptography.fernet import Fernet
import base64

class UUIDGenerator:
    def __init__(self, secret_key):
        # Generate a Fernet key from the provided secret (or load an existing one)
        self.key = Fernet(secret_key)

    def generate_uuid(self, system_name, user_id, batch_id):
        data = f"{system_name}:{user_id}:{batch_id}".encode()
        encrypted_data = self.key.encrypt(data)
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def recover_data(self, identifier_uuid):
        try:
            encrypted_data = base64.urlsafe_b64decode(identifier_uuid.encode())
            data = self.key.decrypt(encrypted_data).decode()
            system_name, user_id, batch_id = data.split(":")
            return system_name, user_id, batch_id
        except Exception as e:
            print(f"Error recovering data: {e}")
            return None, None, None

# # Example Usage:
# # Securely generate or load a secret key and store it safely.
# secret_key = Fernet.generate_key()
# # Convert the key to a string that can be stored
# secret_key_string = secret_key.decode()
# print(f"Your secret key is: {secret_key_string}")

# # Initialize UUIDGenerator with the secret key
# generator = UUIDGenerator(secret_key)

# # Example data
# system_name = "zerosecond-typo"
# user_id = str(uuid.uuid4())  # Generating a random UUID for the user
# batch_id = 12345

# # Generate UUID
# identifier_uuid = generator.generate_uuid(system_name, user_id, batch_id)
# print(f"Generated UUID: {identifier_uuid}")

# # Recover data from UUID
# recovered_system_name, recovered_user_id, recovered_batch_id = generator.recover_data(identifier_uuid)
# print(f"Recovered System Name: {recovered_system_name}")
# print(f"Recovered User ID: {recovered_user_id}")
# print(f"Recovered Batch ID: {recovered_batch_id}")