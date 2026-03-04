"""
Virus scanning via ClamAV daemon.

Requires: pip install pyclamd
Requires: ClamAV daemon running (clamd)

Fail-closed: if scanner unavailable, files are REJECTED (not accepted).
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class VirusScanService:
    """Scans files for malware using ClamAV."""

    @staticmethod
    def scan_file(file_path: str) -> Dict[str, Any]:
        """
        Scan a file with ClamAV.

        Returns:
            {'clean': bool, 'threat': str | None}
        """
        try:
            import pyclamd
        except ImportError:
            logger.error(
                "pyclamd not installed — rejecting upload for safety"
            )
            return {'clean': False, 'threat': 'Scanner unavailable'}

        try:
            cd = pyclamd.ClamdUnixSocket()
            cd.ping()
        except Exception:
            try:
                cd = pyclamd.ClamdNetworkSocket()
                cd.ping()
            except Exception as e:
                logger.error("ClamAV daemon unreachable: %s", e)
                return {'clean': False, 'threat': 'Scanner unreachable'}

        try:
            result = cd.scan_file(file_path)
            if result is None:
                return {'clean': True, 'threat': None}

            status = result.get(file_path)
            if status and status[0] == 'FOUND':
                logger.warning(
                    "Virus found in %s: %s", file_path, status[1]
                )
                return {'clean': False, 'threat': status[1]}

            return {'clean': True, 'threat': None}
        except Exception as e:
            logger.error("ClamAV scan failed for %s: %s", file_path, e)
            return {'clean': False, 'threat': f'Scan error: {e}'}
