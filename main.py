import json
import sys
import os

from multiprocessing import Process

from rabbitWrapper import Consumer, Producer
from reporters import HttpReporter, HttpReporterForDebug
from sensor import Sensor


reportingURL = "https://requestbin.com/r/en6msadu8lecg/sample/post/request/"
reporter = HttpReporter(reportingURL)

# use this reporter instead to see info of sent messages on the console
# reporter = HttpReporterForDebug(reportingURL)

def runConsumer():
    def reportSensorStatus(status):
        msg = str(status, encoding='utf-8')
        reporter.send(msg)
    
    consumer = Consumer()
    consumer.run(reportSensorStatus)

def runProducer(sensor):
    producer = Producer()
    while True:
        sensor.do_work()
        message = json.dumps(sensor.state)
        producer.send(message)

def main():
    consumerProcess = Process(target=runConsumer)
    consumerProcess.start() #run until killed, no join

    sensors = [Sensor(), Sensor()]

    for sensor in sensors:
        producerProcess = Process(target=runProducer, args=(sensor,))
        producerProcess.start() #run until killed, no join


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
