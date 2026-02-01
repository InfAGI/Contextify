import os
import json


class Tracer:
    def __init__(self, path):
        self.path = path
        self.traces = []
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        open(self.path, "w", encoding="utf-8").close()

    def trace(self, trace):
        self.traces.append(trace)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(
                f"{len(self.traces)}: "
                + json.dumps(trace, ensure_ascii=False, indent=4)
                + "\n\n"
            )


if __name__ == "__main__":
    tracer = Tracer("./tracer/tracer.json")
    tracer.trace({"step": 1, "action": "think", "observation": "I am thinking"})
    tracer.trace({"step": 2, "action": "act", "observation": "I am acting"})
