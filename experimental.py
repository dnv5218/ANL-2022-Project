import json
import time
from pathlib import Path

#from utils.plot_trace import plot_trace
from utils.experimental_plotter import experimental_plotter
from utils.runners import run_session

#Experiment Agent vs Available Agents
a_experiment = "agents.experiment_agent.experiment_agent.ExperimentAgent"
#available agents:
#boulware, conceder, hardliner, linear, random, stupid
a_boulware = "agents.boulware_agent.boulware_agent.BoulwareAgent"
a_conceder = "agents.conceder_agent.conceder_agent.ConcederAgent"
a_hardliner = "agents.hardliner_agent.hardliner_agent.HardlinerAgent"
a_linear = "agents.linear_agent.linear_agent.LinearAgent"
a_random = "agents.random_agent.random_agent.RandomAgent"
a_stupid = "agents.stupid_agent.stupid_agent.StupidAgent"

agents = [a_boulware, a_conceder, a_hardliner, a_linear, a_random, a_stupid]
for i in range(len(agents)):
    RESULTS_DIR = Path("results/experimental", str(i))
    # create results directory if it does not exist
    if not RESULTS_DIR.exists():
        RESULTS_DIR.mkdir(parents=True)
    settings = {"agents": [{"class": agents[i]}, {"class": a_experiment}],
                "profiles": ["domains/domain00/profileA.json", "domains/domain00/profileB.json"],
                "deadline_time_ms": 10000}
    session_results_trace, session_results_summary = run_session(settings)
    # plot trace to html file
    if not session_results_trace["error"]:
        experimental_plotter(session_results_trace)
    # write results to file
    #with open(RESULTS_DIR.joinpath("session_results_trace.json"), "w", encoding="utf-8") as f:
        #f.write(json.dumps(session_results_trace, indent=2))
    #with open(RESULTS_DIR.joinpath("session_results_summary.json"), "w", encoding="utf-8") as f:
        #f.write(json.dumps(session_results_summary, indent=2))




