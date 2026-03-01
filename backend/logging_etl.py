"""Sophisticated error handling, structured logging, and ETL pipeline.

Usage
-----
    from backend.logging_etl import get_logger, ArbLogger, ReportWriter, ETLPipeline

``get_logger``
    Returns a standard :class:`logging.Logger` configured for structured JSON
    output and optional file rotation.  Drop-in replacement for
    ``logging.getLogger(name)``.

``ArbLogger``
    Higher-level structured event logger that writes newline-delimited JSON
    (JSONL) to a configurable directory.  Each log file is named
    ``arb_<date>.jsonl`` for easy aggregation.  Call :meth:`log_event` for
    normal events and :meth:`log_error` to capture exception details.

``ReportWriter``
    Writes JSON reports to a configurable directory.  Each report is stamped
    with the report name and generation timestamp so reports can be versioned
    and fed directly into downstream AI models.

``ETLPipeline``
    Lightweight Extract-Transform-Load pipeline for listing/comp records.

    * **Extract** – accepts an in-memory list of dicts.
    * **Transform** – normalises prices, strips empty fields, annotates
      each record with a ``_processed_at`` timestamp.
    * **Load** – writes a JSON summary report to *output_dir* and returns
      a result dict containing aggregated statistics.

All components are designed to be non-blocking and fail-safe: errors during
logging or report writing are caught and printed to stderr rather than
propagating to the caller.
"""

from __future__ import annotations

import datetime
import json
import logging
import logging.handlers
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

# ---------------------------------------------------------------------------
# Standard logging helper
# ---------------------------------------------------------------------------


class _JSONFormatter(logging.Formatter):
    """Emit each log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        payload: Dict[str, Any] = {
            "ts": datetime.datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack_info"] = self.formatStack(record.stack_info)
        return json.dumps(payload, ensure_ascii=False)


def get_logger(
    name: str,
    *,
    level: int = logging.INFO,
    log_dir: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
) -> logging.Logger:
    """Return a structured JSON logger.

    Parameters
    ----------
    name:
        Logger name (typically ``__name__``).
    level:
        Logging level (default ``INFO``).
    log_dir:
        If provided, logs are also written to a rotating file in this
        directory.  Falls back to ``output/logs`` if that directory exists,
        otherwise logs to *stderr* only.
    max_bytes:
        Maximum size of each rotating log file.
    backup_count:
        Number of backup log files to keep.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(level)
    formatter = _JSONFormatter()

    # Always add a stderr handler
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)

    # Optionally add a rotating file handler
    resolved_log_dir: Optional[Path] = None
    if log_dir:
        resolved_log_dir = Path(log_dir)
    else:
        candidate = Path(__file__).parent.parent / "output" / "logs"
        if candidate.exists():
            resolved_log_dir = candidate

    if resolved_log_dir is not None:
        resolved_log_dir.mkdir(parents=True, exist_ok=True)
        log_file = resolved_log_dir / f"{name.replace('.', '_')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# ---------------------------------------------------------------------------
# ArbLogger — structured JSONL event logger
# ---------------------------------------------------------------------------


class ArbLogger:
    """Write structured events to newline-delimited JSON log files.

    Parameters
    ----------
    log_dir:
        Directory where JSONL log files are written.  Created automatically
        if it does not exist.
    """

    def __init__(self, log_dir: str = "output/logs") -> None:
        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._buffer: List[str] = []

    def _log_path(self) -> Path:
        date_str = datetime.date.today().isoformat()
        return self._log_dir / f"arb_{date_str}.jsonl"

    def log_event(self, event: str, data: Dict[str, Any]) -> None:
        """Append a structured event record to the buffer.

        Parameters
        ----------
        event:
            A short string identifying the event type, e.g. ``"api_request"``.
        data:
            Arbitrary key/value payload.
        """
        record: Dict[str, Any] = {
            "ts": datetime.datetime.utcnow().isoformat() + "Z",
            "event": event,
            **data,
        }
        self._buffer.append(json.dumps(record, ensure_ascii=False))

    def log_error(
        self,
        context: str,
        exc: BaseException,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append a structured error record for *exc*.

        Parameters
        ----------
        context:
            Where the error occurred, e.g. ``"etl_transform"``.
        exc:
            The exception instance.
        extra:
            Optional additional key/value data to include in the record.
        """
        record: Dict[str, Any] = {
            "ts": datetime.datetime.utcnow().isoformat() + "Z",
            "event": "error",
            "context": context,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc(),
        }
        if extra:
            record.update(extra)
        self._buffer.append(json.dumps(record, ensure_ascii=False))

    def flush(self) -> None:
        """Write all buffered records to the JSONL log file."""
        if not self._buffer:
            return
        try:
            with self._log_path().open("a", encoding="utf-8") as fh:
                fh.write("\n".join(self._buffer) + "\n")
            self._buffer.clear()
        except OSError as exc:
            print(f"[ArbLogger] Failed to flush logs: {exc}", file=sys.stderr)

    def __del__(self) -> None:
        try:
            self.flush()
        except Exception:  # pragma: no cover
            pass


# ---------------------------------------------------------------------------
# ReportWriter — structured JSON report files
# ---------------------------------------------------------------------------


class ReportWriter:
    """Write versioned JSON reports to a directory.

    Each call to :meth:`write_report` produces a file named
    ``<report_name>_<timestamp>.json`` so reports accumulate without
    overwriting each other.

    Parameters
    ----------
    report_dir:
        Directory where report files are written.  Created automatically.
    """

    def __init__(self, report_dir: str = "output/reports") -> None:
        self._report_dir = Path(report_dir)
        self._report_dir.mkdir(parents=True, exist_ok=True)

    def write_report(self, report_name: str, data: Dict[str, Any]) -> Path:
        """Write *data* to a timestamped JSON file.

        Parameters
        ----------
        report_name:
            Logical name for the report (used in the filename and embedded in
            the JSON envelope).
        data:
            Arbitrary data to include in the report body.

        Returns
        -------
        Path
            The path to the written report file.
        """
        ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        filename = f"{report_name}_{ts}.json"
        out_path = self._report_dir / filename

        envelope: Dict[str, Any] = {
            "report_name": report_name,
            "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
            "data": data,
        }
        try:
            out_path.write_text(
                json.dumps(envelope, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except OSError as exc:
            print(f"[ReportWriter] Failed to write report '{report_name}': {exc}", file=sys.stderr)
        return out_path


# ---------------------------------------------------------------------------
# ETLPipeline — Extract / Transform / Load
# ---------------------------------------------------------------------------


class ETLPipeline:
    """Lightweight ETL pipeline for ArbFinder listing/comp records.

    Parameters
    ----------
    output_dir:
        Directory where transformed records and summary reports are written.
    """

    def __init__(self, output_dir: str = "output/reports") -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._report_writer = ReportWriter(report_dir=str(self._output_dir))
        self._logger = ArbLogger(log_dir=str(self._output_dir))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        records: List[Dict[str, Any]],
        report_name: str = "etl_report",
    ) -> Dict[str, Any]:
        """Execute the full Extract → Transform → Load cycle.

        Parameters
        ----------
        records:
            List of raw record dicts (e.g. listing rows from SQLite).
        report_name:
            Base name for the output report file.

        Returns
        -------
        dict
            ``{"status": "ok", "records_processed": N, "summary": {...}}``
            on success, or ``{"status": "error", "error": "..."}`` on failure.
        """
        try:
            extracted = self._extract(records)
            transformed = self._transform(extracted)
            summary = self._load(transformed, report_name)
            self._logger.log_event(
                "etl_complete",
                {"report_name": report_name, "records": len(transformed)},
            )
            self._logger.flush()
            return {
                "status": "ok",
                "records_processed": len(transformed),
                "summary": summary,
            }
        except Exception as exc:  # pragma: no cover
            self._logger.log_error("etl_pipeline", exc, {"report_name": report_name})
            self._logger.flush()
            return {"status": "error", "error": str(exc)}

    # ------------------------------------------------------------------
    # Internal stages
    # ------------------------------------------------------------------

    def _extract(self, records: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract stage: return records as a mutable list."""
        return [dict(r) for r in records]

    def _transform(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform stage: normalise and annotate each record."""
        out: List[Dict[str, Any]] = []
        ts_now = datetime.datetime.utcnow().isoformat() + "Z"
        for rec in records:
            # Remove None/empty string fields
            cleaned = {k: v for k, v in rec.items() if v is not None and v != ""}
            # Normalise price to float
            if "price" in cleaned:
                try:
                    cleaned["price"] = float(cleaned["price"])
                except (TypeError, ValueError):
                    cleaned["price"] = 0.0
            # Add processing timestamp
            cleaned["_processed_at"] = ts_now
            out.append(cleaned)
        return out

    def _load(
        self,
        records: List[Dict[str, Any]],
        report_name: str,
    ) -> Dict[str, Any]:
        """Load stage: write summary report and return aggregated statistics."""
        prices = [r["price"] for r in records if "price" in r and r["price"] > 0]
        sources: Dict[str, int] = {}
        for r in records:
            src = r.get("source", "unknown")
            sources[src] = sources.get(src, 0) + 1

        summary: Dict[str, Any] = {
            "total_records": len(records),
            "sources": sources,
            "price_stats": {
                "count": len(prices),
                "min": round(min(prices), 2) if prices else None,
                "max": round(max(prices), 2) if prices else None,
                "avg": round(sum(prices) / len(prices), 2) if prices else None,
            },
        }

        self._report_writer.write_report(
            report_name,
            {"summary": summary, "records": records},
        )
        return summary
