### HOW TO RUN

1. Download RabbitMQ Docker image: 
        `docker pull rabbitmq:3-management`

2. Start RabbitMQ: 
        `docker run --rm --name rabbitTest -it  -p 15679:15672 -p 5679:5672 rabbitmq:3-management`

3. Install Pika:
        `pip install pika`

4. Run main function (make sure rabbit is done with initialisation): 
        `python main.py`

5. Run tests:
        `python rabbitWrappper.test.py`
        `python reporters.test.py`


### SOLUTION

I decided to use RabbitMQ to send the sensors information using a queue.
The sensors send the message to the Rabbit queue, then that message is sent to
a worker that sends the message via http to the specified endpoint.

Rabbit resends the messages than haven't been acknowledged, 
and even recovers the pending messages if the Rabbit instance stops running and is restored later.


### CODE STRUCTURE

* **sensor.py**: Provided file with the implementation of a Sensor that sends information periodically

* **rabbitWrapper.py**: This is a wrapper for Pika (the python lib to use RabbitMQ).There two classes in this file:
  * **Producer**: is in charge of sending messages to the queue. 
                It is marked as persistent, which means that if Rabbit goes down, the pending messages won't be lost.
  * **Consumer**: This is the worker that receives messages and process them.
                We use a callback to specify what to do with the messages. 
                If the callback raises an exception the message will be marked as not processed and retried later (NACK)
                If the callback doesn't raise any exception we confirm eveything is fine and the message will be removed from the queue.
        
  The tests for these classes are more **integration test** rather than unit tests.
  I create a rabbit instance with docker and destroy it for every test, which is slow.
  An alternative would have been having a testing instance of rabbit, but I think this would be easier for you to run.

* **reporters.py**: This classes are the ones in charge of sending the information to wherever we need, in the
                case of this example, the http endoint, but there could also be a reporter to send the info to a file, or
                as the other example provided, a reporter that also logs information. 

* **main.py**: The main function creates several producers and a consumer, each one is run in a separate process.
           The producers are fed with the sensors information, and run indefinitely.
           The consumer is created specifying the reporter class we want to use, in this case it will send the data to the HTTP endpoint.
