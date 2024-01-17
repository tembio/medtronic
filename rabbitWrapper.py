import pika

rabbitURL = 'localhost'
rabbitPort = 5679

class Producer:
    def __init__(self, host=rabbitURL, port=rabbitPort, queue='states'):
        self._queue = queue
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host, port))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self._queue)
    
    def send(self, data):
        # save messages on disk if rabbit dies
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent)

        self.channel.basic_publish(exchange='',
                    routing_key=self._queue,
                    body=data,
                    properties=properties)

class Consumer:
    def __init__(self, host=rabbitURL, port=rabbitPort, queue='states'):
        self._queue = queue
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host, port))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self._queue)
    
    def run(self, callback, forever=True):
        def inner_callback(ch, method, properties, body):
            try:
                callback(body)
                ch.basic_ack(delivery_tag = method.delivery_tag)
            except:
                ch.basic_nack(delivery_tag = method.delivery_tag)
            finally:
                if not forever:
                    self.connection.close()
                
        # waits for message confirmation by default (auto_ack=False)
        self.channel.basic_consume(queue=self._queue, on_message_callback=inner_callback)
        self.channel.start_consuming()