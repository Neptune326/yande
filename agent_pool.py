import json


class AgentPool:
    def __init__(self):
        self.index = 0
        with open('agent.json', 'r', encoding='utf-8') as agent_file:
            agent_json = json.load(agent_file)
            self.json = agent_json

    def get(self):
        return self.json[self.index]

    def remove(self):
        self.json.pop(self.index)
        self.index = self.index + 1
