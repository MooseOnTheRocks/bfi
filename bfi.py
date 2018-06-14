# bfi.py

class Memory:
    def __init__(self):
        self._id = 0
        self._data = {}
    
    def segments(self):
        keys = sorted(self._data, key=self._data.get)
        segs = [self._data[key] for key in keys]
        return segs
    
    def new_id(self):
        id = self._id
        self._id += 1
        return id
    
    def alloc(self, size):
        # If there is no allocated data,
        # just allocate from 0
        if not self._data:
            id = self.new_id()
            self._data[id] = (0, size - 1)
            return id
        
        segs = self.segments()
        deltas = [(index, c - b - 1) for index, ((_, b), (c, _)) in enumerate(zip(segs[:-1], segs[1:]))]
        start = 0
        for index, gap in deltas:
            if gap < size:
                continue
            _, start = segs[index]
            start += 1
            break
        else:
            # No gap found in memory
            # Allocate from the end
            _, start = segs[-1]
            start += 1
        id = self.new_id()
        self._data[id] = (start, start + size - 1)
        return id
    
    def dealloc(self, var):
        del self._data[var]

class Context:
    def __init__(self):
        self._mem = Memory()
        self._stack = [[]]
        self._code = ""
        self._ptr = 0
        self._names = {}
        
    def print_(self, dest):
        self._goto(dest)
        self._code += "."
    
    def input_(self, dest):
        self._goto(dest)
        self._code += ","
    
    def zero(self, dest):
        self._goto(dest)
        self._code += "[-]"
    
    def add(self, value, dest):
        if value == 0:
            return
        self._goto(dest)
        if value > 0:
            self._code += "+" * value
        elif value < 0:
            self._code += "-" * abs(value)
    
    def move(self, from_, to):
        self._goto(from_)
        self._code += "["
        self.add(1, to)
        self.add(-1, from_)
        self._code += "]"
        self._goto(to)
    
    def new_var(self, name):
        if name in self._names:
            raise KeyError(f"Variable name {name} already declared")
        id = self._mem.alloc(1)
        self._names[name] = id
        self._stack[-1].append(id)
    
    def _goto(self, name):
        delta = self._names[name] - self._ptr
        self._ptr += delta
        if delta < 0:
            self._code += abs(delta) * "<"
        elif delta > 0:
            self._code += delta * ">"
    
    def _push(self):
        self._stack.append([])
    
    def _pop(self):
        if len(self._stack) <= 1:
            raise RuntimeError("Pop on empty memory stack.")
        for id in self._stack.pop():
            self._mem.dealloc(id)

def codegen(ops):
    ctx = Context()
    ctx.new_var("a")
    ctx.new_var("b")
    ctx.zero("a")
    ctx.add(10, "a")
    ctx.zero("b")
    ctx.add(20, "b")
    ctx.move("b", "a")
    ctx.move("a", "b")
    print(ctx._code)