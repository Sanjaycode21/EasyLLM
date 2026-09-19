import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

class DatasetProcessor:
    """
    Validates, sanitizes, and splits datasets for training or knowledge ingestion.
    Enforces standard conversational JSONL format:
    {"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
    """
    @staticmethod
    def validate_and_parse_jsonl(file_path: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
        valid_records = []
        validation_errors = []
        
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for idx, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as e:
                    validation_errors.append(f"Line {idx}: Invalid JSON syntax ({str(e)})")
                    continue
                
                # Check for messages format
                if "messages" in record and isinstance(record["messages"], list):
                    msgs = record["messages"]
                    if len(msgs) < 2:
                        validation_errors.append(f"Line {idx}: 'messages' must contain at least 2 entries (user & assistant)")
                        continue
                    
                    has_user = any(m.get("role") == "user" and m.get("content") for m in msgs)
                    has_assistant = any(m.get("role") == "assistant" and m.get("content") for m in msgs)
                    
                    if not has_user or not has_assistant:
                        validation_errors.append(f"Line {idx}: 'messages' missing valid user or assistant turn")
                        continue
                    
                    valid_records.append({"messages": msgs})
                
                # Check for prompt / response or instruction / output format
                elif ("prompt" in record and "response" in record) or ("instruction" in record and "output" in record):
                    user_text = record.get("prompt") or record.get("instruction")
                    bot_text = record.get("response") or record.get("output")
                    if str(user_text).strip() and str(bot_text).strip():
                        valid_records.append({
                            "messages": [
                                {"role": "user", "content": str(user_text).strip()},
                                {"role": "assistant", "content": str(bot_text).strip()}
                            ]
                        })
                    else:
                        validation_errors.append(f"Line {idx}: Empty prompt or response")
                else:
                    validation_errors.append(f"Line {idx}: Unrecognized schema. Expected 'messages' or 'prompt'/'response' keys.")

        return valid_records, validation_errors

    @staticmethod
    def parse_csv_to_chat(file_path: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
        valid_records = []
        validation_errors = []
        
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                return [], ["CSV file has no headers"]
            
            headers_lower = {h.lower(): h for h in reader.fieldnames}
            user_col = None
            for col in ["question", "prompt", "user", "instruction", "input", "query"]:
                if col in headers_lower:
                    user_col = headers_lower[col]
                    break
            
            resp_col = None
            for col in ["answer", "response", "assistant", "output", "reply"]:
                if col in headers_lower:
                    resp_col = headers_lower[col]
                    break
            
            if not user_col or not resp_col:
                return [], [f"CSV columns must include question/prompt and answer/response. Found headers: {list(reader.fieldnames)}"]

            for idx, row in enumerate(reader, 1):
                u_text = row.get(user_col, "").strip()
                a_text = row.get(resp_col, "").strip()
                if u_text and a_text:
                    valid_records.append({
                        "messages": [
                            {"role": "user", "content": u_text},
                            {"role": "assistant", "content": a_text}
                        ]
                    })
                else:
                    validation_errors.append(f"Row {idx}: Missing question or answer text")
                    
        return valid_records, validation_errors

    @staticmethod
    def split_train_val(records: List[Dict[str, Any]], val_ratio: float = 0.1) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        if len(records) <= 2:
            return records, records
        split_idx = max(1, int(len(records) * (1.0 - val_ratio)))
        return records[:split_idx], records[split_idx:]
