
"""
Advanced Security and Compliance Features for Enterprise Deployment
"""
import hashlib
import secrets
import base64
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json
import os
from pathlib import Path
import ipaddress
from functools import wraps
import time

from .database import SessionLocal, get_db_context
from .config import settings

logger = logging.getLogger(__name__)

class AdvancedSecurityManager:
    """Enterprise-level security management system"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.audit_logger = AuditLogger()
        self.access_control = RBACManager()
        self.session_manager = SessionManager()
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for data protection"""
        key_file = Path("config/.encryption_key")
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key_file.parent.mkdir(exist_ok=True)
            key = Fernet.generate_key()
            
            # Store securely (in production, use HSM or key management service)
            with open(key_file, 'wb') as f:
                f.write(key)
            
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
            
            logger.info("New encryption key generated")
            return key
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data for storage"""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def hash_pii(self, data: str, salt: str = None) -> Dict[str, str]:
        """Hash personally identifiable information with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 for strong hashing
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
        )
        
        key = kdf.derive(data.encode())
        hashed_data = base64.b64encode(key).decode()
        
        return {
            'hash': hashed_data,
            'salt': salt,
            'algorithm': 'PBKDF2-SHA256',
            'iterations': 100000
        }
    
    def verify_pii_hash(self, data: str, stored_hash: str, salt: str) -> bool:
        """Verify PII hash"""
        try:
            result = self.hash_pii(data, salt)
            return result['hash'] == stored_hash
        except Exception as e:
            logger.error(f"Hash verification failed: {e}")
            return False
    
    def anonymize_customer_data(self, customer_data: Dict) -> Dict:
        """Anonymize customer data for GDPR compliance"""
        anonymized = customer_data.copy()
        
        # Remove direct identifiers
        sensitive_fields = [
            'customer_id', 'name', 'email', 'phone', 'address',
            'id_number', 'passport', 'social_security'
        ]
        
        for field in sensitive_fields:
            if field in anonymized:
                if field == 'customer_id':
                    # Replace with anonymized ID
                    anonymized[field] = f"ANON_{hashlib.md5(str(anonymized[field]).encode()).hexdigest()[:8]}"
                else:
                    del anonymized[field]
        
        # Generalize quasi-identifiers
        if 'age' in anonymized:
            # Generalize age to ranges
            age = anonymized['age']
            if age < 25:
                anonymized['age_group'] = '18-24'
            elif age < 35:
                anonymized['age_group'] = '25-34'
            elif age < 45:
                anonymized['age_group'] = '35-44'
            elif age < 55:
                anonymized['age_group'] = '45-54'
            else:
                anonymized['age_group'] = '55+'
            del anonymized['age']
        
        if 'location' in anonymized:
            # Generalize location to city level
            anonymized['city'] = anonymized['location'].split(',')[0] if ',' in str(anonymized['location']) else anonymized['location']
            del anonymized['location']
        
        # Add anonymization metadata
        anonymized['_anonymized'] = True
        anonymized['_anonymized_at'] = datetime.now().isoformat()
        
        return anonymized

class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self):
        self.audit_file = Path("logs/audit.log")
        self.audit_file.parent.mkdir(exist_ok=True)
        
        # Setup audit logger
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.FileHandler(self.audit_file)
            formatter = logging.Formatter(
                '%(asctime)s - AUDIT - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_access(self, user_id: str, resource: str, action: str, 
                   ip_address: str = None, user_agent: str = None, 
                   result: str = "success", details: Dict = None):
        """Log access attempt"""
        audit_entry = {
            'event_type': 'access',
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'result': result,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        self.logger.info(json.dumps(audit_entry))
    
    def log_data_access(self, user_id: str, data_type: str, record_ids: List[str],
                       action: str, ip_address: str = None):
        """Log data access for compliance"""
        audit_entry = {
            'event_type': 'data_access',
            'user_id': user_id,
            'data_type': data_type,
            'record_count': len(record_ids),
            'record_ids': record_ids[:10],  # Log first 10 IDs
            'action': action,
            'ip_address': ip_address,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(json.dumps(audit_entry))
    
    def log_security_event(self, event_type: str, severity: str, description: str,
                          user_id: str = None, ip_address: str = None, details: Dict = None):
        """Log security events"""
        audit_entry = {
            'event_type': 'security',
            'security_event_type': event_type,
            'severity': severity,
            'description': description,
            'user_id': user_id,
            'ip_address': ip_address,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        self.logger.info(json.dumps(audit_entry))
    
    def log_admin_action(self, admin_user: str, action: str, target: str,
                        changes: Dict = None, ip_address: str = None):
        """Log administrative actions"""
        audit_entry = {
            'event_type': 'admin_action',
            'admin_user': admin_user,
            'action': action,
            'target': target,
            'changes': changes or {},
            'ip_address': ip_address,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(json.dumps(audit_entry))

class RBACManager:
    """Role-Based Access Control Manager"""
    
    def __init__(self):
        self.roles = self._load_roles_config()
        self.permissions = self._load_permissions_config()
    
    def _load_roles_config(self) -> Dict:
        """Load roles configuration"""
        default_roles = {
            'super_admin': {
                'description': 'Full system access',
                'permissions': ['*'],
                'inherits': []
            },
            'admin': {
                'description': 'Administrative access',
                'permissions': [
                    'user_management', 'system_config', 'audit_view',
                    'data_export', 'campaign_management', 'customer_management'
                ],
                'inherits': []
            },
            'marketing_manager': {
                'description': 'Marketing operations',
                'permissions': [
                    'campaign_create', 'campaign_edit', 'campaign_view', 
                    'customer_view', 'analytics_view', 'report_generate'
                ],
                'inherits': []
            },
            'data_analyst': {
                'description': 'Data analysis and reporting',
                'permissions': [
                    'customer_view', 'analytics_view', 'report_generate',
                    'data_export_limited', 'dashboard_view'
                ],
                'inherits': []
            },
            'customer_service': {
                'description': 'Customer support',
                'permissions': [
                    'customer_view', 'customer_edit_limited', 'support_tickets'
                ],
                'inherits': []
            },
            'auditor': {
                'description': 'Audit and compliance',
                'permissions': [
                    'audit_view', 'compliance_reports', 'data_lineage_view'
                ],
                'inherits': []
            },
            'viewer': {
                'description': 'Read-only access',
                'permissions': ['dashboard_view', 'report_view'],
                'inherits': []
            }
        }
        
        return default_roles
    
    def _load_permissions_config(self) -> Dict:
        """Load permissions configuration"""
        return {
            # User Management
            'user_management': 'Manage users and roles',
            'user_create': 'Create new users',
            'user_edit': 'Edit user details',
            'user_delete': 'Delete users',
            
            # System Configuration
            'system_config': 'Modify system configuration',
            'security_config': 'Modify security settings',
            'integration_config': 'Configure integrations',
            
            # Customer Management
            'customer_management': 'Full customer data access',
            'customer_view': 'View customer data',
            'customer_edit': 'Edit customer data',
            'customer_edit_limited': 'Limited customer editing',
            'customer_delete': 'Delete customer data',
            'customer_pii_access': 'Access PII data',
            
            # Campaign Management
            'campaign_management': 'Full campaign management',
            'campaign_create': 'Create campaigns',
            'campaign_edit': 'Edit campaigns',
            'campaign_view': 'View campaigns',
            'campaign_delete': 'Delete campaigns',
            
            # Analytics and Reporting
            'analytics_view': 'View analytics',
            'analytics_advanced': 'Advanced analytics access',
            'report_generate': 'Generate reports',
            'report_view': 'View reports',
            'dashboard_view': 'View dashboards',
            
            # Data Operations
            'data_export': 'Export all data',
            'data_export_limited': 'Limited data export',
            'data_import': 'Import data',
            'data_deletion': 'Delete data permanently',
            
            # Audit and Compliance
            'audit_view': 'View audit logs',
            'compliance_reports': 'Generate compliance reports',
            'data_lineage_view': 'View data lineage',
            
            # Support
            'support_tickets': 'Manage support tickets'
        }
    
    def check_permission(self, user_roles: List[str], required_permission: str) -> bool:
        """Check if user has required permission"""
        user_permissions = set()
        
        for role in user_roles:
            if role in self.roles:
                role_permissions = self.roles[role]['permissions']
                
                # Super admin wildcard
                if '*' in role_permissions:
                    return True
                
                user_permissions.update(role_permissions)
                
                # Check inherited roles
                for inherited_role in self.roles[role].get('inherits', []):
                    if inherited_role in self.roles:
                        user_permissions.update(self.roles[inherited_role]['permissions'])
        
        return required_permission in user_permissions
    
    def get_user_permissions(self, user_roles: List[str]) -> List[str]:
        """Get all permissions for user roles"""
        permissions = set()
        
        for role in user_roles:
            if role in self.roles:
                role_permissions = self.roles[role]['permissions']
                
                if '*' in role_permissions:
                    return list(self.permissions.keys())
                
                permissions.update(role_permissions)
        
        return list(permissions)

class SessionManager:
    """Secure session management"""
    
    def __init__(self):
        self.active_sessions = {}
        self.session_timeout = timedelta(hours=8)
        self.max_sessions_per_user = 5
    
    def create_session(self, user_id: str, ip_address: str, user_agent: str) -> str:
        """Create new session"""
        session_id = secrets.token_urlsafe(32)
        
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'is_active': True
        }
        
        # Clean up old sessions for user
        self._cleanup_user_sessions(user_id)
        
        self.active_sessions[session_id] = session_data
        
        return session_id
    
    def validate_session(self, session_id: str, ip_address: str = None) -> Dict:
        """Validate session and update activity"""
        if session_id not in self.active_sessions:
            return {'valid': False, 'reason': 'Session not found'}
        
        session = self.active_sessions[session_id]
        
        # Check if session expired
        if datetime.now() - session['last_activity'] > self.session_timeout:
            self.invalidate_session(session_id)
            return {'valid': False, 'reason': 'Session expired'}
        
        # Check IP address consistency (optional)
        if ip_address and session['ip_address'] != ip_address:
            # Log suspicious activity
            logger.warning(f"IP address mismatch for session {session_id}")
        
        # Update last activity
        session['last_activity'] = datetime.now()
        
        return {
            'valid': True,
            'user_id': session['user_id'],
            'session_data': session
        }
    
    def invalidate_session(self, session_id: str):
        """Invalidate session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    def invalidate_user_sessions(self, user_id: str):
        """Invalidate all sessions for a user"""
        sessions_to_remove = [
            sid for sid, session in self.active_sessions.items()
            if session['user_id'] == user_id
        ]
        
        for session_id in sessions_to_remove:
            self.invalidate_session(session_id)
    
    def _cleanup_user_sessions(self, user_id: str):
        """Clean up old sessions for user"""
        user_sessions = [
            (sid, session) for sid, session in self.active_sessions.items()
            if session['user_id'] == user_id
        ]
        
        # Remove oldest sessions if exceeding limit
        if len(user_sessions) >= self.max_sessions_per_user:
            user_sessions.sort(key=lambda x: x[1]['last_activity'])
            
            for session_id, _ in user_sessions[:-self.max_sessions_per_user + 1]:
                self.invalidate_session(session_id)

class ComplianceManager:
    """GDPR and compliance management"""
    
    def __init__(self):
        self.data_retention_policies = self._load_retention_policies()
        self.audit_logger = AuditLogger()
    
    def _load_retention_policies(self) -> Dict:
        """Load data retention policies"""
        return {
            'customer_data': {
                'retention_period_months': 84,  # 7 years
                'anonymize_after_months': 36,   # 3 years
                'auto_delete': False
            },
            'transaction_data': {
                'retention_period_months': 84,
                'anonymize_after_months': 60,
                'auto_delete': False
            },
            'marketing_data': {
                'retention_period_months': 24,
                'anonymize_after_months': 12,
                'auto_delete': True
            },
            'audit_logs': {
                'retention_period_months': 120,  # 10 years
                'anonymize_after_months': 84,
                'auto_delete': False
            },
            'session_data': {
                'retention_period_months': 3,
                'anonymize_after_months': 1,
                'auto_delete': True
            }
        }
    
    def process_data_subject_request(self, request_type: str, customer_id: str, 
                                   requester_details: Dict) -> Dict:
        """Process GDPR data subject requests"""
        
        self.audit_logger.log_admin_action(
            admin_user=requester_details.get('admin_user', 'system'),
            action=f'gdpr_request_{request_type}',
            target=customer_id,
            details=requester_details
        )
        
        if request_type == 'access':
            return self._handle_data_access_request(customer_id)
        elif request_type == 'portability':
            return self._handle_data_portability_request(customer_id)
        elif request_type == 'rectification':
            return self._handle_data_rectification_request(customer_id, requester_details)
        elif request_type == 'erasure':
            return self._handle_data_erasure_request(customer_id)
        elif request_type == 'restriction':
            return self._handle_processing_restriction_request(customer_id)
        else:
            return {'error': 'Unsupported request type'}
    
    def _handle_data_access_request(self, customer_id: str) -> Dict:
        """Handle data access request (Article 15)"""
        try:
            with get_db_context() as db:
                from core.database import Customer, Campaign, CameraData
                
                # Collect all customer data
                customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
                if not customer:
                    return {'error': 'Customer not found'}
                
                # Collect related data
                camera_data = db.query(CameraData).filter(
                    CameraData.demographics.contains(customer_id)
                ).all()
                
                # Prepare data export
                data_export = {
                    'request_type': 'data_access',
                    'customer_id': customer_id,
                    'generated_at': datetime.now().isoformat(),
                    'data': {
                        'personal_data': {
                            'customer_id': customer.customer_id,
                            'age': customer.age,
                            'gender': customer.gender,
                            'rating': customer.rating_id,
                            'registration_date': customer.created_at.isoformat(),
                            'last_updated': customer.updated_at.isoformat()
                        },
                        'processing_activities': [
                            'Customer segmentation analysis',
                            'Marketing campaign targeting',
                            'Service personalization',
                            'Business analytics'
                        ],
                        'data_sources': [
                            'Customer registration',
                            'Transaction records',
                            'Website interactions',
                            'Camera analytics (anonymized)'
                        ],
                        'retention_period': self.data_retention_policies['customer_data'],
                        'third_party_sharing': 'None',
                        'automated_decision_making': {
                            'customer_segmentation': 'Yes - for marketing personalization',
                            'churn_prediction': 'Yes - for retention campaigns'
                        }
                    }
                }
                
                return {
                    'success': True,
                    'data_export': data_export,
                    'format': 'json'
                }
                
        except Exception as e:
            logger.error(f"Data access request failed: {e}")
            return {'error': str(e)}
    
    def _handle_data_erasure_request(self, customer_id: str) -> Dict:
        """Handle right to erasure request (Article 17)"""
        try:
            with get_db_context() as db:
                from core.database import Customer
                
                customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
                if not customer:
                    return {'error': 'Customer not found'}
                
                # Check if erasure is legally permissible
                erasure_assessment = self._assess_erasure_request(customer)
                
                if not erasure_assessment['can_erase']:
                    return {
                        'success': False,
                        'reason': erasure_assessment['reason'],
                        'alternative': 'Data can be anonymized instead'
                    }
                
                # Perform erasure
                # In production, this would involve complex data cleanup across systems
                # For demo, we'll mark as erased
                customer.customer_id = f"ERASED_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                customer.gender = None
                customer.expanding_type_name = "ERASED"
                customer.expanding_channel_name = "ERASED"
                
                db.commit()
                
                return {
                    'success': True,
                    'erased_at': datetime.now().isoformat(),
                    'confirmation_id': f"ERASURE_{secrets.token_hex(8)}"
                }
                
        except Exception as e:
            logger.error(f"Data erasure request failed: {e}")
            return {'error': str(e)}
    
    def _assess_erasure_request(self, customer) -> Dict:
        """Assess if data can be legally erased"""
        # Check for legal obligations to retain data
        
        # In production, this would check:
        # - Ongoing legal proceedings
        # - Regulatory requirements
        # - Contractual obligations
        # - Legitimate interests
        
        return {
            'can_erase': True,
            'reason': 'No legal obligations to retain data'
        }
    
    def _handle_data_portability_request(self, customer_id: str) -> Dict:
        """Handle data portability request (Article 20)"""
        # Similar to access request but in machine-readable format
        access_result = self._handle_data_access_request(customer_id)
        
        if access_result.get('success'):
            return {
                'success': True,
                'portable_data': access_result['data_export'],
                'format': 'json',
                'download_url': f'/api/compliance/download/{customer_id}/portable'
            }
        else:
            return access_result
    
    def _handle_data_rectification_request(self, customer_id: str, details: Dict) -> Dict:
        """Handle data rectification request (Article 16)"""
        try:
            with get_db_context() as db:
                from core.database import Customer
                
                customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
                if not customer:
                    return {'error': 'Customer not found'}
                
                # Apply corrections (would validate in production)
                corrections = details.get('corrections', {})
                
                for field, new_value in corrections.items():
                    if hasattr(customer, field) and field in ['age', 'gender']:
                        setattr(customer, field, new_value)
                
                customer.updated_at = datetime.now()
                db.commit()
                
                return {
                    'success': True,
                    'rectified_fields': list(corrections.keys()),
                    'rectified_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Data rectification failed: {e}")
            return {'error': str(e)}
    
    def _handle_processing_restriction_request(self, customer_id: str) -> Dict:
        """Handle processing restriction request (Article 18)"""
        # In production, this would flag the customer record
        # to restrict certain types of processing
        
        return {
            'success': True,
            'restriction_applied': True,
            'restricted_activities': [
                'Marketing campaigns',
                'Automated decision making',
                'Data analytics (except anonymized)'
            ],
            'restriction_date': datetime.now().isoformat()
        }

# Security decorators
def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract current user from kwargs or request context
            current_user = kwargs.get('current_user')
            if not current_user:
                raise Exception("Authentication required")
            
            rbac = RBACManager()
            user_roles = current_user.get('roles', [])
            
            if not rbac.check_permission(user_roles, permission):
                audit_logger = AuditLogger()
                audit_logger.log_security_event(
                    event_type='unauthorized_access',
                    severity='warning',
                    description=f'User {current_user.get("user_id")} attempted to access {permission}',
                    user_id=current_user.get("user_id")
                )
                raise Exception(f"Permission '{permission}' required")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def rate_limit(max_requests: int = 100, time_window: int = 3600):
    """Rate limiting decorator"""
    request_counts = {}
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get client identifier (IP, user ID, etc.)
            client_id = kwargs.get('client_id') or 'unknown'
            current_time = time.time()
            
            # Clean old entries
            request_counts[client_id] = [
                req_time for req_time in request_counts.get(client_id, [])
                if current_time - req_time < time_window
            ]
            
            # Check rate limit
            if len(request_counts.get(client_id, [])) >= max_requests:
                audit_logger = AuditLogger()
                audit_logger.log_security_event(
                    event_type='rate_limit_exceeded',
                    severity='warning',
                    description=f'Rate limit exceeded for client {client_id}',
                    details={'max_requests': max_requests, 'time_window': time_window}
                )
                raise Exception("Rate limit exceeded")
            
            # Record request
            if client_id not in request_counts:
                request_counts[client_id] = []
            request_counts[client_id].append(current_time)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def audit_access(resource_type: str):
    """Decorator to audit resource access"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            audit_logger = AuditLogger()
            
            # Log access attempt
            if current_user:
                audit_logger.log_access(
                    user_id=current_user.get('user_id'),
                    resource=resource_type,
                    action=func.__name__,
                    ip_address=kwargs.get('client_ip'),
                    result='attempted'
                )
            
            try:
                result = func(*args, **kwargs)
                
                # Log successful access
                if current_user:
                    audit_logger.log_access(
                        user_id=current_user.get('user_id'),
                        resource=resource_type,
                        action=func.__name__,
                        result='success'
                    )
                
                return result
                
            except Exception as e:
                # Log failed access
                if current_user:
                    audit_logger.log_access(
                        user_id=current_user.get('user_id'),
                        resource=resource_type,
                        action=func.__name__,
                        result='failed',
                        details={'error': str(e)}
                    )
                raise
                
        return wrapper
    return decorator

# Global instances
advanced_security = AdvancedSecurityManager()
audit_logger = AuditLogger()
rbac_manager = RBACManager()
compliance_manager = ComplianceManager()
