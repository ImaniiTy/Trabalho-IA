def save(element, local):
	f = open(local , "w+")
	f.write(f"viewDistance = {int(element[0])}\n")
	f.write(f"reward_multiplier = {int(element[1])}\n")
	f.write(f"terminal_multiplier = {int(element[2])}\n")
	f.write(f"ship_amount = {int(element[3])}\n")
	f.write(f"maxHaliteToMove = {int(element[4])}\n")
	f.write(f'max_turn_to_spawn = {int(element[5])}\n')
	f.write(f'min_halite_multiplier = {int(element[6])}\n')
	f.write(f"maxHaliteToReturn = {element[7]}\n")
	f.write(f"death_penality = {int(element[8]) * -1}\n")
	f.write(f"enemy_multiplier = {int(element[9])}\n")
	f.write(f"objective_reward = {int(element[10])}\n")
	f.write(f"gamma = {int(element[11])/10}\n")
	f.close()

def save_result(b_v, b_o):
	f = open("result.txt", "w+")

	f.write(f'Order: {b_o}\n\n')
	f.write(f'MaxHalite: {b_v}\n\n')

	f.close


def log(best_value, best_order, b_v, b_o):
    f = open("log.txt", "w+")
    for i, element in enumerate(best_value):
        f.write(f'fitness: {best_value[i]}')
        f.write(f'pop: {best_order[i]}\n')

    save_result(b_v, b_o)
    save(b_o, "choi_yena/utils_/final_parameters.py")

    f.close()