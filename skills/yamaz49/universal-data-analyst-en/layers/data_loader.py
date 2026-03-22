"""
Data Loader

Supports loading multiple data formats:
- CSV/TSV
- Excel (.xlsx/.xls)
- Parquet
- JSON
- SQL database
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field
from enum import Enum
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFormat(Enum):
    """Supported data formats"""
    CSV = "csv"
    TSV = "tsv"
    EXCEL = "excel"
    PARQUET = "parquet"
    JSON = "json"
    SQL = "sql"
    UNKNOWN = "unknown"


@dataclass
class DataLoadResult:
    """Data load result"""
    success: bool
    data: Optional[pd.DataFrame] = None
    format: DataFormat = DataFormat.UNKNOWN
    file_path: Optional[str] = None
    rows: int = 0
    columns: int = 0
    memory_usage_mb: float = 0.0
    load_time_ms: float = 0.0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    encoding: str = "utf-8"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'format': self.format.value,
            'file_path': self.file_path,
            'rows': self.rows,
            'columns': self.columns,
            'memory_usage_mb': round(self.memory_usage_mb, 2),
            'load_time_ms': round(self.load_time_ms, 2),
            'warnings': self.warnings,
            'errors': self.errors,
        }


class DataLoader:
    """
    Data Loader

    Supports automatic format detection and multiple data sources.
    """

    tool_name = "data_loader"
    tool_description = "Load data files in various formats"

    # Format mapping
    EXTENSION_MAP = {
        '.csv': DataFormat.CSV,
        '.tsv': DataFormat.TSV,
        '.txt': DataFormat.CSV,
        '.xlsx': DataFormat.EXCEL,
        '.xls': DataFormat.EXCEL,
        '.parquet': DataFormat.PARQUET,
        '.pq': DataFormat.PARQUET,
        '.json': DataFormat.JSON,
    }

    def __init__(self):
        self._load_stats = []

    def detect_format(self, file_path: Union[str, Path]) -> DataFormat:
        """Detect file format"""
        path = Path(file_path)
        ext = path.suffix.lower()

        # Check extension
        if ext in self.EXTENSION_MAP:
            return self.EXTENSION_MAP[ext]

        # Try reading the first few bytes
        try:
            with open(path, 'rb') as f:
                header = f.read(8)
                # Parquet files start with PAR1
                if header[:4] == b'PAR1':
                    return DataFormat.PARQUET
        except:
            pass

        return DataFormat.UNKNOWN

    def execute(self, params: Dict[str, Any]) -> DataLoadResult:
        """
        Execute data loading

        Args:
            params: {
                'file_path': str,  # file path
                'format': str,     # optional, force format
                'encoding': str,   # optional, default utf-8
                'sheet_name': str, # Excel only
                'sql_query': str,  # SQL only
                'connection_string': str, # SQL only
                'limit': int,      # limit number of rows loaded
                'parse_dates': list, # date columns
                'dtype': dict,     # specify data types
            }
        """
        start_time = time.time()

        file_path = params.get('file_path')
        if not file_path:
            return DataLoadResult(
                success=False,
                errors=["Missing required parameter: file_path"]
            )

        # Detect or get format
        format_hint = params.get('format')
        if format_hint:
            data_format = DataFormat(format_hint.lower())
        else:
            data_format = self.detect_format(file_path)

        if data_format == DataFormat.UNKNOWN:
            return DataLoadResult(
                success=False,
                file_path=str(file_path),
                errors=[f"Cannot detect file format: {file_path}"]
            )

        # Load by format
        try:
            result = self._load_by_format(
                file_path=file_path,
                data_format=data_format,
                params=params
            )
        except Exception as e:
            load_time = (time.time() - start_time) * 1000
            return DataLoadResult(
                success=False,
                file_path=str(file_path),
                format=data_format,
                load_time_ms=load_time,
                errors=[f"Load failed: {str(e)}"]
            )

        result.load_time_ms = (time.time() - start_time) * 1000
        return result

    def _load_by_format(self, file_path: str, data_format: DataFormat,
                        params: Dict[str, Any]) -> DataLoadResult:
        """Load data by format"""

        encoding = params.get('encoding', 'utf-8')
        limit = params.get('limit')
        parse_dates = params.get('parse_dates', [])
        dtype = params.get('dtype')

        result = DataLoadResult(
            success=True,
            file_path=str(file_path),
            format=data_format,
            encoding=encoding
        )

        if data_format == DataFormat.CSV:
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                parse_dates=parse_dates,
                dtype=dtype,
                low_memory=False
            )

        elif data_format == DataFormat.TSV:
            df = pd.read_csv(
                file_path,
                sep='\t',
                encoding=encoding,
                parse_dates=parse_dates,
                dtype=dtype,
                low_memory=False
            )

        elif data_format == DataFormat.EXCEL:
            sheet_name = params.get('sheet_name', 0)
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                parse_dates=parse_dates,
                dtype=dtype
            )

        elif data_format == DataFormat.PARQUET:
            df = pd.read_parquet(file_path)

        elif data_format == DataFormat.JSON:
            df = pd.read_json(file_path)

        elif data_format == DataFormat.SQL:
            connection_string = params.get('connection_string')
            sql_query = params.get('sql_query')

            if not connection_string or not sql_query:
                result.success = False
                result.errors.append("SQL loading requires both connection_string and sql_query")
                return result

            from sqlalchemy import create_engine
            engine = create_engine(connection_string)
            df = pd.read_sql(sql_query, engine, parse_dates=parse_dates)

        else:
            result.success = False
            result.errors.append(f"Unsupported format: {data_format}")
            return result

        # Limit rows
        if limit and len(df) > limit:
            result.warnings.append(f"Row count exceeds limit {limit}, truncated")
            df = df.head(limit)

        # Populate result
        result.data = df
        result.rows = len(df)
        result.columns = len(df.columns)
        result.memory_usage_mb = df.memory_usage(deep=True).sum() / 1024 / 1024

        # Record stats
        self._load_stats.append(result.to_dict())

        logger.info(f"Load successful: {result.rows} rows x {result.columns} columns, "
                   f"{result.memory_usage_mb:.2f} MB")

        return result

    def load_csv(self, file_path: str, **kwargs) -> DataLoadResult:
        """Convenience method: load CSV"""
        params = {'file_path': file_path, 'format': 'csv'}
        params.update(kwargs)
        return self.execute(params)

    def load_excel(self, file_path: str, sheet_name=0, **kwargs) -> DataLoadResult:
        """Convenience method: load Excel"""
        params = {
            'file_path': file_path,
            'format': 'excel',
            'sheet_name': sheet_name
        }
        params.update(kwargs)
        return self.execute(params)

    def load_parquet(self, file_path: str, **kwargs) -> DataLoadResult:
        """Convenience method: load Parquet"""
        params = {'file_path': file_path, 'format': 'parquet'}
        params.update(kwargs)
        return self.execute(params)

    def load_sql(self, connection_string: str, sql_query: str,
                 **kwargs) -> DataLoadResult:
        """Convenience method: load SQL"""
        params = {
            'file_path': 'sql_query',
            'format': 'sql',
            'connection_string': connection_string,
            'sql_query': sql_query
        }
        params.update(kwargs)
        return self.execute(params)

    def get_load_stats(self) -> List[Dict]:
        """Get load statistics"""
        return self._load_stats.copy()


# Global instance
loader = DataLoader()

# Convenience function
def load(file_path: str, **kwargs) -> DataLoadResult:
    """Convenience load function"""
    params = {'file_path': file_path}
    params.update(kwargs)
    return loader.execute(params)
