from database import redis
import time


streams = {'order_completed': '>', 'refund_order': '>'}
group = 'notification-group'


for stream in streams:
    try:
        redis.xgroup_create(stream, group, mkstream=True)
    except:
        print(f'Group already exists for {stream}!')

print("Notification service started, waiting for events...")

while True:
    try:
        
        results = redis.xreadgroup(group, 'notification-worker', streams, count=1, block=5000)

        if results:
            for stream_name, messages in results:
                for message_id, message_data in messages:
                    if stream_name == 'order_completed':
                        print(f"--- OBAVEŠTENJE: Porudžbina {message_data['pk']} je USPEŠNO plaćena. ---")
                    elif stream_name == 'refund_order':
                        print(f"--- OBAVEŠTENJE: Izvršen je POVRAT novca za porudžbinu {message_data.get('pk', 'nepoznato')}. ---")
                    
                    
                    redis.xack(stream_name, group, message_id)
    except Exception as e:
        print(f"Notification Error: {e}")
    time.sleep(1)