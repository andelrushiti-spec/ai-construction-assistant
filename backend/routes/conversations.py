"""
AI Construction Contract & Law Assistant
Conversation Routes - Manage Conversations

Developer: Andel Albdesk
Copyright (c) 2026 Andel Albdesk. All rights reserved.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.db.database import db, Project, Conversation, Query
import logging
import json

logger = logging.getLogger(__name__)

conversations_bp = Blueprint('conversations', __name__, url_prefix='/api/conversations')


@conversations_bp.route('/project/<int:project_id>', methods=['GET'])
@login_required
def list_conversations(project_id):
    """List all conversations for a project"""
    try:
        # Verify project ownership
        project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()

        if not project:
            return jsonify({'error': 'Project not found'}), 404

        # Get all conversations for this project
        conversations = Conversation.query.filter_by(
            project_id=project_id,
            user_id=current_user.id
        ).order_by(Conversation.updated_at.desc()).all()

        conversations_list = []
        for conv in conversations:
            # Get message count
            message_count = Query.query.filter_by(conversation_id=conv.id).count()

            conversations_list.append({
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
                'message_count': message_count
            })

        return jsonify({'conversations': conversations_list}), 200

    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        return jsonify({'error': 'Failed to list conversations'}), 500


@conversations_bp.route('/<int:conversation_id>', methods=['GET'])
@login_required
def get_conversation(conversation_id):
    """Get a specific conversation with all its messages"""
    try:
        # Get conversation and verify ownership
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=current_user.id
        ).first()

        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404

        # Get all messages in the conversation
        messages = Query.query.filter_by(
            conversation_id=conversation_id
        ).order_by(Query.created_at.asc()).all()

        messages_list = []
        for msg in messages:
            messages_list.append({
                'id': msg.id,
                'question': msg.question,
                'answer': msg.answer,
                'language': msg.language,
                'created_at': msg.created_at.isoformat(),
                'response_time': msg.response_time,
                'citations': {
                    'contracts': json.loads(msg.contract_citations) if msg.contract_citations else [],
                    'laws': json.loads(msg.law_citations) if msg.law_citations else []
                }
            })

        return jsonify({
            'conversation': {
                'id': conversation.id,
                'title': conversation.title,
                'project_id': conversation.project_id,
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat(),
                'messages': messages_list
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}")
        return jsonify({'error': 'Failed to get conversation'}), 500


@conversations_bp.route('/<int:conversation_id>', methods=['DELETE'])
@login_required
def delete_conversation(conversation_id):
    """Delete a conversation and all its messages"""
    try:
        # Get conversation and verify ownership
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=current_user.id
        ).first()

        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404

        # Delete conversation (cascade will delete all messages)
        db.session.delete(conversation)
        db.session.commit()

        return jsonify({'message': 'Conversation deleted successfully'}), 200

    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete conversation'}), 500


@conversations_bp.route('/<int:conversation_id>/title', methods=['PUT'])
@login_required
def update_conversation_title(conversation_id):
    """Update conversation title"""
    try:
        # Get conversation and verify ownership
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=current_user.id
        ).first()

        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404

        # Get new title from request
        data = request.get_json()
        new_title = data.get('title', '').strip()

        if not new_title:
            return jsonify({'error': 'Title is required'}), 400

        if len(new_title) > 200:
            return jsonify({'error': 'Title too long (max 200 characters)'}), 400

        # Update title
        conversation.title = new_title
        db.session.commit()

        return jsonify({
            'message': 'Title updated successfully',
            'conversation': {
                'id': conversation.id,
                'title': conversation.title
            }
        }), 200

    except Exception as e:
        logger.error(f"Error updating conversation title: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update title'}), 500
