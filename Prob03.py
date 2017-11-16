"""
Problem 3, Code Quest 2016 Practice
Ryan Drew, Kylan Coffey, Conner Tompson
"""

with open('Prob03.in.txt', 'r') as in_file:
    _num_problems = in_file.readline()
    for line in in_file.readlines():
        a, b, c = (int(_.strip()) for _ in line.strip().split(','))
        if a + b > c and a + c > b and b + c > a:
            # valid
            if a == b == c:
                print("Equilateral")
            elif a == b != c or b == c != a or c == a != b:
                print("Isosceles")
            else:
                print("Scalene")
        else:
            print("Not a Triangle")
