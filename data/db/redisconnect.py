import redis
# Connect to the Redis server
password= 'r9CxvBNMLMKJMR631RCyN4z4ctUvxgeWJY1cgw3tPMzBd380+0Km7IL9fwoI4xW5AWRy8rYC9gIBJLH'
redis_client = redis.Redis(host='13.127.126.101', username='default',port=6379, password=password, decode_responses=True)
try:
    redis_client.ping()

    print("Connected to Redis!")
    keys = redis_client.keys("user:*")  # Example: Fetch keys matching the pattern "user:*"
    print(keys)
except redis.ConnectionError as e:
    print(f"Connection failed: {e}")
# Store a key-value pair
print(redis_client)
all_keys = redis_client.keys()
print(all_keys)
# Fetch data for each key
for key in all_keys:
    value = redis_client.get('key')
    print(f"Key: {key}, Value: {value}")

# Retrieve the value of the key
value = redis_client.get("upstox_db")
print(f"The value of 'name' is: {value}")