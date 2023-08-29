from typing import Annotated


from fastapi import Depends


class CommonQueryParams:
    def __init__(self, page: int = 1, limit: int = 30):
        self._page = page
        self._limit = limit

    @property
    def page(self):
        if self._page < 1:
            self._page = 1
        return self._page

    @page.setter
    def page(self, value: int):
        if value < 1:
            self._page = 1
        else:
            self._page = value

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, value: int):
        self._limit = value

    @property
    def offset(self):
        return (self.page - 1) * self.limit


CommonQuery = Annotated[CommonQueryParams, Depends()]
