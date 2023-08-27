import uuid

import hashlib


async def generate_random_data(len_data: int = 10000):
    data = {'id': [], 'data': []}

    for it, _ in enumerate(range(len_data)):
        random_hash = hashlib.sha256(uuid.uuid4().hex.encode()).hexdigest()
        data['id'].append(it)
        data['data'].append(random_hash)

    return data
