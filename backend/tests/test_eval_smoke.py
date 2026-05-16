from source_lens_api.config import Settings
from source_lens_api.eval_smoke import run_eval


def test_run_eval_uses_deterministic_default_path(tmp_path, capsys) -> None:
    settings = Settings(data_dir=tmp_path / ".local" / "source-lens")

    run_eval(settings)

    output = capsys.readouterr().out
    assert "eval case grounded_golden_path: ok" in output
    assert "eval case insufficient_evidence: ok" in output
    assert "ollama embedding: ok" not in output
    assert "ollama chat: ok" not in output
