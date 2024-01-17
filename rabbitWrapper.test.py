import random
import subprocess
import time
import unittest
import requests
from rabbitWrapper import Consumer, Producer

class TestRabbitWrapper(unittest.TestCase):
    
    def setUp(self):
        self.testQueueName = "test"
        self.testPorts = {"portal":15690, "api": 5690}
        self.testContainerName = "rabbitWrapperTest"
        self.processes = []

        self.run_docker_cmd("run", self.testContainerName, self.testPorts)

    def tearDown(self):
        self.run_docker_cmd("remove", self.testContainerName, self.testPorts)
        for process in self.processes:
            process.wait()

        

    def test_consumer_runs_callback(self):
        TestRabbitWrapper.sentData = ""
        message = str(random.randint(1,30))
        producer = Producer(queue=self.testQueueName, port=self.testPorts["api"])
        consumer = Consumer(queue=self.testQueueName, port=self.testPorts["api"])

        def callback(received_data):
            TestRabbitWrapper.sentData = str(received_data, encoding='utf-8')

        producer.send(message)
        consumer.run(callback= callback, forever= False)

        self.assertEqual(TestRabbitWrapper.sentData, message)
        

    def test_message_resent_when_exception_happens_in_callback(self):
        TestRabbitWrapper.sentData = ""
        TestRabbitWrapper.counter = 0
        num_attempts = 3
        message = str(random.randint(0, 10000))

        def callback(received_data):
            if TestRabbitWrapper.counter < num_attempts:
                TestRabbitWrapper.counter += 1
                raise Exception
            
            TestRabbitWrapper.sentData = str(received_data, encoding='utf-8')


        producer = Producer(queue=self.testQueueName, port=self.testPorts["api"])
        producer.send(message)

        for i in range(num_attempts + 1):
            consumer = Consumer(queue=self.testQueueName, port=self.testPorts["api"])
            consumer.run(callback= callback, forever= False)
        
        self.assertEqual(TestRabbitWrapper.sentData, message)
    

    def test_message_persits_after_shutdown(self):
        message = str(random.randint(1,20))    

        def callback(received_data):
            TestRabbitWrapper.sentData = str(received_data, encoding='utf-8')

        producer = Producer(queue=self.testQueueName, port=self.testPorts["api"])
        producer.send(message)

        # Restart rabbit
        self.run_docker_cmd("stop", self.testContainerName, self.testPorts)
        self.run_docker_cmd("run", self.testContainerName, self.testPorts)

        consumer = Consumer(queue=self.testQueueName, port=self.testPorts["api"])
        consumer.run(callback= callback, forever= False)

        self.assertEqual(TestRabbitWrapper.sentData, message)




    def run_docker_cmd(self, cmdName, containerName, ports):
        match cmdName:
            case 'run':
                createContainerCmd = f'docker run --name {containerName} -it -p {ports["portal"]}:15672 -p {ports["api"]}:5672 rabbitmq:3-management'
                p = subprocess.Popen(createContainerCmd.split(" "), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                self.processes.append(p)
                wait_until_rabbit_ready(ports["portal"])
            case 'stop':
                restartContainerCmd = f'docker exec -it {containerName} sh -c "rabbitmqctl stop"'
                subprocess.call(restartContainerCmd.split(" "), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            case 'remove':
                subprocess.call(f"docker stop {containerName}".split(" "))
                subprocess.call(f"docker rm {containerName}".split(" "))

        
def wait_until_rabbit_ready(port):
        attempts = 10
        while attempts:
            time.sleep(5)
            try:
             resp = requests.get(f"http://localhost:{port}")
             if resp.status_code == 200:
                break
            except:
              attempts-=1

if __name__ == '__main__':
    unittest.main()