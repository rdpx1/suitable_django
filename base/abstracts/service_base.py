from abc import ABC, abstractmethod
from django.core.cache import cache
from typing import Any, List, Tuple


class ServiceException(Exception):
    """
    Exception class for use inside of services
    """
    def __init__(self, detail, success=False, data=None):
        self._detail = detail
        self._success = success
        self._data = data
        super().__init__(detail)

    def __str__(self):
        return self._detail

    @property
    def detail(self):
        return self._detail

    @property
    def success(self):
        return self._success

    @property
    def data(self):
        return self._data


class ServiceBase(ABC):
    """
    Abstract class that should be used as a base for services
    """

    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Constructor, which should setup the properties to be used in the _perform method
        """
        self._disable_cache = kwargs.get("disable_cache", False)
        self._handle_exceptions = kwargs.get("handle_exceptions", True)

    def perform(self) -> Tuple[bool, str, Any]:
        """
        Method that should be called to execute the service
        """
        try:
            (success, detail, data) = self._perform()
        except ServiceException as e:
            if not self._handle_exceptions:
                raise e

            success = e.success
            detail = e.detail
            data = e.data

        except Exception as e:
            if not self._handle_exceptions:
                raise e

            # sentry_sdk.capture_exception(e)
            success = False
            detail = f"{type(e).__name__}: {str(e)}"
            data = None

        return (success, detail, data)

    @abstractmethod
    def _perform() -> Tuple[bool, str, Any]:
        """
        Main method of the service, where the actions should be performed

        Should return a tuple like this: (bool, str, any)

        The first parameter is the boolean that indicates success or failure

        The second parameter is a string with the success or error message

        The third parameter is the data returned by the service
        """
        pass

    def invalidate_cache(self):
        """
        Method that should be used to invalid all cache keys related to the service
        """
        pass

    def _use_cache(self, cache_key: str, cache_duration: int, data_function) -> Any:
        if self._disable_cache:
            return data_function()

        # attempt to get data from cache
        data = cache.get(cache_key)
        if data is not None:
            return data

        # execute data function and cache it
        data = data_function()
        cache.set(cache_key, data, cache_duration)
        return data

    def _delete_cache(self, cache_key: str):
        """
        Invalidates a given cache key
        """
        cache.delete(cache_key)

    def _delete_cache_many(self, cache_keys: List[str]):
        """
        Invalidates several cache keys
        
        Accepts asterisks as wildcard
        """
        keys_to_delete = []
        for cache_key in cache_keys:
            keys_to_delete.extend(cache.keys(cache_key))

        cache.delete_many(keys_to_delete)
