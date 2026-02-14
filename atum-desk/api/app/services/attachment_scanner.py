"""
ATUM DESK - Attachment Scanner Service
Provides virus/malware scanning using ClamAV

This service integrates with the upload pipeline to scan files before
they are served to users.
"""
import os
import logging
from datetime import datetime
from enum import Enum
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ScanStatus(Enum):
    PENDING = "pending"
    CLEAN = "clean"
    INFECTED = "infected"
    QUARANTINED = "quarantined"
    ERROR = "error"


@dataclass
class ScanResult:
    status: ScanStatus
    signature: Optional[str] = None
    scanned_at: Optional[datetime] = None
    scanner_version: Optional[str] = None
    result_text: Optional[str] = None


class AttachmentScanner:
    """ClamAV-based attachment scanner"""
    
    def __init__(self):
        self.clamav_available = False
        self.scanner_version = None
        self._init_clamav()
    
    def _init_clamav(self):
        """Initialize ClamAV connection"""
        try:
            import clamd
            self.cd = clamd.ClamdUnixSocket()
            version = self.cd.version()
            self.scanner_version = version
            self.clamav_available = True
            logger.info("ClamAV initialized successfully", version=version)
        except ImportError:
            logger.warning("python-clamav not installed - scanning disabled")
            self.clamav_available = False
        except Exception as e:
            logger.warning("Failed to connect to ClamAV daemon", error=str(e))
            self.clamav_available = False
    
    async def scan(self, file_path: str) -> ScanResult:
        """
        Scan a file for malware.
        
        Args:
            file_path: Path to file to scan
            
        Returns:
            ScanResult with status and details
        """
        if not self.clamav_available:
            logger.warning("ClamAV not available, skipping scan")
            return ScanResult(
                status=ScanStatus.ERROR,
                result_text="Scanner not available",
                scanned_at=datetime.utcnow()
            )
        
        try:
            result = self.cd.scan(file_path)
            
            if result:
                file_name = list(result.keys())[0]
                scan_result = result[file_name]
                
                status = scan_result[0]
                
                if status == "OK":
                    return ScanResult(
                        status=ScanStatus.CLEAN,
                        scanned_at=datetime.utcnow(),
                        scanner_version=self.scanner_version,
                        result_text="No threats found"
                    )
                elif status == "FOUND":
                    return ScanResult(
                        status=ScanStatus.INFECTED,
                        signature=scan_result[1],
                        scanned_at=datetime.utcnow(),
                        scanner_version=self.scanner_version,
                        result_text=f"Threat detected: {scan_result[1]}"
                    )
                else:
                    return ScanResult(
                        status=ScanStatus.ERROR,
                        scanned_at=datetime.utcnow(),
                        scanner_version=self.scanner_version,
                        result_text=f"Unexpected scan result: {status}"
                    )
            else:
                return ScanResult(
                    status=ScanStatus.ERROR,
                    result_text="No scan result returned",
                    scanned_at=datetime.utcnow()
                )
                
        except Exception as e:
            logger.error("Scan failed", error=str(e))
            return ScanResult(
                status=ScanStatus.ERROR,
                result_text=f"Scan error: {str(e)}",
                scanned_at=datetime.utcnow()
            )
    
    async def scan_and_quarantine(self, file_path: str, quarantine_dir: str) -> ScanResult:
        """
        Scan a file and quarantine if infected.
        
        Args:
            file_path: Path to file to scan
            quarantine_dir: Directory for quarantined files
            
        Returns:
            ScanResult with status and details
        """
        result = await self.scan(file_path)
        
        if result.status == ScanStatus.INFECTED:
            try:
                os.makedirs(quarantine_dir, exist_ok=True)
                
                import shutil
                file_name = os.path.basename(file_path)
                quarantine_path = os.path.join(quarantine_dir, f"{file_name}.quarantined")
                
                shutil.move(file_path, quarantine_path)
                
                result.status = ScanStatus.QUARANTINED
                result.result_text = f"File quarantined to: {quarantine_path}"
                
                logger.warning("File quarantined", 
                             original_path=file_path,
                             quarantine_path=quarantine_path,
                             signature=result.signature)
                
            except Exception as e:
                logger.error("Failed to quarantine file", error=str(e))
                result.result_text = f"Quarantine failed: {str(e)}"
        
        return result


# Global scanner instance
_scanner: Optional[AttachmentScanner] = None


def get_scanner() -> AttachmentScanner:
    """Get or create the global scanner instance"""
    global _scanner
    if _scanner is None:
        _scanner = AttachmentScanner()
    return _scanner


async def scan_attachment(file_path: str, quarantine_dir: str = "/data/ATUM DESK/atum-desk/data/quarantine") -> ScanResult:
    """
    Convenience function to scan an attachment.
    
    Args:
        file_path: Path to file to scan
        quarantine_dir: Directory for quarantined files
        
    Returns:
        ScanResult with status and details
    """
    scanner = get_scanner()
    return await scanner.scan_and_quarantine(file_path, quarantine_dir)
