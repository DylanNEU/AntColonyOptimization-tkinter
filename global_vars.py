import csv
import numpy as np

alpha = 1
beta = 2
rho = 0.5
q = 100
city_num = 34
ant_num = 40

pheromone_matrix = np.ones((city_num, city_num))
distance_matrix = np.zeros((city_num, city_num))

pos_x = []
pos_y = []
city_name = []

cities = []

with open("city.csv", mode="r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)  # csv中的第一行数据是表头，需要忽略
    for row in reader:
        city_name.append(str(row[0]))
        pos_x.append(float(row[1]))
        pos_y.append(float(row[2]))
        cities.append([float(row[1]), float(row[2])])


def get_distance_matrix(coord):
    n = coord.shape[0]  # shape[0]可以获取城市坐标矩阵的行数
    matrix = np.zeros((34, 34))  # 创建一个34*34的矩阵
    for i in range(n):
        for j in range(i, n):
            matrix[i][j] = np.linalg.norm(coord[i] - coord[j])
            matrix[j][i] = matrix[i][j]
    return matrix


coordinates = np.array(cities)
distance_matrix = get_distance_matrix(coordinates)
