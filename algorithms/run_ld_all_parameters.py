import sys
import os
sys.path.insert(0, os.path.abspath('lib'))
from lib.RecRunner import RecRunner
import numpy as np
from lib.constants import experiment_constants
import inquirer

questions = [
  inquirer.List('city',
                    message="City to use",
                    choices=experiment_constants.CITIES,
                    ),
  inquirer.List('baser',
                    message="Base recommender",
                    choices=list(RecRunner.get_base_parameters().keys()),
                    ),
]

answers = inquirer.prompt(questions)
city = answers['city']
baser = answers['baser']


# rr=RecRunner("usg","geocat","madison",80,20,"/home/heitor/recsys/data")
# print(rr.get_base_rec_file_name())
# print(rr.get_final_rec_file_name())

# rr.load_base()
# rr.run_base_recommender()
# rr.run_final_recommender()

rr = RecRunner.getInstance(baser, "ld", city, 80, 10,
                           "/home/heitor/recsys/data")
rr.load_base()
rr.load_base_predicted()

lp = np.around(np.linspace(0, 1, 11),decimals=2)
for div_weight in lp:
    rr.final_rec_parameters['div_weight'] = div_weight
    rr.run_final_recommender(check_already_exists=True)
