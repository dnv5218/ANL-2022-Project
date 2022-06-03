import json
import time
from pathlib import Path

from utils.plot_trace import plot_trace
from utils.runners import run_session

RESULTS_DIR = Path("results", time.strftime('%Y%m%d-%H%M%S'))

if not RESULTS_DIR.exists():
    RESULTS_DIR.mkdir(parents=True)

a_yet_anoter = "agents.yet_another_agent.yet_another_agent.YetAnotherAgent"
a_boulware = "agents.boulware_agent.boulware_agent.BoulwareAgent"

settings = {"agents": [{"class": a_yet_anoter}, {"class": a_boulware}],
            "profiles": ["domains/domain26/profileA.json", "domains/domain26/profileB.json"],
            "deadline_time_ms": 10000}

session_results_trace, session_results_summary = run_session(settings)

if not session_results_trace["error"]:
    plot_trace(session_results_trace, RESULTS_DIR.joinpath("trace_plot.html"))

with open(RESULTS_DIR.joinpath("session_results_trace.json"), "w", encoding="utf-8") as f:
    f.write(json.dumps(session_results_trace, indent=2))
with open(RESULTS_DIR.joinpath("session_results_summary.json"), "w", encoding="utf-8") as f:
    f.write(json.dumps(session_results_summary, indent=2))
