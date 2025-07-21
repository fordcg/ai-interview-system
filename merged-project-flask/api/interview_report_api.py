#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
面试报告API
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import json

from models.interview_report import InterviewReport, interview_report_schema, interview_reports_schema
from base.core import db

interview_report_bp = Blueprint('interview_report', __name__)

@interview_report_bp.route('/save', methods=['POST'])
@login_required
def save_report():
    """保存面试报告"""
    try:
        data = request.json
        
        # 验证必需字段
        if not data.get('reportType'):
            return jsonify({
                'success': False,
                'message': '报告类型不能为空'
            }), 400
        
        # 生成报告标题
        title = data.get('title') or f"面试分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 创建报告记录
        report = InterviewReport(
            user_id=current_user.id,
            report_type=data.get('reportType'),
            title=title
        )

        # 设置JSON数据
        report.set_analysis_data(data.get('analysisData'))
        report.set_raw_data(data.get('rawData'))
        report.set_report_metadata({
            'user_agent': request.headers.get('User-Agent'),
            'ip_address': request.remote_addr,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '报告保存成功',
            'data': {
                'report_id': report.id,
                'title': report.title,
                'created_at': report.created_at.isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'保存报告失败: {str(e)}'
        }), 500

@interview_report_bp.route('/list', methods=['GET'])
@login_required
def list_reports():
    """获取用户的报告列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        report_type = request.args.get('report_type')
        
        # 构建查询
        query = InterviewReport.query.filter_by(
            user_id=current_user.id,
            status='active'
        )
        
        if report_type:
            query = query.filter_by(report_type=report_type)
        
        # 分页查询
        reports = query.order_by(InterviewReport.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'reports': interview_reports_schema.dump(reports.items),
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': reports.total,
                    'pages': reports.pages,
                    'has_next': reports.has_next,
                    'has_prev': reports.has_prev
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取报告列表失败: {str(e)}'
        }), 500

@interview_report_bp.route('/<int:report_id>', methods=['GET'])
@login_required
def get_report(report_id):
    """获取特定报告"""
    try:
        report = InterviewReport.query.filter_by(
            id=report_id,
            user_id=current_user.id,
            status='active'
        ).first()
        
        if not report:
            return jsonify({
                'success': False,
                'message': '报告不存在或无权限访问'
            }), 404
        
        return jsonify({
            'success': True,
            'data': interview_report_schema.dump(report)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取报告失败: {str(e)}'
        }), 500

@interview_report_bp.route('/<int:report_id>', methods=['PUT'])
@login_required
def update_report(report_id):
    """更新报告"""
    try:
        report = InterviewReport.query.filter_by(
            id=report_id,
            user_id=current_user.id,
            status='active'
        ).first()
        
        if not report:
            return jsonify({
                'success': False,
                'message': '报告不存在或无权限访问'
            }), 404
        
        data = request.json
        
        # 更新字段
        if 'title' in data:
            report.title = data['title']
        if 'analysisData' in data:
            report.set_analysis_data(data['analysisData'])
        if 'rawData' in data:
            report.set_raw_data(data['rawData'])
        
        report.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '报告更新成功',
            'data': interview_report_schema.dump(report)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新报告失败: {str(e)}'
        }), 500

@interview_report_bp.route('/<int:report_id>', methods=['DELETE'])
@login_required
def delete_report(report_id):
    """删除报告（软删除）"""
    try:
        report = InterviewReport.query.filter_by(
            id=report_id,
            user_id=current_user.id,
            status='active'
        ).first()
        
        if not report:
            return jsonify({
                'success': False,
                'message': '报告不存在或无权限访问'
            }), 404
        
        # 软删除
        report.status = 'deleted'
        report.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '报告删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'删除报告失败: {str(e)}'
        }), 500

@interview_report_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """获取报告统计信息"""
    try:
        total_reports = InterviewReport.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).count()
        
        # 按类型统计
        type_stats = db.session.query(
            InterviewReport.report_type,
            db.func.count(InterviewReport.id).label('count')
        ).filter_by(
            user_id=current_user.id,
            status='active'
        ).group_by(InterviewReport.report_type).all()
        
        # 最近的报告
        recent_reports = InterviewReport.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).order_by(InterviewReport.created_at.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'data': {
                'total_reports': total_reports,
                'type_stats': [{'type': t[0], 'count': t[1]} for t in type_stats],
                'recent_reports': interview_reports_schema.dump(recent_reports)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计信息失败: {str(e)}'
        }), 500
