with open('Prob10.in.txt', 'r') as in_file:
    num_problems = in_file.readline()
    for prob in range(int(num_problems)):
        num_tot_time = in_file.readline()
        altitude_list = []
        elevation_list = []
        for time in range (int(num_tot_time)):
            altitude, elevation = [(int(_.strip())) for _ in in_file.readline().strip().split(',')]
            altitude_list.append(altitude)
            elevation_list.append(elevation)
        print(altitude_list)
        print(elevation_list)
        print("Low")
        for index in range(1,len(altitude_list) - 1):
            print(altitude_list[index + 1] + (altitude_list[index] - altitude_list[index - 1]))
            print(altitude_list[index] + altitude_list[index - 1], altitude_list[index + 1])
            print(altitude_list[index])
            print(elevation_list[index])
            if altitude_list[index + 1] + (altitude_list[index] - altitude_list[index - 1]) <= elevation_list[index]:
                print("Pull UP")
            elif altitude_list[index] <= 500:
                print("Low Altitude!")
            else:
                print("ok")
            print("\n")


























