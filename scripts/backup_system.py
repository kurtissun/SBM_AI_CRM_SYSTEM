
"""
System backup and recovery script
"""
import sys
import os
from pathlib import Path
import argparse
import shutil
import tarfile
import gzip
import json
import logging
from datetime import datetime, timedelta
import subprocess

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.core.config import settings
from backend.core.database import SessionLocal, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackupManager:
    """Comprehensive backup and recovery system"""
    
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        self.components = {
            'database': self.backup_database,
            'models': self.backup_models,
            'data': self.backup_data,
            'config': self.backup_config,
            'logs': self.backup_logs
        }
    
    def create_full_backup(self, include_components=None):
        """Create full system backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"sbm_crm_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        logger.info(f"🔄 Creating full backup: {backup_name}")
        
        components_to_backup = include_components or list(self.components.keys())
        backup_manifest = {
            'backup_name': backup_name,
            'timestamp': timestamp,
            'components': [],
            'system_info': self._get_system_info(),
            'backup_size': 0
        }
        
        total_size = 0
        
        for component in components_to_backup:
            if component in self.components:
                try:
                    logger.info(f"   📦 Backing up {component}...")
                    component_path = backup_path / component
                    component_path.mkdir(exist_ok=True)
                    
                    size = self.components[component](component_path)
                    total_size += size
                    
                    backup_manifest['components'].append({
                        'name': component,
                        'status': 'success',
                        'size_mb': size / (1024 * 1024),
                        'path': str(component_path.relative_to(self.backup_dir))
                    })
                    
                    logger.info(f"   ✅ {component} backup completed ({size / (1024 * 1024):.1f} MB)")
                    
                except Exception as e:
                    logger.error(f"   ❌ {component} backup failed: {e}")
                    backup_manifest['components'].append({
                        'name': component,
                        'status': 'failed',
                        'error': str(e)
                    })
        
        backup_manifest['backup_size'] = total_size
        
        # Save manifest
        with open(backup_path / 'manifest.json', 'w') as f:
            json.dump(backup_manifest, f, indent=2)
        
        # Create compressed archive
        archive_path = self._create_archive(backup_path)
        
        # Clean up uncompressed backup
        if archive_path and archive_path.exists():
            shutil.rmtree(backup_path)
            
        logger.info(f"🎉 Full backup completed: {archive_path}")
        logger.info(f"   Total size: {total_size / (1024 * 1024):.1f} MB")
        
        return archive_path
    
    def backup_database(self, backup_path: Path) -> int:
        """Backup database"""
        try:
            # PostgreSQL backup
            if settings.DATABASE_URL.startswith('postgresql'):
                dump_file = backup_path / 'database_dump.sql'
                
                # Extract connection details from DATABASE_URL
                # postgresql://user:password@host:port/database
                url_parts = settings.DATABASE_URL.replace('postgresql://', '').split('/')
                connection_part = url_parts[0]
                database_name = url_parts[1] if len(url_parts) > 1 else 'sbm_crm'
                
                user_host = connection_part.split('@')
                if len(user_host) > 1:
                    user_pass = user_host[0].split(':')
                    host_port = user_host[1].split(':')
                    
                    user = user_pass[0] if len(user_pass) > 0 else 'postgres'
                    password = user_pass[1] if len(user_pass) > 1 else ''
                    host = host_port[0] if len(host_port) > 0 else 'localhost'
                    port = host_port[1] if len(host_port) > 1 else '5432'
                    
                    # Use pg_dump
                    env = os.environ.copy()
                    if password:
                        env['PGPASSWORD'] = password
                    
                    cmd = [
                        'pg_dump',
                        '-h', host,
                        '-p', port,
                        '-U', user,
                        '-d', database_name,
                        '-f', str(dump_file),
                        '--verbose'
                    ]
                    
                    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        raise Exception(f"pg_dump failed: {result.stderr}")
                    
                    return dump_file.stat().st_size
                
            # SQLite backup
            elif settings.DATABASE_URL.startswith('sqlite'):
                db_file = settings.DATABASE_URL.replace('sqlite:///', '')
                if Path(db_file).exists():
                    shutil.copy2(db_file, backup_path / 'database.db')
                    return (backup_path / 'database.db').stat().st_size
            
            # Fallback: Export as CSV
            return self._export_tables_csv(backup_path)
            
        except Exception as e:
            logger.warning(f"Database backup method failed, using CSV export: {e}")
            return self._export_tables_csv(backup_path)
    
    def _export_tables_csv(self, backup_path: Path) -> int:
        """Export database tables as CSV files"""
        total_size = 0
        
        try:
            import pandas as pd
            
            with SessionLocal() as db:
                # Export customers
                customers_df = pd.read_sql("SELECT * FROM customers", db.bind)
                customers_file = backup_path / 'customers.csv'
                customers_df.to_csv(customers_file, index=False)
                total_size += customers_file.stat().st_size
                
                # Export campaigns
                campaigns_df = pd.read_sql("SELECT * FROM campaigns", db.bind)
                campaigns_file = backup_path / 'campaigns.csv'
                campaigns_df.to_csv(campaigns_file, index=False)
                total_size += campaigns_file.stat().st_size
                
                # Export camera_data
                try:
                    camera_df = pd.read_sql("SELECT * FROM camera_data", db.bind)
                    camera_file = backup_path / 'camera_data.csv'
                    camera_df.to_csv(camera_file, index=False)
                    total_size += camera_file.stat().st_size
                except:
                    logger.warning("Could not export camera_data table")
                
                # Export reports
                try:
                    reports_df = pd.read_sql("SELECT * FROM reports", db.bind)
                    reports_file = backup_path / 'reports.csv'
                    reports_df.to_csv(reports_file, index=False)
                    total_size += reports_file.stat().st_size
                except:
                    logger.warning("Could not export reports table")
            
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            
        return total_size
    
    def backup_models(self, backup_path: Path) -> int:
        """Backup ML models and model registry"""
        total_size = 0
        models_dir = Path("models")
        
        if models_dir.exists():
            # Copy entire models directory
            backup_models_dir = backup_path / "models"
            shutil.copytree(models_dir, backup_models_dir)
            
            # Calculate total size
            for file_path in backup_models_dir.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        
        return total_size
    
    def backup_data(self, backup_path: Path) -> int:
        """Backup data files"""
        total_size = 0
        data_dir = Path("data")
        
        if data_dir.exists():
            # Copy data directory (excluding raw data which might be large)
            backup_data_dir = backup_path / "data"
            backup_data_dir.mkdir(exist_ok=True)
            
            # Backup processed data
            if (data_dir / "processed").exists():
                shutil.copytree(data_dir / "processed", backup_data_dir / "processed")
            
            # Backup reports
            if (data_dir / "reports").exists():
                shutil.copytree(data_dir / "reports", backup_data_dir / "reports")
            
            # Backup configurations
            for config_file in data_dir.glob("*.json"):
                shutil.copy2(config_file, backup_data_dir)
            
            # Calculate size
            for file_path in backup_data_dir.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        
        return total_size
    
    def backup_config(self, backup_path: Path) -> int:
        """Backup configuration files"""
        total_size = 0
        
        config_files = [
            "config/api_config.yaml",
            "config/database_config.yaml", 
            "config/ml_config.yaml",
            ".env",
            "docker-compose.yml",
            "docker-compose.dev.yml",
            "nginx/nginx.conf"
        ]
        
        for config_file in config_files:
            config_path = Path(config_file)
            if config_path.exists():
                backup_file = backup_path / config_path.name
                shutil.copy2(config_path, backup_file)
                total_size += backup_file.stat().st_size
        
        return total_size
    
    def backup_logs(self, backup_path: Path) -> int:
        """Backup recent log files"""
        total_size = 0
        logs_dir = Path("logs")
        
        if logs_dir.exists():
            backup_logs_dir = backup_path / "logs"
            backup_logs_dir.mkdir(exist_ok=True)
            
            # Only backup logs from last 7 days
            cutoff_date = datetime.now() - timedelta(days=7)
            
            for log_file in logs_dir.glob("*.log*"):
                if log_file.is_file():
                    file_modified = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_modified > cutoff_date:
                        shutil.copy2(log_file, backup_logs_dir)
                        total_size += (backup_logs_dir / log_file.name).stat().st_size
        
        return total_size
    
    def _create_archive(self, backup_path: Path) -> Path:
        """Create compressed archive of backup"""
        archive_path = backup_path.with_suffix('.tar.gz')
        
        try:
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(backup_path, arcname=backup_path.name)
            
            return archive_path
            
        except Exception as e:
            logger.error(f"Failed to create archive: {e}")
            return backup_path
    
    def _get_system_info(self) -> dict:
        """Get system information for backup manifest"""
        return {
            'hostname': os.uname().nodename if hasattr(os, 'uname') else 'unknown',
            'python_version': sys.version,
            'environment': settings.ENVIRONMENT,
            'database_url': settings.DATABASE_URL.split('@')[0] + '@***',  # Hide password
            'backup_time': datetime.now().isoformat()
        }
    
    def list_backups(self) -> list:
        """List available backups"""
        backups = []
        
        for backup_file in self.backup_dir.glob("sbm_crm_backup_*.tar.gz"):
            try:
                # Extract timestamp from filename
                timestamp_str = backup_file.stem.split('_')[-2] + '_' + backup_file.stem.split('_')[-1]
                timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                
                backups.append({
                    'name': backup_file.name,
                    'path': str(backup_file),
                    'timestamp': timestamp.isoformat(),
                    'size_mb': backup_file.stat().st_size / (1024 * 1024),
                    'age_days': (datetime.now() - timestamp).days
                })
                
            except Exception as e:
                logger.warning(f"Could not parse backup file {backup_file}: {e}")
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        return backups
    
    def restore_backup(self, backup_name: str, components: list = None):
        """Restore from backup"""
        backup_file = self.backup_dir / backup_name
        
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_name}")
        
        logger.info(f"🔄 Restoring from backup: {backup_name}")
        
        # Extract backup
        extract_dir = self.backup_dir / "temp_restore"
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extract_dir.mkdir()
        
        try:
            with tarfile.open(backup_file, 'r:gz') as tar:
                tar.extractall(extract_dir)
            
            # Find the extracted backup directory
            extracted_dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
            if not extracted_dirs:
                raise Exception("No backup directory found in archive")
            
            backup_content_dir = extracted_dirs[0]
            
            # Load manifest
            manifest_file = backup_content_dir / 'manifest.json'
            if manifest_file.exists():
                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)
                logger.info(f"Backup created: {manifest['timestamp']}")
            
            # Restore components
            components_to_restore = components or ['models', 'data', 'config']
            
            for component in components_to_restore:
                component_dir = backup_content_dir / component
                if component_dir.exists():
                    logger.info(f"   📦 Restoring {component}...")
                    self._restore_component(component, component_dir)
                    logger.info(f"   ✅ {component} restored")
                else:
                    logger.warning(f"   ⚠️ {component} not found in backup")
            
            logger.info("🎉 Restore completed successfully")
            
        finally:
            # Clean up temporary files
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
    
    def _restore_component(self, component: str, backup_component_dir: Path):
        """Restore a specific component"""
        if component == 'models':
            models_dir = Path("models")
            if models_dir.exists():
                shutil.rmtree(models_dir)
            shutil.copytree(backup_component_dir / "models", models_dir)
            
        elif component == 'data':
            data_dir = Path("data")
            # Only restore processed data and reports, not raw data
            if (backup_component_dir / "data" / "processed").exists():
                if (data_dir / "processed").exists():
                    shutil.rmtree(data_dir / "processed")
                shutil.copytree(backup_component_dir / "data" / "processed", data_dir / "processed")
            
            if (backup_component_dir / "data" / "reports").exists():
                if (data_dir / "reports").exists():
                    shutil.rmtree(data_dir / "reports")
                shutil.copytree(backup_component_dir / "data" / "reports", data_dir / "reports")
            
        elif component == 'config':
            # Restore configuration files
            for config_file in backup_component_dir.glob("*"):
                if config_file.is_file():
                    # Determine where to restore the file
                    if config_file.name.endswith('.yaml'):
                        dest_path = Path("config") / config_file.name
                        dest_path.parent.mkdir(exist_ok=True)
                    elif config_file.name == "nginx.conf":
                        dest_path = Path("nginx") / config_file.name
                        dest_path.parent.mkdir(exist_ok=True)
                    else:
                        dest_path = Path(config_file.name)
                    
                    shutil.copy2(config_file, dest_path)
    
    def cleanup_old_backups(self, keep_days: int = 30):
        """Clean up old backup files"""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        deleted_count = 0
        
        for backup_file in self.backup_dir.glob("sbm_crm_backup_*.tar.gz"):
            try:
                # Extract timestamp from filename
                timestamp_str = backup_file.stem.split('_')[-2] + '_' + backup_file.stem.split('_')[-1]
                timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                
                if timestamp < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old backup: {backup_file.name}")
                    
            except Exception as e:
                logger.warning(f"Could not process backup file {backup_file}: {e}")
        
        logger.info(f"✅ Cleanup completed. Deleted {deleted_count} old backups")

def main():
    """Main backup script function"""
    parser = argparse.ArgumentParser(description="SBM CRM System Backup Manager")
    parser.add_argument("command", choices=[
        "create", "list", "restore", "cleanup"
    ], help="Backup command")
    parser.add_argument("--components", nargs="+", 
                       choices=["database", "models", "data", "config", "logs"],
                       help="Components to backup/restore")
    parser.add_argument("--backup-name", help="Backup name for restore command")
    parser.add_argument("--keep-days", type=int, default=30, 
                       help="Days to keep backups (for cleanup command)")
    
    args = parser.parse_args()
    
    backup_manager = BackupManager()
    
    try:
        if args.command == "create":
            backup_file = backup_manager.create_full_backup(args.components)
            print(f"Backup created: {backup_file}")
            
        elif args.command == "list":
            backups = backup_manager.list_backups()
            if backups:
                print("Available backups:")
                for backup in backups:
                    print(f"  {backup['name']} - {backup['size_mb']:.1f} MB - {backup['age_days']} days old")
            else:
                print("No backups found")
                
        elif args.command == "restore":
            if not args.backup_name:
                print("Error: --backup-name required for restore command")
                sys.exit(1)
            backup_manager.restore_backup(args.backup_name, args.components)
            print("Restore completed successfully")
            
        elif args.command == "cleanup":
            backup_manager.cleanup_old_backups(args.keep_days)
            print(f"Cleanup completed (kept backups newer than {args.keep_days} days)")
            
    except Exception as e:
        logger.error(f"❌ Backup operation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()