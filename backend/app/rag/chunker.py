from typing import List, Dict, Any

class DocumentChunker:
    """
    Chunks document text into overlapping segments preserving semantic context and page provenance.
    """
    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 60,
        metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        metadata = metadata or {}
        words = text.split()
        if not words:
            return []
        
        chunks = []
        start_idx = 0
        chunk_id = 0
        
        while start_idx < len(words):
            end_idx = min(start_idx + chunk_size, len(words))
            chunk_words = words[start_idx:end_idx]
            chunk_text = " ".join(chunk_words)
            
            chunk_meta = dict(metadata)
            chunk_meta["chunk_index"] = chunk_id
            chunk_meta["start_word"] = start_idx
            chunk_meta["end_word"] = end_idx
            
            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "metadata": chunk_meta
            })
            
            chunk_id += 1
            if end_idx >= len(words):
                break
            start_idx += max(1, chunk_size - chunk_overlap)
            
        return chunks

    @staticmethod
    def chunk_pages(
        pages: List[Dict[str, Any]],
        chunk_size: int = 400,
        chunk_overlap: int = 50,
        doc_name: str = "document"
    ) -> List[Dict[str, Any]]:
        all_chunks = []
        global_chunk_idx = 0
        
        for p in pages:
            page_num = p.get("page_number", 1)
            page_text = p.get("text", "")
            page_meta = {"document_name": doc_name, "page": page_num}
            
            page_chunks = DocumentChunker.chunk_text(
                page_text,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                metadata=page_meta
            )
            for c in page_chunks:
                c["chunk_id"] = global_chunk_idx
                c["metadata"]["chunk_index"] = global_chunk_idx
                all_chunks.append(c)
                global_chunk_idx += 1
                
        return all_chunks
