import random

lst = [random.randint(0, 100) for _ in range(100000)]
print(sum(lst) / len(lst))
