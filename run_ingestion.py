"""
EduMate ingestion: reads EduMate_RAG_Knowledge_Base.docx, chunks each topic
into 200-word segments with 50-word overlap, embeds via Gemini, upserts to Pinecone.
Produces ~36 vectors instead of 9 for better RAG precision.
"""
import json, urllib.request, urllib.error
from docx import Document

GEMINI_KEY   = 'YOUR_GEMINI_API_KEY'
PINECONE_KEY = 'YOUR_PINECONE_API_KEY'
PINECONE_HOST = 'YOUR_PINECONE_HOST_URL'  # e.g. https://your-index.svc.aped-4627-b74a.pinecone.io
NAMESPACE    = 'edumate_kb'
DOCX_PATH    = 'data/raw/EduMate_RAG_Knowledge_Base.docx'
CHUNK_SIZE   = 200   # words per chunk
CHUNK_OVERLAP = 50   # words overlap between consecutive chunks

GEMINI_EMBED_URL = (
    'https://generativelanguage.googleapis.com/v1beta/models/'
    f'gemini-embedding-001:embedContent?key={GEMINI_KEY}'
)

# Maps H1 heading text → (doc_id_prefix, topic_key)
TOPIC_MAP = {
    '1. Machine Learning Fundamentals':        ('doc-ml-001',  'machine_learning'),
    '2. Neural Networks and Deep Learning':    ('doc-nn-002',  'neural_networks'),
    '3. Python Programming':                   ('doc-py-003',  'python'),
    '4. Algorithms and Data Structures':       ('doc-alg-004', 'algorithms'),
    '5. Databases: SQL and NoSQL':             ('doc-db-005',  'databases'),
    '6. Large Language Models (LLMs)':         ('doc-llm-006', 'llm'),
    '7. Prompt Engineering Techniques':        ('doc-pe-007',  'prompt_engineering'),
    '8. AI Agents: Tools, RAG and Automation': ('doc-agi-008', 'ai_agents'),
    '9. Data Science: Pandas, Charts and EDA': ('doc-ds-009',  'data_science'),
}

OLD_VECTOR_IDS = [
    'doc-ml-001', 'doc-nn-002', 'doc-py-003', 'doc-alg-004', 'doc-db-005',
    'doc-llm-006', 'doc-pe-007', 'doc-agi-008', 'doc-ds-009',
]


def http_post(url, payload, headers=None):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def embed(text):
    result = http_post(GEMINI_EMBED_URL, {
        'content': {'parts': [{'text': text}]},
        'outputDimensionality': 768
    })
    return result['embedding']['values']


def pinecone_delete(ids):
    http_post(
        f'{PINECONE_HOST}/vectors/delete',
        {'ids': ids, 'namespace': NAMESPACE},
        headers={'Api-Key': PINECONE_KEY}
    )


def pinecone_upsert(vectors):
    result = http_post(
        f'{PINECONE_HOST}/vectors/upsert',
        {'vectors': vectors, 'namespace': NAMESPACE},
        headers={'Api-Key': PINECONE_KEY}
    )
    return result


def chunk_text(text):
    words = text.split()
    stride = CHUNK_SIZE - CHUNK_OVERLAP
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + CHUNK_SIZE, len(words))
        chunks.append(' '.join(words[start:end]))
        if end == len(words):
            break
        start += stride
    return chunks


def parse_docx(path):
    doc = Document(path)
    sections = []
    current = None
    in_sources = False

    for p in doc.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        if p.style.name == 'Heading 1' and any(c.isdigit() for c in t[:3]):
            if current:
                sections.append(current)
            current = {'heading': t, 'body': [], 'sources': []}
            in_sources = False
        elif p.style.name == 'Heading 2' and t.lower() == 'sources':
            in_sources = True
        elif current:
            if in_sources:
                current['sources'].append(t)
            else:
                current['body'].append(t)

    if current:
        sections.append(current)
    return sections


if __name__ == '__main__':
    print(f'Reading {DOCX_PATH}...')
    sections = parse_docx(DOCX_PATH)
    print(f'Parsed {len(sections)} topic sections\n')

    # Step 1: delete old single-doc vectors
    print(f'Deleting {len(OLD_VECTOR_IDS)} old vectors...')
    try:
        pinecone_delete(OLD_VECTOR_IDS)
        print('  Old vectors deleted\n')
    except Exception as e:
        print(f'  Delete warning (may not exist): {e}\n')

    # Step 2: chunk, embed, collect vectors
    all_vectors = []
    total_chunks = 0

    for section in sections:
        heading = section['heading']
        if heading not in TOPIC_MAP:
            print(f'Skipping unrecognized section: {heading}')
            continue

        doc_id, topic = TOPIC_MAP[heading]
        title = heading.split('. ', 1)[1]
        body = ' '.join(section['body'])
        sources = section['sources']
        chunks = chunk_text(body)

        print(f'{title}')
        print(f'  {len(body.split())} words -> {len(chunks)} chunks')

        for i, chunk in enumerate(chunks):
            vector = embed(chunk)
            all_vectors.append({
                'id': f'{doc_id}-c{i}',
                'values': vector,
                'metadata': {
                    'topic': topic,
                    'title': title,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'text': chunk,
                    'sources': sources,
                }
            })
            total_chunks += 1
            print(f'  c{i}: {len(chunk.split())} words embedded ok')

        print()

    # Step 3: upsert in batches of 10
    print(f'Upserting {total_chunks} chunks to Pinecone...')
    batch_size = 10
    for i in range(0, len(all_vectors), batch_size):
        batch = all_vectors[i:i + batch_size]
        result = pinecone_upsert(batch)
        print(f'  Batch {i // batch_size + 1}/{-(-len(all_vectors) // batch_size)}: {result}')

    print(f'\nDone! {total_chunks} chunks in namespace "{NAMESPACE}"')
    print(f'Pinecone now holds {total_chunks} vectors (was 9 before chunking)')
