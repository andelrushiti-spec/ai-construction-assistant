from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from backend.db.database import db, Project, Contract
from backend.processing.document_extractor import DocumentExtractor
from backend.processing.chunker import TextChunker
from backend.processing.embeddings import EmbeddingGenerator
try:
    from backend.vector_db.faiss_handler import ContractVectorDB
except ImportError:
    from backend.vector_db.numpy_handler import ContractVectorDB
from pathlib import Path
import logging
import os
from threading import Thread

logger = logging.getLogger(__name__)

upload_contract_bp = Blueprint('upload_contract', __name__, url_prefix='/api/upload/contract')


def allowed_file(filename):
    """Check if file extension is allowed"""
    from backend.config import ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_contract_async(contract_id, file_path, project_id, app):
    """Process contract in background thread"""
    from backend.config import OPENAI_API_KEY, TESSERACT_CMD, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, AUTO_DELETE_UPLOADS

    # Use Flask application context
    with app.app_context():
        try:
            # Get fresh instances within app context
            contract = Contract.query.get(contract_id)
            project = Project.query.get(project_id)

            contract.processing_status = 'processing'
            db.session.commit()

            logger.info(f"Processing contract {contract_id}: {contract.original_filename}")

            # 1. Extract text from document (PDF, Word, or Pages)
            extractor = DocumentExtractor(tesseract_cmd=TESSERACT_CMD)
            pages = extractor.extract_text(file_path)

            # Get metadata
            metadata = extractor.extract_contract_metadata(pages)

            # Update contract with extracted info
            contract.pages = len(pages)
            contract.parties = ', '.join(metadata.get('parties', []))
            db.session.commit()

            # 2. Chunk text
            chunker = TextChunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
            chunks = chunker.chunk_pages(
                pages,
                doc_type='contract',
                doc_name=contract.original_filename
            )

            logger.info(f"Created {len(chunks)} chunks from contract {contract_id}")

            # 3. Generate embeddings
            embedder = EmbeddingGenerator(api_key=OPENAI_API_KEY, model=EMBEDDING_MODEL)
            chunks = embedder.embed_chunks(chunks)

            # 4. Add to vector database
            contract_db = ContractVectorDB(dimension=embedder.get_embedding_dimension())

            # Load existing index if it exists (check both .faiss and .npy)
            index_exists = False
            if project.contract_index_path:
                index_exists = Path(project.contract_index_path + '.faiss').exists() or Path(project.contract_index_path + '.npy').exists()

            if index_exists:
                contract_db.load_index(project.contract_index_path)
                contract_db.add_to_index(
                    [chunk['embedding'] for chunk in chunks],
                    chunks
                )
            else:
                contract_db.create_index(
                    [chunk['embedding'] for chunk in chunks],
                    chunks
                )

            # Save index
            contract_db.save_index(project.contract_index_path)

            # 5. Update contract status
            contract.processed = True
            contract.processing_status = 'completed'
            db.session.commit()

            # 6. Delete uploaded file (privacy-first)
            if AUTO_DELETE_UPLOADS and Path(file_path).exists():
                os.remove(file_path)
                logger.info(f"Deleted uploaded file: {file_path}")

            logger.info(f"Contract {contract_id} processed successfully")

        except Exception as e:
            logger.error(f"Error processing contract {contract_id}: {str(e)}")

            # Update contract with error
            contract = Contract.query.get(contract_id)
            contract.processing_status = 'failed'
            contract.error_message = str(e)
            db.session.commit()


@upload_contract_bp.route('/<int:project_id>', methods=['POST'])
@login_required
def upload_contract(project_id):
    """Upload and process contract document (PDF, Word, or Pages)"""
    try:
        # Verify project ownership
        project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()

        if not project:
            return jsonify({'error': 'Project not found'}), 404

        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF, Word (.docx, .doc), and Pages files are allowed'}), 400

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        from backend.config import MAX_FILE_SIZE_MB
        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            return jsonify({'error': f'File size exceeds {MAX_FILE_SIZE_MB}MB limit'}), 400

        # Save file
        filename = secure_filename(file.filename)
        from backend.config import UPLOADS_DIR

        upload_dir = UPLOADS_DIR / f"project_{project_id}" / "contracts"
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Add timestamp to filename to avoid conflicts
        from datetime import datetime
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        name_parts = filename.rsplit('.', 1)
        if len(name_parts) == 2:
            unique_filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
        else:
            unique_filename = f"{filename}_{timestamp}"

        filepath = upload_dir / unique_filename
        file.save(str(filepath))

        # Create contract record
        contract = Contract(
            project_id=project_id,
            filename=unique_filename,
            original_filename=filename,
            file_size=file_size,
            processing_status='pending'
        )

        db.session.add(contract)
        db.session.commit()

        logger.info(f"Contract uploaded: {filename} (ID: {contract.id}) for project {project_id}")

        # Process contract in background thread
        thread = Thread(
            target=process_contract_async,
            args=(contract.id, str(filepath), project.id, current_app._get_current_object())
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            'message': 'Contract uploaded successfully. Processing in background.',
            'contract': {
                'id': contract.id,
                'filename': contract.original_filename,
                'status': contract.processing_status,
                'uploaded_at': contract.uploaded_at.isoformat()
            }
        }), 201

    except Exception as e:
        logger.error(f"Error uploading contract: {str(e)}")
        return jsonify({'error': 'Failed to upload contract'}), 500


@upload_contract_bp.route('/<int:contract_id>/status', methods=['GET'])
@login_required
def get_contract_status(contract_id):
    """Get contract processing status"""
    try:
        contract = Contract.query.get(contract_id)

        if not contract:
            return jsonify({'error': 'Contract not found'}), 404

        # Verify ownership through project
        project = Project.query.filter_by(id=contract.project_id, user_id=current_user.id).first()
        if not project:
            return jsonify({'error': 'Unauthorized'}), 403

        return jsonify({
            'contract': {
                'id': contract.id,
                'filename': contract.original_filename,
                'status': contract.processing_status,
                'processed': contract.processed,
                'pages': contract.pages,
                'error_message': contract.error_message,
                'uploaded_at': contract.uploaded_at.isoformat()
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching contract status: {str(e)}")
        return jsonify({'error': 'Failed to fetch status'}), 500


@upload_contract_bp.route('/<int:contract_id>', methods=['DELETE'])
@login_required
def delete_contract(contract_id):
    """Delete contract"""
    try:
        contract = Contract.query.get(contract_id)

        if not contract:
            return jsonify({'error': 'Contract not found'}), 404

        # Verify ownership
        project = Project.query.filter_by(id=contract.project_id, user_id=current_user.id).first()
        if not project:
            return jsonify({'error': 'Unauthorized'}), 403

        # Note: Deleting individual contracts from vector index is complex
        # For MVP, we recommend deleting the entire project or rebuilding the index
        # A production version would implement incremental deletion

        contract_name = contract.original_filename
        db.session.delete(contract)
        db.session.commit()

        logger.info(f"Contract deleted: {contract_name} (ID: {contract_id})")

        return jsonify({
            'message': 'Contract deleted successfully. Note: Vector index will be rebuilt on next upload.'
        }), 200

    except Exception as e:
        logger.error(f"Error deleting contract: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete contract'}), 500
