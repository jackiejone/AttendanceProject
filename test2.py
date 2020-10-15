x = [5, 2, 5, 7, 9, 'a', 2, 'b', 'd', 'c', 5 , 10, 3, 9, 6, 3, 'a', 'b', 'e', 'f']

def sortKey(elem):
    return int(elem)

print(x.sort(key=sortKey))