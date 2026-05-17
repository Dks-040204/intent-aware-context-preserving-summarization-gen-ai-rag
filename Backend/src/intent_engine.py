"""
Intent-Aware Engine  (v2)
==========================
Drives genuinely different output per intent by combining:

  1. Pre-filtering  – sentence-level keyword scoring + section detection
  2. Prompt shaping – T5/BART-compatible instruction prefix per intent
  3. Level handling – executive / brief / detailed / bullets control length & format
  4. Post-processing – format, deduplicate, and label the raw model output
  5. Translation     – lightweight deep-translator for non-English output

Intent catalogue
----------------
technical_overview  High-level: what the system/paper does, key technologies
detailed_analysis   Deep-dive: methods, architecture, design decisions, equations
methodology         HOW: algorithm, pipeline, dataset, training, evaluation setup
results             WHAT was found: numbers, benchmarks, metrics, comparisons
conclusion          So what: conclusions, implications, limitations, future work
abstract            Compact academic abstract: problem → approach → result
"""

import re
import logging
from typing import List, Tuple, Dict, Optional

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Summary-level configuration
# ─────────────────────────────────────────────────────────────────────────────

LEVEL_CONFIG = {
    "executive": {"min_length": 20, "max_length": 60,  "num_beams": 3, "label": "Executive Summary"},
    "brief":     {"min_length": 50, "max_length": 130, "num_beams": 3, "label": "Brief Summary"},
    "detailed":  {"min_length": 100,"max_length": 280, "num_beams": 4, "label": "Detailed Summary"},
    "bullets":   {"min_length": 60, "max_length": 200, "num_beams": 4, "label": "Bullet Points"},
}
_DEFAULT_LEVEL = LEVEL_CONFIG["brief"]

# ─────────────────────────────────────────────────────────────────────────────
# Quality-mode → generation params
# ─────────────────────────────────────────────────────────────────────────────

QUALITY_CONFIG = {
    "speed":    {"num_beams": 2, "no_repeat_ngram_size": 2, "length_penalty": 1.0},
    "balanced": {"num_beams": 4, "no_repeat_ngram_size": 3, "length_penalty": 1.2},
    "quality":  {"num_beams": 6, "no_repeat_ngram_size": 3, "length_penalty": 1.5},
}
_DEFAULT_QUALITY = QUALITY_CONFIG["balanced"]

# ─────────────────────────────────────────────────────────────────────────────
# Intent configuration table
# ─────────────────────────────────────────────────────────────────────────────

INTENT_CONFIG: Dict[str, dict] = {
    "technical_overview": {
        "t5_prefix": "summarize the key technical contributions, system design, and core technologies: ",
        "focus_keywords": [
            "propose", "present", "introduce", "system", "framework", "architecture",
            "approach", "model", "method", "technique", "design", "develop", "built",
            "based on", "consists of", "leverages", "uses", "overview", "we propose",
            "this paper", "this work", "we present", "contribution", "novel",
        ],
        "section_priority": ["abstract", "introduction", "overview", "system", "contribution"],
        "label": "Technical Overview",
        "postprocess": "standard",
    },

    "detailed_analysis": {
        "t5_prefix": (
            "provide a comprehensive technical analysis covering the architecture, "
            "implementation details, design choices, and key algorithms: "
        ),
        "focus_keywords": [
            "layer", "encoder", "decoder", "attention", "network", "module",
            "equation", "formula", "parameter", "trained", "fine-tune", "embedding",
            "vector", "dimension", "kernel", "function", "optimization", "gradient",
            "loss", "activation", "transformer", "convolutional", "recurrent",
            "algorithm", "complexity", "implementation", "configuration",
            "mechanism", "architecture", "block", "head", "weight", "hidden",
        ],
        "section_priority": ["method", "approach", "model", "architecture", "implementation", "detail"],
        "label": "Detailed Technical Analysis",
        "postprocess": "detailed",
    },

    "methodology": {
        "t5_prefix": (
            "summarize the methodology, experimental setup, dataset used, "
            "training procedure, evaluation metrics, and pipeline: "
        ),
        "focus_keywords": [
            "dataset", "corpus", "training", "evaluation", "experiment", "setup",
            "pipeline", "procedure", "step", "process", "baseline", "split",
            "validation", "test", "train", "fine-tun", "pre-train", "annotation",
            "collect", "sample", "batch", "epoch", "hyperparameter", "learning rate",
            "benchmark", "protocol", "augmentation", "split", "fold", "cross-validation",
        ],
        "section_priority": ["method", "methodology", "experiment", "setup", "data", "training"],
        "label": "Methodology & Experimental Setup",
        "postprocess": "methodology",
    },

    "results": {
        "t5_prefix": (
            "summarize the experimental results, key quantitative findings, "
            "performance metrics, and comparisons with baselines: "
        ),
        "focus_keywords": [
            "result", "performance", "accuracy", "score", "f1", "bleu", "rouge",
            "precision", "recall", "achieves", "outperform", "beats", "surpass",
            "improves", "gain", "%", "percent", "state-of-the-art", "sota",
            "baseline", "comparison", "ablation", "demonstrate", "show",
            "table", "figure", "metric", "evaluation", "benchmark", "error rate",
            "recall", "map", "ndcg", "auc", "roc",
        ],
        "section_priority": ["result", "experiment", "evaluation", "performance", "finding", "ablation"],
        "label": "Results & Findings",
        "postprocess": "results",
    },

    "conclusion": {
        "t5_prefix": (
            "summarize the conclusions, key takeaways, limitations of the work, "
            "and potential future research directions: "
        ),
        "focus_keywords": [
            "conclude", "conclusion", "summary", "finding", "contribution",
            "implication", "limitation", "future", "direction", "work",
            "suggest", "recommend", "open problem", "challenge", "prospect",
            "overall", "in summary", "in conclusion", "we show", "we demonstrate",
            "our work", "this paper", "insight", "takeaway", "impact",
        ],
        "section_priority": ["conclusion", "summary", "discussion", "future", "limitation"],
        "label": "Conclusions & Implications",
        "postprocess": "conclusion",
    },

    "abstract": {
        "t5_prefix": (
            "write a concise abstract covering the problem statement, proposed approach, "
            "key results, and significance of the work: "
        ),
        "focus_keywords": [
            "propose", "present", "address", "problem", "challenge", "solution",
            "achieve", "result", "outperform", "significant", "novel",
            "contribution", "state-of-the-art", "demonstrate", "this paper",
            "we present", "we propose", "this work", "task", "application",
        ],
        "section_priority": ["abstract", "introduction", "conclusion"],
        "label": "Abstract",
        "postprocess": "abstract",
    },
}

_DEFAULT_INTENT = INTENT_CONFIG["technical_overview"]


# ─────────────────────────────────────────────────────────────────────────────
# Public config accessors
# ─────────────────────────────────────────────────────────────────────────────

def get_intent_config(intent: str) -> dict:
    return INTENT_CONFIG.get(intent, _DEFAULT_INTENT)

def get_level_config(level: str) -> dict:
    return LEVEL_CONFIG.get(level, _DEFAULT_LEVEL)

def get_quality_config(quality: str) -> dict:
    return QUALITY_CONFIG.get(quality, _DEFAULT_QUALITY)


# ─────────────────────────────────────────────────────────────────────────────
# Sentence utilities
# ─────────────────────────────────────────────────────────────────────────────

def _split_sentences(text: str) -> List[str]:
    raw = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in raw if len(s.strip()) > 25]


def _score_sentences(sentences: List[str], keywords: List[str]) -> List[Tuple[str, float]]:
    kw_lower = [k.lower() for k in keywords]
    scored = []
    for sent in sentences:
        sl = sent.lower()
        score = sum(1.5 if len(kw) > 6 else 1.0 for kw in kw_lower if kw in sl)
        scored.append((sent, score))
    return scored


def _detect_sections(text: str) -> Dict[str, str]:
    heading_re = re.compile(
        r"^(#{1,4}\s+.+|(?:abstract|introduction|background|related work|"
        r"methodology|method|approach|experiment|result|evaluation|"
        r"discussion|conclusion|limitation|future work|references)"
        r"[:\s]*$)",
        re.IGNORECASE | re.MULTILINE,
    )
    parts = heading_re.split(text)
    sections: Dict[str, str] = {}
    i = 0
    current = "body"
    while i < len(parts):
        part = parts[i].strip()
        if heading_re.match(part):
            current = part.lower().strip("#").strip()
            i += 1
            if i < len(parts):
                sections[current] = parts[i].strip()
                i += 1
        else:
            sections.setdefault(current, "")
            sections[current] += " " + part
            i += 1
    return {k: v.strip() for k, v in sections.items() if v.strip()}


# ─────────────────────────────────────────────────────────────────────────────
# Core pre-filtering
# ─────────────────────────────────────────────────────────────────────────────

def extract_intent_relevant_text(
    document: str,
    intent: str,
    max_chars: int = 3000,
) -> str:
    """
    Select the most intent-relevant sentences from the document.

    Strategy:
      1. Detect named sections and prioritise intent-relevant ones.
      2. Score every sentence against intent keywords.
      3. Take top-scoring sentences (preserving original order).
    """
    cfg = get_intent_config(intent)
    keywords: List[str] = cfg["focus_keywords"]
    section_priority: List[str] = cfg["section_priority"]

    sections = _detect_sections(document)

    # Pull high-priority section text first
    priority_text = ""
    for priority in section_priority:
        for sec_name, sec_text in sections.items():
            if priority in sec_name.lower():
                priority_text += " " + sec_text
                break

    all_text = (priority_text + " " + document).strip()
    sentences = _split_sentences(all_text)

    if not sentences:
        return document[:max_chars]

    scored = _score_sentences(sentences, keywords)
    sorted_scored = sorted(scored, key=lambda x: x[1], reverse=True)

    # Take at least 1/3 of sentences, never fewer than 6
    top_n = max(6, len(sentences) // 3)
    # Include all sentences that scored > 0 up to top_n
    top_set = {s for s, sc in sorted_scored[:top_n] if sc > 0}

    if not top_set:
        # Nothing scored — return the best section text or full text
        return (priority_text or all_text)[:max_chars]

    # Restore original order
    ordered = [s for s in sentences if s in top_set]
    result = " ".join(ordered)

    if len(result) > max_chars:
        result = result[:max_chars].rsplit(" ", 1)[0]

    logger.info(
        f"[IntentEngine] intent={intent}, total={len(sentences)}, "
        f"selected={len(ordered)}, chars={len(result)}"
    )
    return result or all_text[:max_chars]


# ─────────────────────────────────────────────────────────────────────────────
# T5 input construction
# ─────────────────────────────────────────────────────────────────────────────

def build_t5_input(filtered_text: str, intent: str) -> str:
    """Combine the intent-specific prefix with the pre-filtered text."""
    prefix = get_intent_config(intent)["t5_prefix"]
    return f"{prefix}{filtered_text}"


# ─────────────────────────────────────────────────────────────────────────────
# Post-processing
# ─────────────────────────────────────────────────────────────────────────────

def _clean_raw(text: str) -> str:
    """Basic cleanup: collapse whitespace and deduplicate sentences."""
    text = re.sub(r"\s{2,}", " ", text.strip())
    seen: set = set()
    deduped = []
    for sent in re.split(r"(?<=[.!?])\s+", text):
        key = sent.lower().strip()
        if key and key not in seen:
            seen.add(key)
            deduped.append(sent.strip())
    return " ".join(deduped)


def _to_bullets(text: str) -> str:
    """Convert a paragraph into a bullet-point list."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 15]
    if not sentences:
        return text
    return "\n".join(f"• {s}" for s in sentences)


def _to_numbered(text: str) -> str:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 15]
    if len(sentences) < 2:
        return text
    return "\n".join(f"{i+1}. {s}" for i, s in enumerate(sentences))


def postprocess_summary(raw_summary: str, intent: str, summary_level: str = "brief") -> str:
    """
    Apply intent + level specific post-processing to the raw model output.

    Modes (from intent):
      standard    → label + clean paragraph
      detailed    → label + longer clean paragraph
      methodology → numbered steps
      results     → metric highlighting with ►
      conclusion  → "In conclusion, …" framing
      abstract    → "This work …" academic framing

    Summary level overrides:
      bullets     → always convert to • bullet list
      executive   → trim to first 1-2 sentences
    """
    cfg = get_intent_config(intent)
    mode = cfg.get("postprocess", "standard")
    label = cfg["label"]

    summary = _clean_raw(raw_summary)

    # ── Bullets level overrides everything → convert to bullet list ──
    if summary_level == "bullets":
        summary = _to_bullets(summary)
        return f"[{label}]\n{summary}"

    # ── Executive level → very short, first 2 sentences max ──
    if summary_level == "executive":
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", summary) if s.strip()]
        summary = " ".join(sentences[:2])
        return f"[{label}]\n{summary}"

    # ── Intent-specific formatting ──
    if mode == "detailed":
        if summary and not summary[-1] in ".!?":
            summary += "."
        return f"[Detailed Analysis]\n{summary}"

    elif mode == "methodology":
        numbered = _to_numbered(summary)
        return f"[Methodology]\n{numbered}"

    elif mode == "results":
        # Highlight numbers and metric names
        highlighted = re.sub(
            r"(\d+\.?\d*\s*%|\b\d+\.\d+\b|\b(?:accuracy|f1|bleu|rouge|score|precision|recall|auc)[^.]*\d[^.]*\.?)",
            lambda m: f"► {m.group(0).strip()}",
            summary,
            flags=re.IGNORECASE,
        )
        return f"[Results & Findings]\n{highlighted}"

    elif mode == "conclusion":
        if not re.match(
            r"^(in conclusion|to conclude|overall|this (paper|work|study))",
            summary, re.IGNORECASE
        ):
            summary = "In conclusion, " + summary[0].lower() + summary[1:]
        return f"[Conclusions]\n{summary}"

    elif mode == "abstract":
        if not re.match(
            r"^(this (paper|work|study)|we (propose|present|introduce)|in this)",
            summary, re.IGNORECASE
        ):
            summary = "This work " + summary[0].lower() + summary[1:]
        return f"[Abstract]\n{summary}"

    else:  # standard / technical_overview
        return f"[{label}]\n{summary}"


# ─────────────────────────────────────────────────────────────────────────────
# Translation  (non-English output)
# ─────────────────────────────────────────────────────────────────────────────

# Map our language names → deep-translator language codes
_LANG_CODES = {
    "english":    "en",
    "spanish":    "es",
    "french":     "fr",
    "german":     "de",
    "italian":    "it",
    "portuguese": "pt",
    "chinese":    "zh-CN",
    "japanese":   "ja",
    "korean":     "ko",
    "arabic":     "ar",
    "hindi":      "hi",
    "russian":    "ru",
    "turkish":    "tr",
    "vietnamese": "vi",
    "thai":       "th",
}


def translate_summary(text: str, target_language: str) -> str:
    """
    Translate the English summary to the target language using deep-translator.
    Returns original text if target is English or translation fails.
    """
    lang = target_language.lower().strip()
    if lang in ("english", "en", ""):
        return text

    target_code = _LANG_CODES.get(lang)
    if not target_code:
        logger.warning(f"[Translation] Unknown language: {lang}, skipping translation")
        return text

    try:
        from deep_translator import GoogleTranslator
        # Split into chunks ≤ 4500 chars (API limit)
        chunks = _chunk_for_translation(text, max_chars=4500)
        translated_chunks = []
        translator = GoogleTranslator(source="en", target=target_code)
        for chunk in chunks:
            translated_chunks.append(translator.translate(chunk))
        result = " ".join(translated_chunks)
        logger.info(f"[Translation] Translated to {lang} ({len(result)} chars)")
        return result
    except ImportError:
        logger.warning("[Translation] deep-translator not installed. pip install deep-translator")
        return text
    except Exception as e:
        logger.error(f"[Translation] Failed: {e}")
        return text  # Graceful fallback to English


def _chunk_for_translation(text: str, max_chars: int = 4500) -> List[str]:
    """Split text into chunks that fit within the translation API limit."""
    if len(text) <= max_chars:
        return [text]
    sentences = re.split(r"(?<=[.!?\n])\s+", text)
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) + 1 > max_chars:
            if current:
                chunks.append(current.strip())
            current = s
        else:
            current = (current + " " + s).strip()
    if current:
        chunks.append(current.strip())
    return chunks
