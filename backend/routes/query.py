"""
Construction Legal Assistant
Query Routes - Question Answering with RAG

Developer: Andel Albdesk
Copyright (c) 2026 Andel Albdesk. All rights reserved.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.db.database import db, Project, Query, Conversation
from backend.processing.embeddings import EmbeddingGenerator
try:
    from backend.vector_db.faiss_handler import ContractVectorDB, LawVectorDB
except ImportError:
    from backend.vector_db.numpy_handler import ContractVectorDB, LawVectorDB
from langdetect import detect
from pathlib import Path
import openai
import logging
import time
import json

logger = logging.getLogger(__name__)

query_bp = Blueprint('query', __name__, url_prefix='/api/query')


def detect_language(text):
    """Detect language of text"""
    try:
        lang = detect(text)
        # Map to supported languages
        if lang in ['sq', 'en']:
            return lang
        # Default to English for unsupported languages
        return 'en'
    except:
        return 'en'


def format_context_for_llm(contract_chunks, law_chunks):
    """Format retrieved chunks for LLM context"""
    context = "=== RELEVANT CONTRACT INFORMATION ===\n\n"

    if contract_chunks:
        for i, chunk in enumerate(contract_chunks, 1):
            context += f"[Contract Chunk {i}]\n"
            context += f"Document: {chunk.get('doc_name', 'Unknown')}\n"
            context += f"Page: {chunk.get('page', 'N/A')}\n"
            if chunk.get('clause'):
                context += f"Clause: {chunk.get('clause')}\n"
            context += f"Content: {chunk.get('text', '')}\n"
            context += f"Relevance Score: {chunk.get('similarity_score', 0):.3f}\n\n"
    else:
        context += "No relevant contract information found.\n\n"

    context += "=== RELEVANT LAW INFORMATION ===\n\n"

    if law_chunks:
        for i, chunk in enumerate(law_chunks, 1):
            context += f"[Law Chunk {i}]\n"
            context += f"Document: {chunk.get('doc_name', 'Unknown')}\n"
            context += f"Page: {chunk.get('page', 'N/A')}\n"
            if chunk.get('article'):
                context += f"Article: {chunk.get('article')}\n"
            context += f"Content: {chunk.get('text', '')}\n"
            context += f"Relevance Score: {chunk.get('similarity_score', 0):.3f}\n\n"
    else:
        context += "No relevant law information found.\n\n"

    return context


def extract_citations(contract_chunks, law_chunks):
    """Extract citation information from chunks including source text"""
    citations = {
        'contracts': [],
        'laws': []
    }

    for chunk in contract_chunks:
        citation = {
            'document': chunk.get('doc_name', 'Unknown'),
            'page': chunk.get('page', 'N/A'),
            'clause': chunk.get('clause', ''),
            'score': chunk.get('similarity_score', 0),
            'text': chunk.get('text', '')  # Include the actual chunk text
        }
        citations['contracts'].append(citation)

    for chunk in law_chunks:
        citation = {
            'document': chunk.get('doc_name', 'Unknown'),
            'page': chunk.get('page', 'N/A'),
            'article': chunk.get('article', ''),
            'score': chunk.get('similarity_score', 0),
            'text': chunk.get('text', '')  # Include the actual chunk text
        }
        citations['laws'].append(citation)

    return citations


@query_bp.route('/<int:project_id>', methods=['POST'])
@login_required
def ask_question(project_id):
    """Ask a question about contracts and laws"""
    try:
        start_time = time.time()

        # Verify project ownership
        project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()

        if not project:
            return jsonify({'error': 'Project not found'}), 404

        # Get question from request
        data = request.get_json()
        question = data.get('question', '').strip()
        conversation_id = data.get('conversation_id')  # Optional

        if not question:
            return jsonify({'error': 'Question is required'}), 400

        # Detect language
        language = detect_language(question)
        logger.info(f"Question language detected: {language}")

        # Handle conversation
        conversation = None
        if conversation_id:
            # Load existing conversation
            conversation = Conversation.query.filter_by(
                id=conversation_id,
                project_id=project_id,
                user_id=current_user.id
            ).first()
            if not conversation:
                return jsonify({'error': 'Conversation not found'}), 404
        else:
            # Create new conversation with auto-generated title
            conversation_title = question[:100] if len(question) <= 100 else question[:97] + "..."
            conversation = Conversation(
                project_id=project_id,
                user_id=current_user.id,
                title=conversation_title
            )
            db.session.add(conversation)
            db.session.flush()  # Get the conversation ID

        # Initialize components
        from backend.config import OPENAI_API_KEY, EMBEDDING_MODEL, LLM_MODEL, TOP_K_RESULTS, RAG_SYSTEM_PROMPT

        embedder = EmbeddingGenerator(api_key=OPENAI_API_KEY, model=EMBEDDING_MODEL)
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        # Generate query embedding
        query_embedding = embedder.embed_query(question)

        # Retrieve relevant contract chunks
        contract_chunks = []
        contract_index_file = Path(project.contract_index_path + '.npy') if project.contract_index_path else None
        if contract_index_file and (contract_index_file.exists() or Path(project.contract_index_path + '.faiss').exists()):
            contract_db = ContractVectorDB(dimension=embedder.get_embedding_dimension())
            contract_db.load_index(project.contract_index_path)
            contract_chunks = contract_db.search_contracts(query_embedding, top_k=TOP_K_RESULTS)
            logger.info(f"Retrieved {len(contract_chunks)} contract chunks")

        # Retrieve relevant law chunks
        law_chunks = []
        law_index_file = Path(project.law_index_path + '.npy') if project.law_index_path else None
        if law_index_file and (law_index_file.exists() or Path(project.law_index_path + '.faiss').exists()):
            law_db = LawVectorDB(dimension=embedder.get_embedding_dimension())
            law_db.load_index(project.law_index_path)
            law_chunks = law_db.search_laws(query_embedding, top_k=TOP_K_RESULTS)
            logger.info(f"Retrieved {len(law_chunks)} law chunks")

        # Format context for LLM (even if empty, we'll let GPT-4 answer from general knowledge)
        context = format_context_for_llm(contract_chunks, law_chunks)

        # Add note if no documents available
        if not contract_chunks and not law_chunks:
            context += "\n\nNOTE: No documents have been uploaded to this project yet. Answer from general construction knowledge."

        # Build conversation history
        conversation_history = []
        if conversation_id and conversation:
            # Get previous messages from the conversation (limit to last 10 for context window)
            previous_messages = Query.query.filter_by(
                conversation_id=conversation.id
            ).order_by(Query.created_at.asc()).limit(10).all()

            for msg in previous_messages:
                conversation_history.append({"role": "user", "content": msg.question})
                if msg.answer:
                    conversation_history.append({"role": "assistant", "content": msg.answer})

        # Create LLM prompt
        user_prompt = f"""Based on the provided contract and law information, answer the following question:

Question: {question}

Instructions:
- Answer in {language} language ({'Albanian' if language == 'sq' else 'English'})
- Cite specific contracts (page + clause) and laws (number + article)
- If the information is not in the provided context, clearly state this
- Be precise and construction-focused
- Consider the conversation history if this is a follow-up question

{context}
"""

        # Call GPT-4
        logger.info(f"Calling {LLM_MODEL} for answer generation")

        # Build messages with conversation history
        messages = [{"role": "system", "content": RAG_SYSTEM_PROMPT}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_prompt})

        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.3,  # Lower temperature for more factual answers
            max_tokens=1500
        )

        answer = response.choices[0].message.content

        # Extract citations
        citations = extract_citations(contract_chunks, law_chunks)

        # Calculate response time
        response_time = time.time() - start_time

        # Save query to database
        query_record = Query(
            conversation_id=conversation.id,
            project_id=project_id,
            user_id=current_user.id,
            question=question,
            answer=answer,
            language=language,
            contract_citations=json.dumps(citations['contracts']),
            law_citations=json.dumps(citations['laws']),
            response_time=response_time
        )

        db.session.add(query_record)
        db.session.commit()

        logger.info(f"Query processed in {response_time:.2f}s")

        return jsonify({
            'answer': answer,
            'citations': citations,
            'language': language,
            'response_time': response_time,
            'query_id': query_record.id,
            'conversation_id': conversation.id
        }), 200

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({'error': 'Failed to process question'}), 500


@query_bp.route('/history/<int:project_id>', methods=['GET'])
@login_required
def get_query_history(project_id):
    """Get query history for a project"""
    try:
        # Verify project ownership
        project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()

        if not project:
            return jsonify({'error': 'Project not found'}), 404

        # Get queries
        queries = Query.query.filter_by(project_id=project_id).order_by(Query.created_at.desc()).limit(50).all()

        history = []
        for q in queries:
            history.append({
                'id': q.id,
                'question': q.question,
                'answer': q.answer,
                'language': q.language,
                'created_at': q.created_at.isoformat(),
                'response_time': q.response_time,
                'citations': {
                    'contracts': json.loads(q.contract_citations) if q.contract_citations else [],
                    'laws': json.loads(q.law_citations) if q.law_citations else []
                }
            })

        return jsonify({'history': history}), 200

    except Exception as e:
        logger.error(f"Error fetching query history: {str(e)}")
        return jsonify({'error': 'Failed to fetch history'}), 500


@query_bp.route('/<int:query_id>', methods=['DELETE'])
@login_required
def delete_query(query_id):
    """Delete a query from history"""
    try:
        query = Query.query.get(query_id)

        if not query:
            return jsonify({'error': 'Query not found'}), 404

        # Verify ownership
        if query.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403

        db.session.delete(query)
        db.session.commit()

        return jsonify({'message': 'Query deleted successfully'}), 200

    except Exception as e:
        logger.error(f"Error deleting query: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete query'}), 500
