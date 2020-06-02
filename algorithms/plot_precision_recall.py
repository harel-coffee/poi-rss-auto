import sys, os
sys.path.insert(0, os.path.abspath('lib'))
from lib.RecRunner import RecRunner, NameType
import inquirer
from lib.constants import experiment_constants

questions = [
  inquirer.List('city',
                    message="City to use",
                    choices=experiment_constants.CITIES,
                    ),
]

answers = inquirer.prompt(questions)
city = answers['city']

rr=RecRunner("usg","xxxx",city,80,20,"/home/heitor/recsys/data")
rr.load_metrics(base=True,name_type=NameType.PRETTY)
rr.plot_precision_recall()
for rec in ['geocat','persongeocat']:
    rr.final_rec = rec
    rr.load_metrics(base=False,name_type=NameType.PRETTY)
    rr.plot_precision_recall()
