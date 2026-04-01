import pika
import sys
import json

from Globals import RMQ_HOST, RMQ_USER, RMQ_PASS, EXCHANGE_NAME


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=RMQ_HOST,
        credentials=pika.PlainCredentials(RMQ_USER, RMQ_PASS)
    ))
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE_NAME,
                             exchange_type='fanout', durable=True)

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name)

    print('[*] Waiting for messages. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        message = json.loads(body)
        number = message["number"]
        publisher = message["publisher"]
        cubed = number ** 3

        result_msg = {
            "original": number,
            "result": cubed,
            "from": publisher
        }

        channel.basic_publish(
            exchange='',
            routing_key='cubed',
            body=json.dumps(result_msg),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        print(f"[x] Cubed {number} -> {cubed}")

    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(' [x] Cuber stopped')
        sys.exit(0)
