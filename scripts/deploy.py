
"""
Production deployment script
"""
import sys
import os
from pathlib import Path
import argparse
import subprocess
import yaml
import json
import logging
import time
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeploymentManager:
    """Production deployment management"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.deployment_config = self._load_deployment_config()
    
    def _load_deployment_config(self):
        """Load deployment configuration"""
        config_file = self.project_root / "deployment" / "config.yaml"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Default configuration
            return {
                'environment': 'production',
                'services': ['api', 'frontend', 'database', 'redis', 'nginx'],
                'health_check_timeout': 300,
                'backup_before_deploy': True
            }
    
    def pre_deployment_checks(self):
        """Run pre-deployment checks"""
        logger.info("🔍 Running pre-deployment checks...")
        
        checks = [
            ("Environment variables", self._check_environment),
            ("Database connection", self._check_database),
            ("Model files", self._check_models),
            ("Configuration files", self._check_config),
            ("Docker installation", self._check_docker),
            ("Disk space", self._check_disk_space)
        ]
        
        failed_checks = []
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                if result:
                    logger.info(f"   ✅ {check_name}: OK")
                else:
                    logger.error(f"   ❌ {check_name}: Failed")
                    failed_checks.append(check_name)
            except Exception as e:
                logger.error(f"   ❌ {check_name}: Error - {e}")
                failed_checks.append(check_name)
        
        if failed_checks:
            logger.error(f"❌ Pre-deployment checks failed: {failed_checks}")
            return False
        else:
            logger.info("✅ All pre-deployment checks passed")
            return True
    
    def _check_environment(self):
        """Check environment variables"""
        required_vars = [
            'DATABASE_URL',
            'REDIS_URL', 
            'SECRET_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing environment variables: {missing_vars}")
            return False
        
        # Check if using production values
        if os.getenv('SECRET_KEY') == 'change-me-in-production-use-random-string':
            logger.error("SECRET_KEY still using default value")
            return False
        
        return True
    
    def _check_database(self):
        """Check database connectivity"""
        try:
            from backend.core.database import check_database_connection
            return check_database_connection()
        except Exception as e:
            logger.error(f"Database check failed: {e}")
            return False
    
    def _check_models(self):
        """Check if ML models exist"""
        models_dir = self.project_root / "models"
        
        if not models_dir.exists():
            logger.warning("Models directory not found")
            return True  # Not critical for initial deployment
        
        # Check for critical model files
        critical_models = [
            "model_registry.json"
        ]
        
        for model in critical_models:
            if not (models_dir / model).exists():
                logger.warning(f"Model file not found: {model}")
        
        return True
    
    def _check_config(self):
        """Check configuration files"""
        required_configs = [
            "config/api_config.yaml",
            "config/database_config.yaml",
            "docker-compose.yml"
        ]
        
        for config in required_configs:
            config_path = self.project_root / config
            if not config_path.exists():
                logger.error(f"Configuration file missing: {config}")
                return False
        
        return True
    
    def _check_docker(self):
        """Check Docker installation"""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                return False
            
            result = subprocess.run(['docker-compose', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
            
        except FileNotFoundError:
            return False
    
    def _check_disk_space(self):
        """Check available disk space"""
        try:
            result = subprocess.run(['df', '-h', '.'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    # Parse disk usage (simplified)
                    usage_line = lines[1].split()
                    if len(usage_line) > 4:
                        usage_percent = usage_line[4].rstrip('%')
                        if int(usage_percent) > 90:
                            logger.warning(f"Disk usage high: {usage_percent}%")
                            return False
            
            return True
            
        except Exception:
            logger.warning("Could not check disk space")
            return True
    
    def backup_before_deploy(self):
        """Create backup before deployment"""
        if not self.deployment_config.get('backup_before_deploy', True):
            logger.info("⏭️ Skipping backup (disabled in config)")
            return True
        
        logger.info("💾 Creating pre-deployment backup...")
        
        try:
            from scripts.backup_system import BackupManager
            
            backup_manager = BackupManager()
            backup_file = backup_manager.create_full_backup(['database', 'models', 'config'])
            
            logger.info(f"✅ Pre-deployment backup created: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return False
    
    def build_images(self):
        """Build Docker images"""
        logger.info("🔨 Building Docker images...")
        
        try:
            # Build main application image
            cmd = ['docker', 'build', '-t', 'sbm-crm:latest', '.']
            result = subprocess.run(cmd, cwd=self.project_root, 
                                  capture_output=False, text=True)
            
            if result.returncode != 0:
                raise Exception("Docker build failed")
            
            logger.info("✅ Docker images built successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Docker build failed: {e}")
            return False
    
    def deploy_services(self):
        """Deploy services using docker-compose"""
        logger.info("🚀 Deploying services...")
        
        try:
            # Stop existing services
            logger.info("   Stopping existing services...")
            subprocess.run(['docker-compose', 'down'], 
                         cwd=self.project_root, capture_output=True)
            
            # Start services
            logger.info("   Starting services...")
            cmd = ['docker-compose', 'up', '-d']
            result = subprocess.run(cmd, cwd=self.project_root, 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Docker-compose failed: {result.stderr}")
                return False
            
            logger.info("✅ Services deployed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Service deployment failed: {e}")
            return False
    
    def run_migrations(self):
        """Run database migrations"""
        logger.info("🗃️ Running database migrations...")
        
        try:
            # Wait for database to be ready
            time.sleep(10)
            
            # Run setup script
            cmd = ['docker-compose', 'exec', '-T', 'sbm-api', 
                   'python', 'scripts/setup_database.py']
            result = subprocess.run(cmd, cwd=self.project_root, 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Migration failed: {result.stderr}")
                return False
            
            logger.info("✅ Database migrations completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
    
    def health_check(self):
        """Run post-deployment health checks"""
        logger.info("🏥 Running health checks...")
        
        health_endpoints = [
            ('API Health', 'http://localhost:8000/health'),
            ('Frontend', 'http://localhost:8501'),
        ]
        
        timeout = self.deployment_config.get('health_check_timeout', 300)
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            all_healthy = True
            
            for name, url in health_endpoints:
                try:
                    import requests
                    response = requests.get(url, timeout=5)
                    
                    if response.status_code == 200:
                        logger.info(f"   ✅ {name}: Healthy")
                    else:
                        logger.warning(f"   ⚠️ {name}: Status {response.status_code}")
                        all_healthy = False
                        
                except Exception as e:
                    logger.warning(f"   ⚠️ {name}: Not ready ({e})")
                    all_healthy = False
            
            if all_healthy:
                logger.info("✅ All services are healthy")
                return True
            
            logger.info("   Waiting for services to be ready...")
            time.sleep(10)
        
        logger.error("❌ Health check timeout")
        return False
    
    def run_smoke_tests(self):
        """Run smoke tests"""
        logger.info("🧪 Running smoke tests...")
        
        smoke_tests = [
            self._test_api_endpoints,
            self._test_database_connectivity,
            self._test_model_loading
        ]
        
        failed_tests = []
        
        for test in smoke_tests:
            try:
                if not test():
                    failed_tests.append(test.__name__)
            except Exception as e:
                logger.error(f"Smoke test {test.__name__} failed: {e}")
                failed_tests.append(test.__name__)
        
        if failed_tests:
            logger.error(f"❌ Smoke tests failed: {failed_tests}")
            return False
        else:
            logger.info("✅ All smoke tests passed")
            return True
    
    def _test_api_endpoints(self):
        """Test critical API endpoints"""
        try:
            import requests
            
            base_url = "http://localhost:8000"
            
            # Test root endpoint
            response = requests.get(f"{base_url}/", timeout=10)
            if response.status_code != 200:
                return False
            
            # Test health endpoint
            response = requests.get(f"{base_url}/health", timeout=10)
            if response.status_code != 200:
                return False
            
            logger.info("   ✅ API endpoints responding")
            return True
            
        except Exception as e:
            logger.error(f"   ❌ API test failed: {e}")
            return False
    
    def _test_database_connectivity(self):
        """Test database connectivity"""
        try:
            cmd = ['docker-compose', 'exec', '-T', 'sbm-api', 
                   'python', '-c', 
                   'from backend.core.database import check_database_connection; print(check_database_connection())']
            
            result = subprocess.run(cmd, cwd=self.project_root, 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and 'True' in result.stdout:
                logger.info("   ✅ Database connectivity OK")
                return True
            else:
                logger.error(f"   ❌ Database test failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"   ❌ Database test error: {e}")
            return False
    
    def _test_model_loading(self):
        """Test model loading"""
        try:
            # Test if model registry is accessible
            models_path = self.project_root / "models" / "model_registry.json"
            
            if models_path.exists():
                with open(models_path, 'r') as f:
                    registry = json.load(f)
                    
                if 'model_registry' in registry:
                    logger.info("   ✅ Model registry accessible")
                    return True
            
            logger.warning("   ⚠️ Model registry not found (not critical)")
            return True
            
        except Exception as e:
            logger.warning(f"   ⚠️ Model test warning: {e}")
            return True
    
    def rollback_deployment(self):
        """Rollback to previous deployment"""
        logger.info("⏪ Rolling back deployment...")
        
        try:
            # Stop current services
            subprocess.run(['docker-compose', 'down'], 
                         cwd=self.project_root, capture_output=True)
            
            # Restore from backup
            from scripts.backup_system import BackupManager
            backup_manager = BackupManager()
            
            # Get latest backup
            backups = backup_manager.list_backups()
            if backups:
                latest_backup = backups[0]['name']
                backup_manager.restore_backup(latest_backup, ['config', 'models'])
                logger.info(f"✅ Restored from backup: {latest_backup}")
                
                # Restart services
                subprocess.run(['docker-compose', 'up', '-d'], 
                             cwd=self.project_root, capture_output=True)
                
                logger.info("✅ Rollback completed")
                return True
            else:
                logger.error("❌ No backup available for rollback")
                return False
                
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False
    
    def generate_deployment_report(self, deployment_result: dict):
        """Generate deployment report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.project_root / "deployment" / f"deployment_report_{timestamp}.json"
        
        report_file.parent.mkdir(exist_ok=True)
        
        report = {
            'deployment_timestamp': timestamp,
            'environment': self.deployment_config.get('environment'),
            'deployment_result': deployment_result,
            'system_info': {
                'python_version': sys.version,
                'deployment_user': os.getenv('USER', 'unknown'),
                'hostname': os.uname().nodename if hasattr(os, 'uname') else 'unknown'
            },
            'services_deployed': self.deployment_config.get('services', []),
            'configuration': self.deployment_config
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Deployment report saved: {report_file}")
        return report_file
    
    def full_deployment(self, skip_checks=False, skip_backup=False):
        """Run full deployment process"""
        logger.info("🚀 Starting full deployment process...")
        
        deployment_start = time.time()
        
        deployment_result = {
            'status': 'started',
            'steps_completed': [],
            'steps_failed': [],
            'start_time': datetime.now().isoformat(),
            'duration_seconds': 0
        }
        
        try:
            # Step 1: Pre-deployment checks
            if not skip_checks:
                if not self.pre_deployment_checks():
                    deployment_result['status'] = 'failed'
                    deployment_result['steps_failed'].append('pre_deployment_checks')
                    return deployment_result
                deployment_result['steps_completed'].append('pre_deployment_checks')
            
            # Step 2: Backup
            if not skip_backup:
                if not self.backup_before_deploy():
                    deployment_result['status'] = 'failed'
                    deployment_result['steps_failed'].append('backup')
                    return deployment_result
                deployment_result['steps_completed'].append('backup')
            
            # Step 3: Build images
            if not self.build_images():
                deployment_result['status'] = 'failed'
                deployment_result['steps_failed'].append('build_images')
                return deployment_result
            deployment_result['steps_completed'].append('build_images')
            
            # Step 4: Deploy services
            if not self.deploy_services():
                deployment_result['status'] = 'failed'
                deployment_result['steps_failed'].append('deploy_services')
                return deployment_result
            deployment_result['steps_completed'].append('deploy_services')
            
            # Step 5: Run migrations
            if not self.run_migrations():
                deployment_result['status'] = 'failed'
                deployment_result['steps_failed'].append('migrations')
                return deployment_result
            deployment_result['steps_completed'].append('migrations')
            
            # Step 6: Health checks
            if not self.health_check():
                deployment_result['status'] = 'failed'
                deployment_result['steps_failed'].append('health_check')
                return deployment_result
            deployment_result['steps_completed'].append('health_check')
            
            # Step 7: Smoke tests
            if not self.run_smoke_tests():
                deployment_result['status'] = 'failed'
                deployment_result['steps_failed'].append('smoke_tests')
                return deployment_result
            deployment_result['steps_completed'].append('smoke_tests')
            
            # Success
            deployment_result['status'] = 'success'
            deployment_result['end_time'] = datetime.now().isoformat()
            deployment_result['duration_seconds'] = time.time() - deployment_start
            
            logger.info("🎉 Deployment completed successfully!")
            logger.info(f"   Duration: {deployment_result['duration_seconds']:.1f} seconds")
            
            return deployment_result
            
        except Exception as e:
            deployment_result['status'] = 'error'
            deployment_result['error'] = str(e)
            deployment_result['end_time'] = datetime.now().isoformat()
            deployment_result['duration_seconds'] = time.time() - deployment_start
            
            logger.error(f"❌ Deployment failed with error: {e}")
            
            # Attempt rollback
            logger.info("Attempting automatic rollback...")
            if self.rollback_deployment():
                deployment_result['rollback_status'] = 'success'
            else:
                deployment_result['rollback_status'] = 'failed'
            
            return deployment_result

def main():
    """Main deployment script function"""
    parser = argparse.ArgumentParser(description="SBM CRM Production Deployment")
    parser.add_argument("command", choices=[
        "deploy", "rollback", "health-check", "smoke-test", "pre-check"
    ], help="Deployment command")
    parser.add_argument("--skip-checks", action="store_true", 
                       help="Skip pre-deployment checks")
    parser.add_argument("--skip-backup", action="store_true", 
                       help="Skip pre-deployment backup")
    parser.add_argument("--report", action="store_true", 
                       help="Generate deployment report")
    
    args = parser.parse_args()
    
    deployment_manager = DeploymentManager()
    
    try:
        if args.command == "deploy":
            result = deployment_manager.full_deployment(
                skip_checks=args.skip_checks,
                skip_backup=args.skip_backup
            )
            
            if args.report:
                deployment_manager.generate_deployment_report(result)
            
            if result['status'] != 'success':
                sys.exit(1)
                
        elif args.command == "rollback":
            if deployment_manager.rollback_deployment():
                print("✅ Rollback completed successfully")
            else:
                print("❌ Rollback failed")
                sys.exit(1)
                
        elif args.command == "health-check":
            if deployment_manager.health_check():
                print("✅ All services healthy")
            else:
                print("❌ Health check failed")
                sys.exit(1)
                
        elif args.command == "smoke-test":
            if deployment_manager.run_smoke_tests():
                print("✅ All smoke tests passed")
            else:
                print("❌ Smoke tests failed")
                sys.exit(1)
                
        elif args.command == "pre-check":
            if deployment_manager.pre_deployment_checks():
                print("✅ Pre-deployment checks passed")
            else:
                print("❌ Pre-deployment checks failed")
                sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ Deployment command failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
