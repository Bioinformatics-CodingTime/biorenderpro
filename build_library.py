#!/usr/bin/env python3
"""Rebuild from the approved manifest; never reimport quarantined downloads."""
from audit_library import rebuild
if __name__ == '__main__':
    rebuild()
