import geocat.objfunc as objfunc
import metrics
from RecList import RecList
from Swarm import Swarm
from Particle import Particle
from random import randint

def local_max(tmp_rec_list, tmp_score_list, poi_cats, poi_neighbors, K, undirected_category_tree,
				rec_list, relevant_cats, log_poi_ids, log_neighbors, poi_cover, current_proportionality,
				div_geo_cat_weight, div_weight, final_scores):

	range_K = range(K)

	for i in range_K:
			#print(i)
			poi_to_insert=None
			max_objective_value=-200
			for j in range(len(tmp_rec_list)):
				candidate_poi_id=tmp_rec_list[j]
				candidate_score=tmp_score_list[j]
				ild_div=objfunc.min_dist_to_list_cat(candidate_poi_id,rec_list,poi_cats,undirected_category_tree)
				gc_div=objfunc.gc(candidate_poi_id,rec_list,relevant_cats,poi_cats)
				pr=objfunc.update_geo_cov(candidate_poi_id,log_poi_ids,K,poi_cover.copy(),poi_neighbors,log_neighbors[candidate_poi_id])

				objective_value=objfunc.ILD_GC_PR(candidate_score,ild_div,gc_div,pr,current_proportionality,K,div_geo_cat_weight,div_weight)
				#print(candidate_poi_id,ild_div,gc_div,max(0,pr-current_proportionality),objective_value)
				#print(candidate_poi_id,objective_value)

				if objective_value > max_objective_value:
					max_objective_value=objective_value
					poi_to_insert=candidate_poi_id
				pass
			if poi_to_insert is not None:
				#print(poi_to_insert,max_objective_value)

				rm_idx=tmp_rec_list.index(poi_to_insert)

				tmp_rec_list.pop(rm_idx)
				tmp_score_list.pop(rm_idx)
				rec_list.append(poi_to_insert)
				final_scores.append(max_objective_value)
				# remove from tmp_rec_list
				current_proportionality=objfunc.update_geo_cov(poi_to_insert,log_poi_ids,K,poi_cover,poi_neighbors,log_neighbors[poi_to_insert])
				#print(current_proportionality)
	
	return rec_list,final_scores

def tabu_search(tmp_rec_list, tmp_score_list, poi_cats, poi_neighbors, K, undirected_category_tree,
				relevant_cats, div_geo_cat_weight, div_weight, user_log):

	max_iteration = 100
	iteration = 0
	neighbour_number = 20
	list_size = K
	tabu_size = 100
	tabu_index = 0

	# div_geo_cat_weight = 0.75 # beta,this is here because of the work to be done on parameter customization for each user
	# div_weight = 0.5 # lambda, geo vs cat

	current_solution = RecList(list_size)
	best_solution = RecList(list_size)

	# Inicializa a solução inicial
	current_solution.create_from_base_rec(tmp_rec_list, tmp_score_list)
	# Calcula a função objetivo
	current_solution.fo = metrics.calculate_fo(current_solution, poi_cats, undirected_category_tree,
						user_log, poi_neighbors, div_geo_cat_weight, div_weight, K, relevant_cats)
	
	# Inicializa a melhor solução
	best_solution.clone(current_solution)

	# Cria a lista tabu
	tabu_list = []
	# Adiciona a solução inicial à lista tabu
	tabu_list.append(current_solution)

	while iteration < max_iteration:
		# Gera o primeiro vizinho
		new_solution = current_solution.create_neighbour(tmp_rec_list, len(tmp_rec_list), tmp_score_list)
		
		# Gera os outros n-1 vizinhos
		for i in range(neighbour_number-1):
			neighbour_solution = current_solution.create_neighbour(tmp_rec_list, len(tmp_rec_list), tmp_score_list)

			if  neighbour_solution not in tabu_list and (neighbour_solution.fo > new_solution.fo or new_solution in tabu_list):
				# Atualiza o melhor vizinho
				new_solution.clone(neighbour_solution)
				
		# Calcula-se a função objetiva de ambas as soluções e mantêm-se a melhor:
		if new_solution not in tabu_list and new_solution.fo > current_solution.fo:

			current_solution.clone(new_solution) # Substitui
			tabu_list[tabu_index] = current_solution # Adiciona à lista tabu

			if tabu_index == tabu_size-1:
				tabu_index = 0
			else:
				tabu_index += 1
			
			if current_solution.fo > best_solution.fo:
				# Atualiza a melhor
				best_solution.clone(current_solution)
	
		iteration += 1

	# A melhor solução está em best_solution, agora não sei o que fazer para completar o processo de diversificação
	return best_solution.get_result()

def pso_roulette_shuffle(roulette_list, roulette_size):
	for i in range(roulette_size):
		r = randint(roulette_size)
		temp = roulette_list[i]
		roulette_list[i] = roulette_list[r]
		roulette_list[r] = temp

def pso_roulette(w, c1, c2):
	roulette_list = []
	t1 = w * 10
	t2 = c1 * 10
	t3 = 10 - (t1 + t2)

	for i in range(t1):
		roulette_list.append(1)
	
	for i in range(t2):
		roulette_list.append(2)

	for i in range(t3):
		roulette_list.append(3)

	pso_roulette_shuffle(roulette_list, len(roulette_list))
	roulette_position = randint(10)
	return roulette_list[roulette_position]

def particle_swarm(tmp_rec_list, tmp_score_list, poi_cats, poi_neighbors, K, undirected_category_tree,
				relevant_cats, div_geo_cat_weight, div_weight, user_log):
	
	swarm_size = 30
	particle_size = 10
	base_rec_size = K
	iteration = 0
	max_iteration = 100

	# Global best solution
	global_best = RecList(particle_size)
	
	# Best diversity
	dbest = RecList(particle_size)

	# Particle swarm
	swarm = Swarm(swarm_size)
	swarm.create_particles(tmp_rec_list, tmp_score_list, particle_size, base_rec_size)

	# Calculate local best for each particle and global best
	for i in range(swarm_size):

		metrics.pso_calculate_fo(swarm[i], poi_cats, undirected_category_tree, user_log, poi_neighbors,
								div_geo_cat_weight, div_weight, K, relevant_cats, dbest)

		# Update global best
		if (global_best.fo < swarm[i].best_fo):
			global_best.clone_particle(swarm[i])

	while iteration < max_iteration:
		gbest_position = -1

		for i in range(swarm_size):
			# Build particle from parents
			new_particle = Particle(particle_size)

			for i in range(particle_size):
				item_id = -1
				item_score = -1

				while item_id == -1 or item_id not in swarm[i]:
					particle_choice = pso_roulette(0.3, 0.3, 0.6)
					position = randint(10)
					
					if (particle_choice == 1):
						item_id = swarm[i].item_list[position]
						item_score = swarm[i].score_list[position]
					elif (particle_choice == 2):
						item_id = swarm[i].best_item_list[position]
						item_score = swarm[i].best_score_list[position]
					else:
						item_id = global_best.item_list[position]
						item_score = global_best.score_list[position]

				new_particle.add_item(item_id, item_score)
			
			swarm[i].clone(new_particle)

			# Calcule local best and global best
			metrics.pso_calculate_fo(swarm[i], poi_cats, undirected_category_tree, user_log, poi_neighbors,
									div_geo_cat_weight, div_weight, K, relevant_cats, dbest)
			# Update global best
			if (global_best.fo < swarm[i].best_fo):
				global_best.clone_particle(swarm[i])

		# Path relink function is not complete
		# global_best = path_Relink(gbest, gbestPos, dBest, swarm, hashFeature, numPreds, alfa, featureSize);
		iteration += 1

	return global_best.get_result()