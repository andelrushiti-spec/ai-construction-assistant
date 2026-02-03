from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.db.database import db, Project, Contract, Law
try:
    from backend.vector_db.faiss_handler import ContractVectorDB, LawVectorDB
except ImportError:
    from backend.vector_db.numpy_handler import ContractVectorDB, LawVectorDB
from pathlib import Path
import logging
import shutil

logger = logging.getLogger(__name__)

projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')


@projects_bp.route('/', methods=['GET'])
@login_required
def get_projects():
    """Get all projects for current user"""
    try:
        projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.updated_at.desc()).all()

        projects_data = []
        for project in projects:
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat(),
                'contract_count': len(project.contracts),
                'law_count': len(project.laws),
                'query_count': len(project.queries)
            })

        return jsonify({'projects': projects_data}), 200

    except Exception as e:
        logger.error(f"Error fetching projects: {str(e)}")
        return jsonify({'error': 'Failed to fetch projects'}), 500


@projects_bp.route('/', methods=['POST'])
@login_required
def create_project():
    """Create a new project"""
    try:
        data = request.get_json()

        name = data.get('name', '').strip()
        description = data.get('description', '').strip()

        if not name:
            return jsonify({'error': 'Project name is required'}), 400

        # Create project
        project = Project(
            name=name,
            description=description,
            user_id=current_user.id
        )

        db.session.add(project)
        db.session.commit()

        # Create vector DB index paths
        from backend.config import VECTOR_DB_DIR
        project.contract_index_path = str(VECTOR_DB_DIR / f"project_{project.id}_contracts")
        project.law_index_path = str(VECTOR_DB_DIR / f"project_{project.id}_laws")

        db.session.commit()

        logger.info(f"Project created: {name} (ID: {project.id}) by user {current_user.username}")

        return jsonify({
            'message': 'Project created successfully',
            'project': {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'created_at': project.created_at.isoformat()
            }
        }), 201

    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create project'}), 500


@projects_bp.route('/<int:project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    """Get project details"""
    try:
        project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()

        if not project:
            return jsonify({'error': 'Project not found'}), 404

        # Get contracts
        contracts = []
        for contract in project.contracts:
            contracts.append({
                'id': contract.id,
                'filename': contract.original_filename,
                'pages': contract.pages,
                'uploaded_at': contract.uploaded_at.isoformat(),
                'processed': contract.processed,
                'status': contract.processing_status
            })

        # Get laws
        laws = []
        for law in project.laws:
            laws.append({
                'id': law.id,
                'filename': law.original_filename,
                'law_number': law.law_number,
                'law_title': law.law_title,
                'pages': law.pages,
                'uploaded_at': law.uploaded_at.isoformat(),
                'processed': law.processed,
                'status': law.processing_status
            })

        return jsonify({
            'project': {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat(),
                'contracts': contracts,
                'laws': laws
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching project: {str(e)}")
        return jsonify({'error': 'Failed to fetch project'}), 500


@projects_bp.route('/<int:project_id>', methods=['PUT'])
@login_required
def update_project(project_id):
    """Update project"""
    try:
        project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()

        if not project:
            return jsonify({'error': 'Project not found'}), 404

        data = request.get_json()

        if 'name' in data:
            project.name = data['name'].strip()

        if 'description' in data:
            project.description = data['description'].strip()

        db.session.commit()

        logger.info(f"Project updated: {project.name} (ID: {project.id})")

        return jsonify({
            'message': 'Project updated successfully',
            'project': {
                'id': project.id,
                'name': project.name,
                'description': project.description
            }
        }), 200

    except Exception as e:
        logger.error(f"Error updating project: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update project'}), 500


@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    """Delete project and all associated data"""
    try:
        project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()

        if not project:
            return jsonify({'error': 'Project not found'}), 404

        # Delete vector indexes
        if project.contract_index_path:
            try:
                contract_db = ContractVectorDB()
                contract_db.delete_index(project.contract_index_path)
            except Exception as e:
                logger.warning(f"Error deleting contract index: {str(e)}")

        if project.law_index_path:
            try:
                law_db = LawVectorDB()
                law_db.delete_index(project.law_index_path)
            except Exception as e:
                logger.warning(f"Error deleting law index: {str(e)}")

        # Delete uploaded files
        from backend.config import UPLOADS_DIR
        project_upload_dir = UPLOADS_DIR / f"project_{project_id}"
        if project_upload_dir.exists():
            shutil.rmtree(project_upload_dir)

        # Delete project (cascades to contracts, laws, queries)
        project_name = project.name
        db.session.delete(project)
        db.session.commit()

        logger.info(f"Project deleted: {project_name} (ID: {project_id})")

        return jsonify({'message': 'Project deleted successfully'}), 200

    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete project'}), 500
