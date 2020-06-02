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
]

answers = inquirer.prompt(questions)
city = answers['city']

rr = RecRunner.getInstance("geosoca", "geocat", city, 80, 10,
                           "/home/heitor/recsys/data")
rr.load_base()

lp = np.around(np.linspace(0, 1, 11),decimals=2)
for alpha in lp:
    rr.base_rec_parameters['alpha'] = alpha
    rr.load_base_predicted()
    rr.eval_rec_metrics(base=True,METRICS_KS=[10])
