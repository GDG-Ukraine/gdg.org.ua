from io import BytesIO
from json import dumps as json_dumps

from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook


event_parsers = {
    ('Registration id', (lambda _: _.EventParticipant.id)),
    ('Registration date', (lambda _: _.EventParticipant.register_date)),
    ('Event id', (lambda _: _.Event.id)),
    ('Event title', (lambda _: _.Event.title)),
    ('Name', (lambda _: _.User.full_name)),
    ('Gender', (lambda _: _.User.gender)),
    ('Nickname', (lambda _: _.User.nickname or '')),
    ('Email', (lambda _: _.User.email)),
    ('Phone', (lambda _: _.User.phone or '')),
    ('Google +', (lambda _: _.User.gplus)),
    ('City', (lambda _: _.User.hometown or '')),
    ('Company', (lambda _: _.User.company or '')),
    ('Position', (lambda _: _.User.position or '')),
    ('Website', (lambda _: _.User.www or '')),
    ('Experience level', (lambda _: _.User.experience_level or '')),
    ('Experience description', (lambda _: _.User.experience_desc or '')),
    ('Interests', (lambda _: _.User.interests or '')),
    ('Events visited', (lambda _: _.User.events_visited or '')),
    ('English knowledge', (lambda _: _.User.english_knowledge or '')),
    ('T-Shirt size', (lambda _: _.User.t_shirt_size or '')),
    ('Additional info', (lambda _: _.User.additional_info or '')),
    ('Extra fields', (lambda _: (
        json_dumps(_.EventParticipant.fields)
        if _.EventParticipant.fields
        else ''
    ))),
    ('Confirmed', (lambda _: _.EventParticipant.confirmed)),
}


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
        self._data_getters = tuple(data_getters)
        self._headers = tuple(headers)

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


def gen_participants_xlsx(data):
    return TableExporter(
        data=data,
        data_getters=map(lambda _: _[1], event_parsers),
        headers=map(lambda _: _[0], event_parsers),
    ).get_xlsx_content()
