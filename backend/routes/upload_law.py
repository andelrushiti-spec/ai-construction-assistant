from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from backend.db.database import db, Project, Law
from backend.processing.document_extractor import DocumentExtractor
from backend.processing.chunker import TextChunker
from backend.processing.embeddings import EmbeddingGenerator
try:
    from backend.vector_db.faiss_handler import LawVectorDB
except ImportError:
    from backend.vector_db.numpy_handler import LawVectorDB
from pathlib import Path
import logging
import os
from threading import Thread

logger = logging.getLogger(__name__)

upload_law_bp = Blueprint('upload_law', __name__, url_prefix='/api/upload/law')


def allowed_file(filename):
    """Check if file extension is allowed"""
    from backend.config import ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_law_async(law_id, file_path, project_id, app):
    """Process law document in background thread"""
    from backend.config import OPENAI_API_KEY, TESSERACT_CMD, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, AUTO_DELETE_UPLOADS

    # Use Flask application context
    with app.app_context():
        try:
            # Get fresh instances within app context
            law = Law.query.get(law_id)
            project = Project.query.get(project_id)

            law.processing_status = 'processing'
            db.session.commit()

            logger.info(f"Processing law {law_id}: {law.original_filename}")

            # 1. Extract text from document (PDF, Word, or Pages)
            extractor = DocumentExtractor(tesseract_cmd=TESSERACT_CMD)
            pages = extractor.extract_text(file_path)

            # Get law metadata
            metadata = extractor.extract_law_metadata(pages)

            # Update law with extracted info
            law.pages = len(pages)
            if metadata.get('law_number'):
                law.law_number = metadata['law_number']
            if metadata.get('year'):
                law.year = metadata['year']
            db.session.commit()

            # 2. Chunk text
            chunker = TextChunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
            chunks = chunker.chunk_pages(
                pages,
                doc_type='law',
                doc_name=law.original_filename
            )

            logger.info(f"Created {len(chunks)} chunks from law {law_id}")

            # 3. Generate embeddings
            embedder = EmbeddingGenerator(api_key=OPENAI_API_KEY, model=EMBEDDING_MODEL)
            chunks = embedder.embed_chunks(chunks)

            # 4. Add to vector database
            law_db = LawVectorDB(dimension=embedder.get_embedding_dimension())

            # Load existing index if it exists (check both .faiss and .npy)
            index_exists = False
            if project.law_index_path:
                index_exists = Path(project.law_index_path + '.faiss').exists() or Path(project.law_index_path + '.npy').exists()

            if index_exists:
                law_db.load_index(project.law_index_path)
                law_db.add_to_index(
                    [chunk['embedding'] for chunk in chunks],
                    chunks
                )
            else:
                law_db.create_index(
                    [chunk['embedding'] for chunk in chunks],
                    chunks
                )

            # Save index
            law_db.save_index(project.law_index_path)

            # 5. Update law status
            law.processed = True
            law.processing_status = 'completed'
            db.session.commit()

            # 6. Delete uploaded file (privacy-first)
            if AUTO_DELETE_UPLOADS and Path(file_path).exists():
                os.remove(file_path)
                logger.info(f"Deleted uploaded file: {file_path}")

            logger.info(f"Law {law_id} processed successfully")

        except Exception as e:
            logger.error(f"Error processing law {law_id}: {str(e)}")

            # Update law with error
            law = Law.query.get(law_id)
            law.processing_status = 'failed'
            law.error_message = str(e)
            db.session.commit()


@upload_law_bp.route('/<int:project_id>', methods=['POST'])
@login_required
def upload_law(project_id):
    """Upload and process law document (PDF, Word, or Pages)"""
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

        # Get optional metadata from form
        law_number = request.form.get('law_number', '').strip()
        law_title = request.form.get('law_title', '').strip()
        year = request.form.get('year', '').strip()
        update_version = request.form.get('update_version', '').strip()

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

        upload_dir = UPLOADS_DIR / f"project_{project_id}" / "laws"
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Add timestamp to filename
        from datetime import datetime
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        name_parts = filename.rsplit('.', 1)
        if len(name_parts) == 2:
            unique_filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
        else:
            unique_filename = f"{filename}_{timestamp}"

        filepath = upload_dir / unique_filename
        file.save(str(filepath))

        # Create law record
        law = Law(
            project_id=project_id,
            filename=unique_filename,
            original_filename=filename,
            file_size=file_size,
            processing_status='pending',
            law_number=law_number if law_number else None,
            law_title=law_title if law_title else None,
            year=int(year) if year and year.isdigit() else None,
            update_version=update_version if update_version else None
        )

        db.session.add(law)
        db.session.commit()

        logger.info(f"Law uploaded: {filename} (ID: {law.id}) for project {project_id}")

        # Process law in background thread
        thread = Thread(
            target=process_law_async,
            args=(law.id, str(filepath), project.id, current_app._get_current_object())
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            'message': 'Law uploaded successfully. Processing in background.',
            'law': {
                'id': law.id,
                'filename': law.original_filename,
                'law_number': law.law_number,
                'status': law.processing_status,
                'uploaded_at': law.uploaded_at.isoformat()
            }
        }), 201

    except Exception as e:
        logger.error(f"Error uploading law: {str(e)}")
        return jsonify({'error': 'Failed to upload law'}), 500


@upload_law_bp.route('/<int:law_id>/status', methods=['GET'])
@login_required
def get_law_status(law_id):
    """Get law processing status"""
    try:
        law = Law.query.get(law_id)

        if not law:
            return jsonify({'error': 'Law not found'}), 404

        # Verify ownership through project
        project = Project.query.filter_by(id=law.project_id, user_id=current_user.id).first()
        if not project:
            return jsonify({'error': 'Unauthorized'}), 403

        return jsonify({
            'law': {
                'id': law.id,
                'filename': law.original_filename,
                'law_number': law.law_number,
                'law_title': law.law_title,
                'year': law.year,
                'status': law.processing_status,
                'processed': law.processed,
                'pages': law.pages,
                'error_message': law.error_message,
                'uploaded_at': law.uploaded_at.isoformat()
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching law status: {str(e)}")
        return jsonify({'error': 'Failed to fetch status'}), 500


@upload_law_bp.route('/<int:law_id>', methods=['DELETE'])
@login_required
def delete_law(law_id):
    """Delete law"""
    try:
        law = Law.query.get(law_id)

        if not law:
            return jsonify({'error': 'Law not found'}), 404

        # Verify ownership
        project = Project.query.filter_by(id=law.project_id, user_id=current_user.id).first()
        if not project:
            return jsonify({'error': 'Unauthorized'}), 403

        law_name = law.original_filename
        db.session.delete(law)
        db.session.commit()

        logger.info(f"Law deleted: {law_name} (ID: {law_id})")

        return jsonify({
            'message': 'Law deleted successfully. Note: Vector index will be rebuilt on next upload.'
        }), 200

    except Exception as e:
        logger.error(f"Error deleting law: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete law'}), 500
