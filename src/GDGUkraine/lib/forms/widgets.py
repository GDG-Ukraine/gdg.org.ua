from wtforms.widgets import HTMLString


class InlineWidget(object):
    """
    Renders a list of fields inline.
    This is used for fields which encapsulate many inner fields as subfields.
    The widget will try to iterate the field to get access to the subfields and
    call them to render them.
    If `prefix_label` is set, the subfield's label is printed before the field,
    otherwise afterwards. The latter is useful for iterating radios or
    checkboxes.
    """
    def __init__(self, prefix_label=True):
        self.prefix_label = prefix_label

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = ['<div>']
        for subfield in field:
            if self.prefix_label:
                html.append(
                    '<span>%s %s</span> ' %
                    (subfield.label, subfield(**kwargs))
                )
            else:
                html.append(
                    '<span>%s %s</span> ' %
                    (subfield(**kwargs), subfield.label)
                )
        html.append('</div>')
        return HTMLString(''.join(html))
