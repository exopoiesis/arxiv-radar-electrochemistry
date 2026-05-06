"""Tests for tools/filter_corpus.py — apply relevance filter locally."""
import json
import sys

import pytest


def test_is_relevant_paper_direct_domain():
    import filter_corpus
    assert filter_corpus.is_relevant_paper("This paper studies mackinawite iron sulfide surfaces.")


def test_is_relevant_paper_method_plus_domain():
    import filter_corpus
    assert filter_corpus.is_relevant_paper("We use density functional theory for iron sulfide surfaces.")


def test_is_relevant_paper_gnn_plus_domain():
    import filter_corpus
    assert filter_corpus.is_relevant_paper("Electrochemical CO2 reduction on sulfide catalysts.")


def test_is_relevant_paper_llm_plus_domain():
    import filter_corpus
    assert filter_corpus.is_relevant_paper("Constant potential DFT for an electrochemical interface.")


def test_is_relevant_paper_surrogate_plus_domain():
    import filter_corpus
    assert filter_corpus.is_relevant_paper("Electrochemical impedance spectroscopy for sulfide electrodes.")


def test_is_relevant_paper_domain_llm():
    """LLM paper that is actually about the target domain passes the filter."""
    import filter_corpus
    text = "We model an electrochemical membrane reactor for CO2 reduction."
    assert filter_corpus.is_relevant_paper(text)


def test_is_not_relevant_paper_pure_ml():
    """Pure ML/CS paper that mentions LLMs but no domain context fails."""
    import filter_corpus
    text = "We propose a Large Language Model for code generation tasks."
    assert not filter_corpus.is_relevant_paper(text)


def test_is_not_relevant_paper_robotics():
    import filter_corpus
    text = "Diffusion models for robot motion planning in cluttered environments."
    assert not filter_corpus.is_relevant_paper(text)


def test_is_not_relevant_paper_image():
    import filter_corpus
    text = "Generative adversarial networks for high-resolution image synthesis."
    assert not filter_corpus.is_relevant_paper(text)


def test_is_relevant_paper_empty_abstract():
    import filter_corpus
    assert not filter_corpus.is_relevant_paper("")


def test_is_relevant_paper_no_false_positive_on_subword():
    """Domain terms do not match as arbitrary unrelated subwords."""
    import filter_corpus
    assert not filter_corpus.is_relevant_paper("Random text about networks and graphs.")
    assert not filter_corpus.is_relevant_paper("This is anotherdomainterm without boundaries.")


def test_filter_corpus_writes_kept_papers(isolated_data_dir):
    """filter_corpus.run reads data/papers-*.json, writes to out_dir keeping
    only relevant papers."""
    import filter_corpus
    import data_io
    domain_paper = {
        "title": "Domain model", "first_author": "A", "authors": ["A"],
        "abstract": "We use density functional theory for iron sulfide surfaces.",
        "primary_category": "cond-mat.mtrl-sci",
        "categories": ["cond-mat.mtrl-sci"],
        "published": "2025-04-01", "updated": "2025-04-05",
        "comment": None, "pdf_url": "http://arxiv.org/pdf/2504.00100",
        "topics": ["Example Topic"], "tags": [],
    }
    noise_paper = {
        "title": "LLM for code", "first_author": "B", "authors": ["B"],
        "abstract": "We use Large Language Models for code completion in IDEs.",
        "primary_category": "cs.LG", "categories": ["cs.LG"],
        "published": "2025-04-10", "updated": "2025-04-12",
        "comment": None, "pdf_url": "http://arxiv.org/pdf/2504.00200",
        "topics": ["Large Language Models & Materials"], "tags": [],
    }
    by_month = {"2025-04": {"2504.00100": domain_paper, "2504.00200": noise_paper}}
    data_io.save_month(by_month, "2025-04")

    out_dir = isolated_data_dir.root / "data_filtered"
    stats = filter_corpus.run(out_dir=out_dir)

    assert stats["kept"] == 1
    assert stats["dropped"] == 1
    out_file = out_dir / "papers-2025-04.json"
    assert out_file.exists()
    kept = json.loads(out_file.read_text(encoding="utf-8"))
    assert "2504.00100" in kept
    assert "2504.00200" not in kept


def test_filter_corpus_stats_per_topic(isolated_data_dir):
    """Stats report dropped count per topic — useful to see which topic is noisy."""
    import filter_corpus
    import data_io
    base = {
        "title": "x", "first_author": "x", "authors": ["x"],
        "abstract": "We propose a Large Language Model for code generation.",
        "primary_category": "cs.LG", "categories": ["cs.LG"],
        "published": "2025-04-01", "updated": "2025-04-05",
        "comment": None, "pdf_url": "http://arxiv.org/pdf/x",
        "tags": [],
    }
    by_month = {"2025-04": {
        "p1": {**base, "topics": ["Topic A"]},
        "p2": {**base, "topics": ["Topic A"]},
        "p3": {**base, "topics": ["Topic B"]},
    }}
    data_io.save_month(by_month, "2025-04")

    out_dir = isolated_data_dir.root / "data_filtered"
    stats = filter_corpus.run(out_dir=out_dir)

    assert stats["dropped_by_topic"]["Topic A"] == 2
    assert stats["dropped_by_topic"]["Topic B"] == 1
