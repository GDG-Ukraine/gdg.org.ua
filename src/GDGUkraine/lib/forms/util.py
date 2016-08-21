class InputDict(dict):
    """Workaround to make WTForms work proper with cherrypy/blueberrypy

    WTForms require formdata to be passed in a dict which supports getlist
    method to get list of values by key.
    """
    def getlist(self, arg):
        """This method always returns a list of values associated
        with form field name. The method returns an empty list if
        no such form field or value exists for name. It returns
        a list consisting of one item if only one such value exists.
        """
        try:
            if isinstance(self[arg], list):
                return self[arg]
            return [self[arg]]
        except KeyError:
            return []
