import pika
from datetime import datetime
import json
from Globals import RMQ_HOST, RMQ_USER, RMQ_PASS, EXCHANGE_NAME

LOG_FILE = 'rabbitmq_messages.log'


def setup_logging():
    with open(LOG_FILE, 'w') as f:
        f.write(f"=== Log started at {datetime.now().isoformat()} ===\n")


def log_message(message, message_type):
    try:
        timestamp = datetime.now().isoformat()

        if message_type == "original":
            number = message.get("number")
            publisher = message.get("publisher")
        else:
            number = message.get("result")
            publisher = message.get("from", "unknown")

        log_entry = f"[{timestamp}] {publisher} : {message_type} : {number}\n"
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
        print(log_entry.strip())
    except Exception as e:
        print(f"[!] Failed to log message: {e}")


# Final
def main():
    setup_logging()

    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=RMQ_HOST,
        credentials=pika.PlainCredentials(RMQ_USER, RMQ_PASS)
    ))
    channel = connection.channel()

    original_queue = channel.queue_declare(
        queue='', exclusive=True).method.queue
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=original_queue)

    channel.queue_declare(queue='squared', durable=True)
    channel.queue_declare(queue='cubed', durable=True)

    def original_callback(ch, method, properties, body):
        message = json.loads(body)
        log_message(message, "original")

    def squared_callback(ch, method, properties, body):
        message = json.loads(body)
        log_message(message, "squared")

    def cubed_callback(ch, method, properties, body):
        message = json.loads(body)
        log_message(message, "cubed")

    channel.basic_consume(queue=original_queue,
                          on_message_callback=original_callback, auto_ack=True)
    channel.basic_consume(
        queue='squared', on_message_callback=squared_callback, auto_ack=True)
    channel.basic_consume(
        queue='cubed', on_message_callback=cubed_callback, auto_ack=True)

    print('[*] Logger is waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(' [*] Logger stopped')
