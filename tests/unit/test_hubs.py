from src.hubs import Bulletin, Secretary, Orchestrator


def test_bulletin_post_and_history():
    bulletin = Bulletin()
    bulletin.post({"agent": "a", "report": "r"})
    assert bulletin.history() == [{"agent": "a", "report": "r"}]


def test_secretary_handles_report():
    bulletin = Bulletin()
    secretary = Secretary(bulletin)
    entry = secretary.handle_report("agent", "data")
    assert entry == {"agent": "agent", "report": "data"}
    assert bulletin.history() == [entry]


def test_orchestrator_assign():
    orchestrator = Orchestrator()
    task = orchestrator.assign("agent", "do work")
    assert task in orchestrator.task_queue
    assert task["agent"] == "agent"
    assert task["task"] == "do work"
