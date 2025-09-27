"""Setup script for GDELT Analysis Pipeline."""

import os
import sys
import subprocess


def check_python_version():
    """Check Python version compatibility."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def install_requirements():
    """Install required packages."""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False


def check_credentials():
    """Check Google Cloud credentials."""
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        print("⚠️  GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
        print("Please set it to your service account key file path:")
        print("export GOOGLE_APPLICATION_CREDENTIALS='/path/to/your/service-account-key.json'")
        return False
    
    if not os.path.exists(creds_path):
        print(f"❌ Credentials file not found: {creds_path}")
        return False
        
    print(f"✅ Credentials file found: {creds_path}")
    return True


def create_directories():
    """Create necessary directories."""
    directories = [
        'data',
        'data/cache', 
        'data/exports',
        'vizuals',
        'vizuals/plots',
        'vizuals/graphs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    return True


def main():
    """Main setup function."""
    print("🌍 GDELT Analysis Pipeline Setup")
    print("=" * 40)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Install requirements
    if success and not install_requirements():
        success = False
    
    # Check credentials
    if success and not check_credentials():
        success = False
        print("\n💡 You can continue setup after setting credentials")
    
    # Create directories
    if not create_directories():
        success = False
    
    print("\n" + "=" * 40)
    
    if success:
        print("✅ Setup completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Test the pipeline: python main.py --test")
        print("2. Run quick analysis: python main.py --quick --visualize")
        print("3. See full options: python main.py --help")
    else:
        print("❌ Setup completed with issues")
        print("Please resolve the issues above and run setup again")
    
    return success


if __name__ == "__main__":
    main()