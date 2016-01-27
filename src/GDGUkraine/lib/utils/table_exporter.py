from io import BytesIO
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook


class TableExporter:
    """Class to export data to xlsx spreadsheet

    Usage:
        >>> exporter = TableExporter(
        ...     data=[{'a': 1, 'b': 2}, {'a': 3, 'b': 4}, ...],
        ...     data_getters=[
        ...         (lambda x: x['a']),
        ...         (lambda x: x['b']),
        ...     ],
        ...     headers=['first_column', 'second_column']
        ... )
        ...
        >>> binary_xlsx = exporter.get_xlsx_content()
    """
    def __init__(self, data, data_getters, headers=None):
        """Creates a new TableExporter

        Args:
            data (iterable): Data source of the spreadsheet. It is an iterable,
                each item of which contains sufficient data for creating a
                row in spreadsheet
            data_getters (iterable): Iterable of functions, which are applied
                to each row of data to get a spreadsheet row
            headers (iterable) [Optional]: list of table headers
        """
        self._data = data
        self._data_getters = data_getters
        self._headers = headers

    def _get_row_data(self, data):
        """Applies getter functions to data row and returns a row to
        be inserted to the spreadsheet

        Args:
            data (Any): some portion of data.

        Returns:
            (list): list of results of applying data getter functions to input
            data
        """
        return [f(data) for f in self._data_getters]

    def get_xlsx_content(self):
        """Prepares binary xlsx content from exporter

        Returns:
            (BytesIO): bytes of xlsx file
        """
        wb = Workbook()
        ws = wb.active
        if self._headers:
            ws.append(self._headers)
        for row in self._data:
            ws.append(self._get_row_data(row))
        return BytesIO(save_virtual_workbook(wb))
